"""SLURM array worker: execute one LPG simulation task.

Usage (called automatically by the batch script):
    python SLP_Ade/run_task.py --task-id $SLURM_ARRAY_TASK_ID

Or for local testing of a single task:
    python SLP_Ade/run_task.py --task-id 0

Input
-----
SLP_Ade/tasks.json  -- task manifest created by generate_tasks.py.

Output
------
slurm_output/task_<NNNNNN>.h5  -- per-task HDF5 file with:
    /data/<data_type>   -- simulation result DataFrames (per-load-type profiles;
                           with flexibility enabled also the `<LoadType>_NoFlex`
                           baseline profiles and a `FlexibilityEvents` event log)
    /metadata           -- single-row DataFrame with run metadata

Writing one file per task avoids concurrent HDF5 write conflicts entirely.
Run merge_results.py after all array jobs finish to assemble the final
per-template HDF5 files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from pylpg import lpgdata

from SLP_Ade.simulation import (  # noqa: E402
    TransportVariant,
    attach_flexibility_events,
    run_lpg_simulation,
    safe_name,
    split_dataframe_by_type,
)


def _resolve_optional(container: object, key: str | None) -> object | None:
    """Return ``getattr(container, key)`` or ``None`` when *key* is ``None``.

    :param object container: The object to look up the attribute on.
    :param str | None key: Attribute name to retrieve, or ``None``.
    :return object | None: The resolved attribute value, or ``None`` if key is ``None``.
    """
    return getattr(container, key) if key is not None else None


def run_task(task: dict) -> None:
    """Execute one simulation task and write the result to a per-task HDF5 file.

    Resolves all string keys in *task* back to LPG objects, calls
    :func:`~SLP_Ade.simulation.run_lpg_simulation`, and writes one
    ``task_<NNNNNN>.h5`` file containing:

    - ``/data/<data_type>`` — simulation result DataFrames (one per load type)
    - ``/metadata`` — single-row DataFrame with run metadata

    The output directory defaults to ``slurm_output/`` in the repo root and
    can be overridden via the ``$LPG_OUTPUT_DIR`` environment variable.

    :param dict task: Task dictionary as produced by :func:`~SLP_Ade.generate_tasks.build_task_list`.
    :return None: No return value.
    :raises SystemExit: If the simulation returns no results.
    """
    task_id: int = task["task_id"]

    # --- resolve string keys to LPG objects ------------------------------
    tmpl = getattr(lpgdata.HouseholdTemplates, task["template_key"])
    geographic_location = getattr(
        lpgdata.GeographicLocations, task["geographic_location_key"]
    )
    temperature_profile = _resolve_optional(
        lpgdata.TemperatureProfiles, task["temperature_profile_key"]
    )

    transport_variant = TransportVariant(
        simulate_transportation=task["transport_simulate"],
        charging_set=_resolve_optional(
            lpgdata.ChargingStationSets, task["transport_charging_set_key"]
        ),
        transport_device_set=_resolve_optional(
            lpgdata.TransportationDeviceSets, task["transport_device_set_key"]
        ),
        travel_route_set=_resolve_optional(
            lpgdata.TravelRouteSets, task["transport_travel_route_key"]
        ),
        tag=task["transport_tag"],
    )

    # --- execute simulation ----------------------------------------------
    print(
        f"[task {task_id}] {task['template_key']}  "
        f"climate={task['climate_tag']}  "
        f"transport={task['transport_tag']}  "
        f"run={task['run_idx'] + 1}/{task['num_runs']}  "
        f"seed={task['seed']}"
    )

    # Use task_id as the (unique) calculation index so concurrent array tasks
    # never share a C<idx> working directory. clear_previous_calc=True ensures a
    # clean dir if this task id is requeued. The dir base is LPG_WORK_DIR (set to
    # node-local scratch by submit_array.sh).
    df = run_lpg_simulation(
        tmpl,
        transport_variant,
        geographic_location,
        temperature_profile,
        task["seed"],
        calculation_index=task_id,
        clear_previous_calc=True,
    )

    if df is None:
        print(f"[task {task_id}] No results returned — exiting with error.")
        sys.exit(1)

    # --- save per-task HDF5 (no concurrent write risk) -------------------
    # LPG_OUTPUT_DIR can be set in the environment (e.g. by submit_array.sh on
    # the cluster).  Falls back to slurm_output/ inside the repo for local runs.
    _env_output = os.environ.get("LPG_OUTPUT_DIR")
    output_dir = Path(_env_output) if _env_output else _REPO_ROOT / "slurm_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"task_{task_id:06d}.h5"

    data_types = split_dataframe_by_type(df)
    # Store the flexibility event log (if any) as its own group.
    attach_flexibility_events(data_types, df)

    with pd.HDFStore(out_path, mode="w", complevel=9, complib="blosc") as store:
        for data_type, type_df in data_types.items():
            store.put(f"data/{safe_name(data_type)}", type_df, format="fixed")

        meta_df = pd.DataFrame(
            [
                {
                    "task_id": task_id,
                    "template_key": task["template_key"],
                    "climate_tag": task["climate_tag"],
                    "transport_tag": task["transport_tag"],
                    "run_idx": task["run_idx"],
                    "seed": task["seed"],
                    "geographic_location": geographic_location.Name,
                    "temperature_profile": (
                        temperature_profile.Name
                        if temperature_profile is not None
                        else None
                    ),
                }
            ]
        )
        store.put("metadata", meta_df, format="fixed")

    print(f"[task {task_id}] Saved  ->  {out_path.relative_to(_REPO_ROOT)}")


def main() -> None:
    """Parse CLI arguments and dispatch to :func:`run_task`.

    Reads ``--task-id`` (falls back to ``$SLURM_ARRAY_TASK_ID``, then 0),
    loads ``SLP_Ade/tasks.json``, and calls :func:`run_task` for the selected
    entry.

    :return None: No return value.
    :raises SystemExit: If ``tasks.json`` is missing or the task id is out of range.
    """
    parser = argparse.ArgumentParser(description="Run one LPG task from tasks.json")
    parser.add_argument(
        "--task-id",
        type=int,
        # Fall back to $SLURM_ARRAY_TASK_ID so the script works unmodified
        # both when called with an explicit flag and from the batch script.
        default=int(os.environ.get("SLURM_ARRAY_TASK_ID", 0)),
        help="Zero-based index into tasks.json (default: $SLURM_ARRAY_TASK_ID)",
    )
    args = parser.parse_args()

    tasks_file = _REPO_ROOT / "SLP_Ade" / "tasks.json"
    if not tasks_file.exists():
        sys.exit(f"tasks.json not found at {tasks_file}. Run generate_tasks.py first.")

    tasks: list[dict] = json.loads(tasks_file.read_text())

    if args.task_id >= len(tasks):
        sys.exit(
            f"task-id {args.task_id} is out of range (tasks.json has {len(tasks)} entries)"
        )

    run_task(tasks[args.task_id])


if __name__ == "__main__":
    main()
