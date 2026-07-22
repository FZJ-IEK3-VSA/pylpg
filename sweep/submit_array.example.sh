#!/bin/bash
# SLURM job-array submission script for pylpg parameter sweeps.
#
# This is a TEMPLATE. Copy it to `submit_array.sh` (git-ignored, so your
# cluster-specific paths stay out of the repo) and edit the lines marked [EDIT]:
#
#     cp sweep/submit_array.example.sh sweep/submit_array.sh
#
# Workflow
# --------
# 1. Generate the task manifest (once, on the login node):
#       python sweep/generate_tasks.py
#    This creates tasks.json (one entry per task).
#
# 2. Submit the array, passing the index range explicitly with sbatch --array.
#    Indices are 0-based and index into tasks.json, so N tasks span 0..N-1
#    (get N with: python -c 'import json;print(len(json.load(open("sweep/tasks.json"))))'):
#       sbatch --array=0-10    sweep/submit_array.sh   # all 11 tasks
#       sbatch --array=0-10%50 sweep/submit_array.sh   # ... capped at 50 concurrent
#       sbatch --array=3,7,9   sweep/submit_array.sh   # re-run just these tasks
#
#    Before the FIRST submission, ensure the LPG binary is already in pylpg/
#    (run one task locally, or `python sweep/simulation.py` once). Otherwise
#    the first wave of array tasks all race to download it and corrupt pylpg/.
#
# 3. After all jobs finish, merge per-task outputs into the final HDF5 files:
#       python sweep/merge_results.py
#
# Resource guidance
# -----------------
# Each LPG run is single-threaded (--cpus-per-task=1).
# Memory usage is typically <2 GB per run; 4 GB gives headroom.
# Wall time depends on the simulation year and household complexity; 2 h is
# a safe default for a single year.  Adjust all three to cluster limits.

#SBATCH --job-name=pylpg_array
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=02:00:00

# Log files - one per array element: logs/task_<jobid>_<arrayid>.{out,err}
#SBATCH --output=logs/task_%A_%a.out
#SBATCH --error=logs/task_%A_%a.err

# NOTE: --array is deliberately NOT a #SBATCH directive. The number of tasks
# varies per manifest, so the range is passed on the sbatch command line
# instead (see the examples in the header). Append %K to cap concurrency, e.g.
# --array=0-10%50, tuned to the cluster's fair-use policy.

# ---------------------------------------------------------------------------
# Environment setup - adapt to your cluster's module system.   [EDIT]
# ---------------------------------------------------------------------------
source "$HOME/.bashrc"
mamba activate pyLPG_env

# ---------------------------------------------------------------------------
# Output location   [EDIT - or set the defaults in sweep/config.py instead]
# ---------------------------------------------------------------------------
# All results derive from the single BASE_OUTPUT_DIR knob in sweep/config.py:
# run_task.py writes per-task files to <base>/tasks/ and merge_results.py writes
# the merged per-template files to <base>/multi_runs_output/, then deletes the
# per-task files. To override the config default for this run, uncomment and set:
# export LPG_OUTPUT_DIR="/path/to/output"
# If you export it here, ALSO export the same value in the shell where you run
# merge_results.py, or the merge will look in the config.py default instead.

# Working directory for each task's LPG calc dir (C<task_id>). Point it at fast
# node-local scratch so per-task result I/O does not land on shared storage.
# $TMPDIR is set per job by SLURM on most clusters.
export LPG_WORK_DIR="$TMPDIR"

# Create log directory if it does not yet exist
mkdir -p logs

# ---------------------------------------------------------------------------
# Run the worker for this array element
# ---------------------------------------------------------------------------
echo "Starting task $SLURM_ARRAY_TASK_ID on $(hostname) at $(date)"

python sweep/run_task.py --task-id "$SLURM_ARRAY_TASK_ID"

EXIT_CODE=$?
FINISH_LINE="Task $SLURM_ARRAY_TASK_ID (job $SLURM_ARRAY_JOB_ID) finished with exit code $EXIT_CODE at $(date)"

# This runs on a compute node, so its stdout goes to this task's own
# logs/task_%A_%a.out. ALSO append the finish line to a single shared
# logs/completion.log so you can watch all tasks finish live on the login node:
#     tail -f logs/completion.log
# flock serialises the concurrent array tasks' appends so their lines don't
# interleave; fd 9 is opened in append mode (>>) so the lock never truncates it.
echo "$FINISH_LINE"                                    # per-task .out (self-contained)
( flock 9; echo "$FINISH_LINE" >&9 ) 9>>logs/completion.log

exit $EXIT_CODE
