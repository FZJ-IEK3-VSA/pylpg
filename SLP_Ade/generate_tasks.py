"""Generate task manifest for SLURM array job.

Run once on the login node **before** submitting the job array:

    python SLP_Ade/generate_tasks.py

Output
------
tasks.json  -- one entry per independent simulation run, indexed 0 .. N-1.
               The job array should cover indices 0 .. N-1.

Each task stores only string keys (attribute names in lpgdata.*) so the
manifest is fully JSON-serialisable.  The worker resolves them back to LPG
objects at runtime.

Seed strategy
-------------
Seeds are derived deterministically from the combo tag + run index via MD5
so that tasks.json is reproducible and re-runnable with identical parameters.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# Make the repo root importable regardless of CWD
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from pylpg import lpgdata
from pylpg.lpgpythonbindings import JsonReference

# Configuration lives in config.py; execution helpers in simulation.py.
from SLP_Ade.config import (  # noqa: E402
    CLIMATE_SET_KEYS,
    HOUSEHOLD_TEMPLATE_KEYS,
    TRANSPORT_VARIANT_KEYS,
    get_runs_for_combo,
)
from SLP_Ade.simulation import (  # noqa: E402
    collect_lpg_members,
    create_combo_tag,
)


def _deterministic_seed(combo_tag: str, run_idx: int) -> int:
    """Derive a reproducible 31-bit seed from combo_tag and run index.

    Uses MD5 of ``"<combo_tag>_<run_idx>"`` so the same manifest always
    produces the same seeds regardless of when or where it is generated.

    :param str combo_tag: Combined identifier tag for the parameter combination.
    :param int run_idx: Zero-based run index within the combination.
    :return int: A reproducible seed value in the range [0, 2**31).
    """
    raw = f"{combo_tag}_{run_idx}".encode()
    return int(hashlib.md5(raw).hexdigest(), 16) % (2**31)


def build_task_list() -> list[dict]:
    """Build the full list of independent simulation tasks.

    Expands the CONFIG cartesian product (templates × climate sets × transport
    variants × runs-per-combo) into a flat list of task dictionaries. Each
    task stores only string keys so the manifest is JSON-serialisable; the
    worker resolves them back to LPG objects at runtime.

    Seeds are derived deterministically via :func:`_deterministic_seed` so the
    manifest is reproducible.

    :return list[dict]: Ordered list of task dictionaries, one per simulation run.
    """
    # --- resolve template keys -------------------------------------------
    all_template_keys: list[str] = list(
        collect_lpg_members(lpgdata.HouseholdTemplates, str).keys()
    )
    template_keys: list[str] = (
        HOUSEHOLD_TEMPLATE_KEYS
        if HOUSEHOLD_TEMPLATE_KEYS is not None
        else all_template_keys
    )

    # --- resolve climate key triples -------------------------------------
    # Each triple: (geographic_location_key, temperature_profile_key, tag)
    if CLIMATE_SET_KEYS is None:
        all_geo_keys = list(
            collect_lpg_members(lpgdata.GeographicLocations, JsonReference).keys()
        )
        all_temp_keys = list(
            collect_lpg_members(lpgdata.TemperatureProfiles, JsonReference).keys()
        )
        climate_key_triples = [
            (geo_key, temp_key, f"{geo_key}__{temp_key}")
            for geo_key in all_geo_keys
            for temp_key in all_temp_keys
        ]
    else:
        climate_key_triples = CLIMATE_SET_KEYS  # already (geo, temp, tag)

    # --- build task list -------------------------------------------------
    tasks: list[dict] = []
    task_id = 0

    for tmpl_key in template_keys:
        for geo_key, temp_key, climate_tag in climate_key_triples:
            for tvk in TRANSPORT_VARIANT_KEYS:
                combo_tag = create_combo_tag(tmpl_key, climate_tag, tvk.tag)
                num_runs = get_runs_for_combo(combo_tag)

                for run_idx in range(num_runs):
                    seed = _deterministic_seed(combo_tag, run_idx)
                    tasks.append(
                        {
                            "task_id": task_id,
                            "template_key": tmpl_key,
                            "geographic_location_key": geo_key,
                            "temperature_profile_key": temp_key,
                            "climate_tag": climate_tag,
                            "transport_simulate": tvk.simulate_transportation,
                            "transport_charging_set_key": tvk.charging_set_key,
                            "transport_device_set_key": tvk.transport_device_set_key,
                            "transport_travel_route_key": tvk.travel_route_set_key,
                            "transport_tag": tvk.tag,
                            "run_idx": run_idx,
                            "num_runs": num_runs,
                            "seed": seed,
                        }
                    )
                    task_id += 1

    return tasks


def main() -> None:
    """Generate tasks.json and print submission guidance.

    Calls :func:`build_task_list`, writes the result to ``SLP_Ade/tasks.json``,
    and prints the total task count together with the ``--array`` range to use
    when submitting the SLURM job array.

    :return None: No return value.
    """
    tasks = build_task_list()
    out = _REPO_ROOT / "SLP_Ade" / "tasks.json"
    out.write_text(json.dumps(tasks, indent=2))

    # Write the task count to a machine-readable file so submit_array.sh can
    # derive its --array range automatically (no manual, drift-prone edit).
    count_file = _REPO_ROOT / "SLP_Ade" / "task_count.txt"
    count_file.write_text(str(len(tasks)))

    print(f"Generated {len(tasks)} tasks  ->  {out}")
    print(f"Wrote task count        ->  {count_file}")
    print(f"Submit with:  bash SLP_Ade/submit_array.sh   (reads {count_file.name} automatically)")
    print(f"Or manually:  sbatch --array=0-{len(tasks) - 1} SLP_Ade/submit_array.sh")


if __name__ == "__main__":
    main()
