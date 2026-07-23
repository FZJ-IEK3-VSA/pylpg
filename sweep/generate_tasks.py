"""Generate task manifest for SLURM array job.

Run once on the login node **before** submitting the job array:

    python sweep/generate_tasks.py

Output
------
tasks.json  -- one entry per independent simulation run, indexed 0 .. N-1.
               The job array should cover indices 0 .. N-1.

Each task stores only string keys so the manifest is fully JSON-serialisable:
household templates by their lpgdata attribute name, and the JsonReference
catalogs (locations, temperature profiles, transport sets) by their ``.Name``
reference string.  The worker resolves them back to LPG objects at runtime.

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

# Make the repo root importable so `from sweep.config import ...` works when this
# module is run directly as a script (python sweep/generate_tasks.py), matching
# run_task.py and merge_results.py.
_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

from pylpg import lpgdata

# Configuration lives in config.py; execution helpers in simulation.py.
from sweep.config import (
    CLIMATE_SET_KEYS,
    HOUSEHOLD_TEMPLATE_KEYS,
    TRANSPORT_VARIANT_KEYS,
    ClimateSetKey,
    get_runs_for_combo,
)
from sweep.simulation import (
    collect_lpg_members,
    collect_lpg_references_by_name,
    create_combo_tag,
)


def _deterministic_seed(combo_tag: str, run_idx: int) -> int:                           # TODO:  simplify seed generation
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

    # --- resolve climate keys --------------------------------------------
    # Each entry is a ClimateSetKey(geographic_location_key,
    # temperature_profile_key, tag).
    if CLIMATE_SET_KEYS is None:
        all_geo_keys = list(
            collect_lpg_references_by_name(lpgdata.GeographicLocations).keys()
        )
        all_temp_keys = list(
            collect_lpg_references_by_name(lpgdata.TemperatureProfiles).keys()
        )
        climate_keys = [
            ClimateSetKey(geo_key, temp_key, f"{geo_key}__{temp_key}")
            for geo_key in all_geo_keys
            for temp_key in all_temp_keys
        ]
    else:
        climate_keys = CLIMATE_SET_KEYS

    # --- build task list -------------------------------------------------
    tasks: list[dict] = []
    task_id = 0

    for tmpl_key in template_keys:
        for climate_key in climate_keys:
            for tvk in TRANSPORT_VARIANT_KEYS:
                combo_tag = create_combo_tag(tmpl_key, climate_key.tag, tvk.tag)
                num_runs = get_runs_for_combo(combo_tag)

                for run_idx in range(num_runs):
                    seed = _deterministic_seed(combo_tag, run_idx)
                    tasks.append(
                        {
                            "task_id": task_id,
                            "template_key": tmpl_key,
                            "geographic_location_key": climate_key.geographic_location_key,
                            "temperature_profile_key": climate_key.temperature_profile_key,
                            "climate_tag": climate_key.tag,
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

    Calls :func:`build_task_list`, writes the result to ``sweep/tasks.json``,
    and prints the total task count together with the ``--array`` range to use
    when submitting the SLURM job array.

    :return None: No return value.
    """
    tasks = build_task_list()
    # Write to the same repo-root-absolute path run_task.py / merge_results.py
    # read from, so the manifest lands in the right place regardless of CWD.
    out = _REPO_ROOT / "sweep" / "tasks.json"
    out.write_text(json.dumps(tasks, indent=2))

    # The --array range is passed explicitly on the sbatch command line (the
    # submit script is a plain array-element worker), so print the exact range.
    last = len(tasks) - 1
    print(f"Generated {len(tasks)} tasks  ->  {out}")
    print(f"Submit with:  sbatch --array=0-{last} sweep/submit_array.sh")
    print(f"Cap concurrency by appending %K, e.g.  sbatch --array=0-{last}%50 sweep/submit_array.sh")


if __name__ == "__main__":
    main()
