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
config.TASK_OUTPUT_DIR/task_<NNNNNN>.h5  -- per-task HDF5 file with:
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

from SLP_Ade.config import TASK_OUTPUT_DIR  # noqa: E402
from SLP_Ade.simulation import (  # noqa: E402
    TransportVariant,
    attach_flexibility_events,
    run_lpg_simulation,
    safe_name,
    split_dataframe_by_type,
)


class NoResultsError(RuntimeError):
    """Raised when a simulation task produces no usable result data.

    Signals one of two no-data outcomes — the engine wrote no results
    directory at all, or the directory held no profiles (a silent exit-0
    empty run) — so that the caller can fail the task instead of writing a
    metadata-only file that looks complete.
    """


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

    The output directory is :data:`SLP_Ade.config.TASK_OUTPUT_DIR` — the single
    source of truth that :mod:`SLP_Ade.merge_results` reads from too, so writer
    and reader can never diverge. Override it for a one-off run by exporting
    ``$LPG_OUTPUT_DIR`` (config resolves that consistently for both scripts).

    :param dict task: Task dictionary as produced by :func:`~SLP_Ade.generate_tasks.build_task_list`.
    :return None: No return value.
    :raises NoResultsError: If the simulation returns no results (``None``) or an
        empty result frame (a silent exit-0 run with no profiles).
    """
    task_id: int = task["task_id"]

    # --- resolve string keys to LPG objects ------------------------------
    tmpl = getattr(lpgdata.HouseholdTemplates, task["template_key"])            #TODO: replace with JsonReference to avoid get_attr_key() and make it more robust
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

    # Two distinct no-data outcomes both mean "don't write a useless file":
    #   df is None  -> the engine wrote no results/Results directory at all.
    #   df.empty    -> the directory existed but held no Sum.*.json profiles
    #                  (a silent, exit-0 empty run — seen occasionally on
    #                  transport tasks). Guarding df.empty keeps these from
    #                  being saved as metadata-only files that look complete.
    if df is None or df.empty:
        reason = "No results returned" if df is None else "Empty result frame"
        raise NoResultsError(f"[task {task_id}] {reason}")

    # --- save per-task HDF5 (no concurrent write risk) -------------------
    # config.TASK_OUTPUT_DIR (= BASE_OUTPUT_DIR / "tasks") is the single source of
    # truth for where task files go; merge_results.py reads the same value and
    # deletes these files once they are merged. It honours $LPG_OUTPUT_DIR when
    # set, else falls back to the committed default in config.py.
    output_dir = TASK_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"task_{task_id:06d}.h5"

    # Regroup the flat <LoadType>_<HHKey> columns into one frame per load type
    # so each is saved as its own HDF5 group (keeps data types separable on read).
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

    print(f"[task {task_id}] Saved  ->  {out_path}")


def main() -> None:
    """Parse CLI arguments and dispatch to :func:`run_task`.

    Reads ``--task-id`` (falls back to ``$SLURM_ARRAY_TASK_ID``, then 0),
    loads ``SLP_Ade/tasks.json``, and calls :func:`run_task` for the selected
    entry.

    :return None: No return value.
    :raises FileNotFoundError: If ``tasks.json`` is missing.
    :raises IndexError: If the task id is out of range for ``tasks.json``.
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
        raise FileNotFoundError(
            f"tasks.json not found at {tasks_file}. Run generate_tasks.py first."
        )

    tasks: list[dict] = json.loads(tasks_file.read_text())

    if args.task_id >= len(tasks):
        raise IndexError(
            f"task-id {args.task_id} is out of range (tasks.json has {len(tasks)} entries)"
        )

    run_task(tasks[args.task_id])


if __name__ == "__main__":
    # The process boundary is the one place a non-zero exit belongs. Translate
    # the anticipated failure conditions into a clean one-line stderr message +
    # exit 1 (which SLURM records as a failed array task). Anything else — an
    # unexpected bug — is left to propagate as a full traceback, which is more
    # useful than a terse message in cluster logs.
    try:
        main()
    except (NoResultsError, FileNotFoundError, IndexError) as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
