"""Merge per-task HDF5 files into final per-template HDF5 files.

Run after **all** array jobs have finished:

    python SLP_Ade/merge_results.py

Input
-----
tasks.json           -- task manifest (repo root)
slurm_output/        -- directory of task_<NNNNNN>.h5 files written by run_task.py

Output
------
multi_runs_output/<template_name>.h5  -- one file per household template,
    with the same hierarchical structure as simulation.py:
    /<climate_tag>/<transport_tag>/run_<N>/<data_type>
    /<climate_tag>/<transport_tag>/run_<N>/_metadata

Also writes multi_runs_output/runs_metadata.csv summarising every merged run.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd

from SLP_Ade.simulation import safe_name  # noqa: E402


def main() -> None:
    """Merge all per-task HDF5 files into final per-template HDF5 files.

    Reads ``tasks.json`` and iterates over every ``task_<NNNNNN>.h5`` in
    ``$LPG_OUTPUT_DIR`` (default: ``slurm_output/``).  For each task file the
    simulation DataFrames are copied into
    ``multi_runs_output/<template_name>.h5`` under the hierarchical path
    ``/<climate_tag>/<transport_tag>/run_<N>/<data_type>``.

    After merging, a ``runs_metadata.csv`` summary is written to
    ``multi_runs_output/`` and any task ids present in ``tasks.json`` but
    missing from the output directory are reported as warnings.

    :return None: No return value.
    :raises SystemExit: If ``tasks.json`` is missing or no task files are found.
    """
    tasks_file = _REPO_ROOT / "tasks.json"
    if not tasks_file.exists():
        sys.exit(f"tasks.json not found at {tasks_file}")

    tasks: list[dict] = json.loads(tasks_file.read_text())
    tasks_by_id: dict[int, dict] = {t["task_id"]: t for t in tasks}

    # LPG_OUTPUT_DIR mirrors the setting in submit_array.sh / run_task.py.
    slurm_dir = Path(os.environ.get("LPG_OUTPUT_DIR", str(_REPO_ROOT / "slurm_output")))
    final_dir = _REPO_ROOT / "multi_runs_output"
    final_dir.mkdir(exist_ok=True)

    task_files = sorted(slurm_dir.glob("task_*.h5"))
    if not task_files:
        sys.exit(f"No task_*.h5 files found in {slurm_dir}")

    print(f"Merging {len(task_files)} task file(s) ...")

    meta_rows: list[dict] = []
    missing: list[int] = []

    for task_file in task_files:
        # Parse task id from filename, e.g. task_000042.h5 -> 42
        try:
            task_id = int(task_file.stem.split("_")[1])
        except (IndexError, ValueError):
            print(f"  WARNING: cannot parse task id from {task_file.name}, skipping")
            continue

        if task_id not in tasks_by_id:
            print(f"  WARNING: task id {task_id} not found in tasks.json, skipping")
            continue

        task = tasks_by_id[task_id]
        tmpl_key = task["template_key"]
        climate_tag = task["climate_tag"]
        transport_tag = task["transport_tag"]
        run_idx = task["run_idx"]

        hdf5_file = final_dir / f"{safe_name(tmpl_key)}.h5"
        base_path = (
            f"{safe_name(climate_tag)}/{transport_tag}/run_{run_idx + 1}"
        )

        with pd.HDFStore(task_file, mode="r") as src:
            keys = src.keys()
            with pd.HDFStore(hdf5_file, mode="a", complevel=9, complib="blosc") as dst:
                for key in keys:
                    if key.startswith("/data/"):
                        data_type = key[len("/data/"):]
                        dst.put(
                            f"{base_path}/{data_type}",
                            src[key],
                            format="fixed",
                        )
                # Copy metadata into the hierarchical path
                if "/metadata" in keys:
                    dst.put(f"{base_path}/_metadata", src["/metadata"], format="fixed")
                    row = src["/metadata"].iloc[0].to_dict()
                    row["hdf5_file"] = hdf5_file.name
                    row["hdf5_path"] = base_path
                    meta_rows.append(row)

        print(f"  task {task_id:>6d}  ->  {hdf5_file.name}:{base_path}")

    # Report tasks from tasks.json that have no matching output file
    found_ids = {int(f.stem.split("_")[1]) for f in task_files}
    missing = [t["task_id"] for t in tasks if t["task_id"] not in found_ids]
    if missing:
        print(f"\nWARNING: {len(missing)} task(s) have no output file:")
        for tid in missing[:10]:
            t = tasks_by_id[tid]
            print(
                f"  task {tid}: {t['template_key']}  {t['climate_tag']}  "
                f"{t['transport_tag']}  run {t['run_idx']}"
            )
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    # Write metadata summary
    if meta_rows:
        meta_df = pd.DataFrame(meta_rows)
        meta_path = final_dir / "runs_metadata.csv"
        meta_df.to_csv(meta_path, index=False)
        print(f"\nMerged {len(meta_rows)} run(s).")
        print(f"Metadata: {meta_path}")
    else:
        print("\nNo data merged.")


if __name__ == "__main__":
    main()
