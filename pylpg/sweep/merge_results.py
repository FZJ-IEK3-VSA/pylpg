"""Merge per-task HDF5 files into final per-template HDF5 files.

Run after **all** array jobs have finished:

    python -m pylpg.sweep.merge_results

Input
-----
config.TASKS_FILE       -- task manifest (= BASE_OUTPUT_DIR / "tasks.json")
config.TASK_OUTPUT_DIR  -- directory of task_<NNNNNN>.h5 files written by
                           run_task.py (= BASE_OUTPUT_DIR / "tasks";
                           honours $LPG_OUTPUT_DIR)

Output
------
config.MERGED_OUTPUT_DIR/<template_name>.h5  -- one file per household template
    (= BASE_OUTPUT_DIR / "multi_runs_output"), with the same hierarchical
    structure as simulation.py:
    /<climate_tag>/<transport_tag>/run_<N>/<data_type>
    /<climate_tag>/<transport_tag>/run_<N>/_metadata

Also writes runs_metadata.csv (same directory) summarising every merged run.

The per-task files are temporary: once every task has been folded into the
merged files they are deleted, so nothing accumulates outside the merged output.
Pass ``--keep-tasks`` to retain them.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from pylpg.sweep.config import (
    MERGED_OUTPUT_DIR,
    TASK_OUTPUT_DIR,
    TASKS_FILE,
)
from pylpg.sweep.simulation import safe_name


# Fields that jointly identify which (template, climate, transport, run) a task
# file holds. run_task.py records them in the file's /metadata; the merge
# cross-checks them against the manifest entry so a stale file left over from a
# previous tasks.json can never be merged into the wrong place. These are exactly
# the manifest keys the merge uses to build the destination file + HDF5 path.
_IDENTITY_FIELDS = ("template_key", "climate_tag", "transport_tag", "run_idx")


def _identity_mismatches(task: dict, file_meta: dict) -> list[str]:
    """Return human-readable descriptions of identity fields that disagree.

    Compares the manifest *task* entry against the *file_meta* recorded in a task
    file's ``/metadata`` group across :data:`_IDENTITY_FIELDS`. Values are
    compared as strings so numpy scalar types read back from HDF5 (e.g.
    ``run_idx`` as ``numpy.int64``) do not cause spurious mismatches. An empty
    list means the file belongs to this task.

    :param dict task: Manifest task dictionary (from ``tasks.json``).
    :param dict file_meta: Single-row ``/metadata`` mapping read from the task file.
    :return list[str]: One ``"field: manifest=... file=..."`` string per mismatch.
    """
    mismatches: list[str] = []
    for field in _IDENTITY_FIELDS:
        expected = task.get(field)
        actual = file_meta.get(field)
        if str(expected) != str(actual):
            mismatches.append(f"{field}: manifest={expected!r} file={actual!r}")
    return mismatches


def merge_all(keep_tasks: bool = False) -> None:
    """Merge all per-task HDF5 files into final per-template HDF5 files.

    Reads the manifest from :data:`pylpg.sweep.config.TASKS_FILE` and iterates
    over every ``task_<NNNNNN>.h5`` in
    :data:`pylpg.sweep.config.TASK_OUTPUT_DIR` (the same location run_task.py
    writes to -- ``BASE_OUTPUT_DIR / "tasks"``, honouring ``$LPG_OUTPUT_DIR``).
    For each task file the simulation DataFrames are copied into
    :data:`pylpg.sweep.config.MERGED_OUTPUT_DIR` ``/<template_name>.h5`` under
    the hierarchical path ``/<climate_tag>/<transport_tag>/run_<N>/<data_type>``.

    Before copying, each file's recorded identity (its ``/metadata``) is
    cross-checked against the manifest entry for its filename-derived task id; a
    file that does not match -- e.g. a stale leftover from a previous
    ``tasks.json`` -- is skipped with a warning instead of being merged into the
    wrong template (see :func:`_identity_mismatches`).

    After merging, a ``runs_metadata.csv`` summary is written next to the merged
    files, any task ids present in ``tasks.json`` but missing from the input
    directory are reported as warnings, and -- unless *keep_tasks* is set -- the
    per-task files that were merged are deleted (they are temporary).

    :param bool keep_tasks: If True, keep the per-task files instead of deleting
        them after a successful merge.
    :return None: No return value.
    :raises SystemExit: If ``tasks.json`` is missing or no task files are found.
    """
    # Same TASKS_FILE generate_tasks.py wrote and run_task.py read, so a merge
    # can never pick up a manifest from a different base than the workers used.
    tasks_file = TASKS_FILE
    if not tasks_file.exists():
        sys.exit(f"tasks.json not found at {tasks_file}")

    tasks: list[dict] = json.loads(tasks_file.read_text())
    tasks_by_id: dict[int, dict] = {t["task_id"]: t for t in tasks}

    # TASK_OUTPUT_DIR and MERGED_OUTPUT_DIR both derive from the single
    # BASE_OUTPUT_DIR knob in config.py (honouring $LPG_OUTPUT_DIR), so this merge
    # can never look in a different directory than the array workers wrote to.
    task_dir = TASK_OUTPUT_DIR
    final_dir = MERGED_OUTPUT_DIR
    final_dir.mkdir(parents=True, exist_ok=True)

    task_files = sorted(task_dir.glob("task_*.h5"))
    if not task_files:
        sys.exit(f"No task_*.h5 files found in {task_dir}")

    print(f"Merging {len(task_files)} task file(s) from {task_dir} ...")

    meta_rows: list[dict] = []
    merged_files: list[Path] = []

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

            # Identity cross-check: a task file is matched to a manifest entry by
            # the id parsed from its filename, and that id is otherwise trusted
            # blindly. A file left over from a *different* tasks.json (e.g. a
            # previous sweep) can share an id with an unrelated current task and
            # would then be merged into the wrong template with the wrong
            # metadata. Guard against that by comparing the file's own recorded
            # identity (written by run_task.py into /metadata) against the
            # manifest; on any mismatch skip and report instead of corrupting the
            # merged output.
            if "/metadata" not in keys:
                print(
                    f"  WARNING: {task_file.name} has no /metadata group; cannot "
                    f"verify it belongs to task {task_id}, skipping"
                )
                continue
            mismatches = _identity_mismatches(
                task, src["/metadata"].iloc[0].to_dict()
            )
            if mismatches:
                print(
                    f"  WARNING: {task_file.name} does not match tasks.json"
                    f"[{task_id}] ({'; '.join(mismatches)}); likely a stale file "
                    f"from a previous manifest, skipping"
                )
                continue

            with pd.HDFStore(hdf5_file, mode="a", complevel=9, complib="blosc") as dst:
                for key in keys:
                    if key.startswith("/data/"):
                        data_type = key[len("/data/"):]
                        dst.put(
                            f"{base_path}/{data_type}",
                            src[key],
                            format="fixed",
                        )
                # Copy metadata into the hierarchical path (its presence is
                # guaranteed by the cross-check above).
                dst.put(f"{base_path}/_metadata", src["/metadata"], format="fixed")
                row = src["/metadata"].iloc[0].to_dict()
                row["hdf5_file"] = hdf5_file.name
                row["hdf5_path"] = base_path
                meta_rows.append(row)

        # This file's data now lives inside the merged file, so it is a temporary
        # that can be deleted once the whole merge has succeeded.
        merged_files.append(task_file)
        print(f"  task {task_id:>6d}  ->  {hdf5_file.name}:{base_path}")

    # Report tasks from tasks.json that were never merged (no matching file).
    found_ids = {int(f.stem.split("_")[1]) for f in merged_files}
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
        print(f"\nMerged {len(meta_rows)} run(s)  ->  {final_dir}")
        print(f"Metadata: {meta_path}")
    else:
        print("\nNo data merged.")

    # Delete the temporary per-task files now that they are safely merged. Only
    # files that were actually merged are removed; anything skipped above (bad
    # name / unknown task id) is left in place for inspection. Reaching this line
    # means the merge loop did not raise, so the merged files are complete on
    # disk before any task file is removed.
    if merged_files and not keep_tasks:
        for f in merged_files:
            f.unlink()
        print(f"Deleted {len(merged_files)} merged task file(s) from {task_dir}.")
        # Drop the tasks dir too if it is now empty (best effort).
        try:
            task_dir.rmdir()
        except OSError:
            pass
    elif merged_files and keep_tasks:
        print(f"Kept {len(merged_files)} task file(s) in {task_dir} (--keep-tasks).")


def main() -> None:
    """Parse CLI arguments and run the merge.

    Reads ``--keep-tasks`` and dispatches to :func:`merge_all`.

    :return None: No return value.
    :raises SystemExit: If ``tasks.json`` is missing or no task files are found.
    """
    parser = argparse.ArgumentParser(
        description="Merge per-task HDF5 files into final per-template HDF5 files."
    )
    parser.add_argument(
        "--keep-tasks",
        action="store_true",
        help="Keep the per-task task_*.h5 files instead of deleting them after a "
        "successful merge (they are treated as temporary and removed by default).",
    )
    args = parser.parse_args()
    merge_all(keep_tasks=args.keep_tasks)


if __name__ == "__main__":
    main()
