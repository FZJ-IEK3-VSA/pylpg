"""Generate task manifest for SLURM array job.

Run once on the login node **before** submitting the job array:

    python -m pylpg.sweep.generate_tasks

Output
------
config.TASKS_FILE  -- one entry per independent simulation run, indexed 0 .. N-1
                      (= BASE_OUTPUT_DIR / "tasks.json"; honours
                      $LPG_OUTPUT_DIR). The job array should cover indices
                      0 .. N-1.

Each task stores only string keys so the manifest is fully JSON-serialisable:
household templates by their lpgdata attribute name, and the JsonReference
catalogs (locations, temperature profiles, transport sets) by their ``.Name``
reference string.  The worker resolves them back to LPG objects at runtime.

Seed strategy
-------------
Each task gets a fresh random 31-bit seed, drawn once when the manifest is
generated and then frozen in tasks.json. Re-running a task (or the whole
array) therefore reproduces exactly the same simulation, since the worker
reads the seed from the manifest; only regenerating tasks.json draws new ones.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

# Make the repo root importable so `from pylpg.sweep.config import ...` works when
# this module is run directly as a script (python pylpg/sweep/generate_tasks.py),
# matching run_task.py and merge_results.py.
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from pylpg import lpgdata

# Configuration lives in config.py; execution helpers in simulation.py.
from pylpg.sweep.config import (
    CLIMATE_SET_KEYS,
    HOUSEHOLD_TEMPLATE_KEYS,
    TASKS_FILE,
    TRANSPORT_VARIANT_KEYS,
    get_runs_for_combo,
)
from pylpg.sweep.keys import ClimateSetKey
from pylpg.sweep.simulation import (
    collect_lpg_members,
    collect_lpg_references_by_name,
    create_combo_tag,
)


def build_task_list() -> list[dict]:
    """Build the full list of independent simulation tasks.

    Expands the CONFIG cartesian product (templates × climate sets × transport
    variants × runs-per-combo) into a flat list of task dictionaries. Each
    task stores only string keys so the manifest is JSON-serialisable; the
    worker resolves them back to LPG objects at runtime.

    Every task gets its own random 31-bit seed, frozen into the manifest so
    each run is independent and any task can be replayed from tasks.json.

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
                    # 31 bits so the seed fits the engine's 32-bit signed
                    # RandomSeed field.
                    seed = random.randrange(2**31)
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
    """Generate the task manifest and print submission guidance.

    Calls :func:`build_task_list`, writes the result to
    :data:`~pylpg.sweep.config.TASKS_FILE`, and prints the total task count
    together with the ``--array`` range to use when submitting the SLURM job
    array.

    :return None: No return value.
    """
    tasks = build_task_list()
    # Write to the same absolute path run_task.py / merge_results.py read from
    # (both import TASKS_FILE), so the manifest lands in the right place
    # regardless of CWD and generator and readers can never diverge.
    out = TASKS_FILE
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tasks, indent=2))

    # The --array range is passed explicitly on the sbatch command line (the
    # submit script is a plain array-element worker), so print the exact range.
    last = len(tasks) - 1
    print(f"Generated {len(tasks)} tasks  ->  {out}")
    print(f"Submit with:  sbatch --array=0-{last} submit_array.sh")
    print(f"Cap concurrency by appending %K, e.g.  sbatch --array=0-{last}%50 submit_array.sh")


if __name__ == "__main__":
    main()
