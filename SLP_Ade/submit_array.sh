#!/bin/bash
# SLURM job-array submission script for pylpg multi-simulations.
#
# Workflow
# --------
# 1. Generate the task manifest (once, on the login node):
#       python SLP_Ade/generate_tasks.py
#    This creates tasks.json (one entry per task).
#
# 2. Submit the array, passing the index range explicitly with sbatch --array.
#    Indices are 0-based and index into tasks.json, so N tasks span 0..N-1
#    (get N with: python -c 'import json;print(len(json.load(open("SLP_Ade/tasks.json"))))'):
#       sbatch --array=0-10    SLP_Ade/submit_array.sh   # all 11 tasks
#       sbatch --array=0-10%50 SLP_Ade/submit_array.sh   # ... capped at 50 concurrent
#       sbatch --array=3,7,9   SLP_Ade/submit_array.sh   # re-run just these tasks
#
#    Before the FIRST submission, ensure the LPG binary is already in pylpg/
#    (run one task locally, or `python SLP_Ade/simulation.py` once). Otherwise
#    the first wave of array tasks all race to download it and corrupt pylpg/.
#
# 3. After all jobs finish, merge per-task outputs into the final HDF5 files:
#       python SLP_Ade/merge_results.py
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
    
# Log files – one per array element: logs/task_<jobid>_<arrayid>.{out,err}
#SBATCH --output=logs/task_%A_%a.out
#SBATCH --error=logs/task_%A_%a.err

# NOTE: --array is deliberately NOT a #SBATCH directive. The number of tasks
# varies per manifest, so the range is passed on the sbatch command line
# instead (see the examples in the header). Append %K to cap concurrency, e.g.
# --array=0-10%50, tuned to the cluster's fair-use policy.

# ---------------------------------------------------------------------------
# Array element: this runs once per task with $SLURM_ARRAY_TASK_ID set.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Environment setup – adapt to your cluster's module system
# ---------------------------------------------------------------------------

# Activate the project virtual environment (path relative to repo root):
source $HOME/.bashrc
mamba activate pyLPG_env

# Output location for all results: the single source of truth is BASE_OUTPUT_DIR
# in SLP_Ade/config.py. run_task.py writes per-task files to <base>/tasks/ and
# merge_results.py writes the merged per-template files to <base>/multi_runs_output/
# and then deletes the per-task files -- both paths derive from that one knob, so
# nothing lands in the repo. Do NOT set LPG_OUTPUT_DIR only here: an `export` in
# this batch script is invisible to an interactive `merge_results.py` on the
# login node, which would make the merge look in the wrong directory. To override
# for a run, uncomment the line below AND run merge_results.py in a shell with the
# same value exported (or just change the default in config.py):
# export LPG_OUTPUT_DIR="/fast/central/projects/2026-a-tarasenko-SLP_Ade/first_training_set"

# Working directory for per-task LPG calc dirs (C<task_id>). Point it at fast
# node-local scratch so the ~155 MB binary+DB copy each task makes does NOT land
# on shared storage. $TMPDIR is set per job by SLURM on most clusters; the LPG
# binary itself is still read from / downloaded into pylpg/ (done in pre-flight).
export LPG_WORK_DIR="/fast/central/projects/2026-a-tarasenko-SLP_Ade/first_training_set/lpg_results"

# Create log directory if it does not yet exist
mkdir -p logs

# ---------------------------------------------------------------------------
# Run the worker for this array element
# ---------------------------------------------------------------------------
echo "Starting task $SLURM_ARRAY_TASK_ID on $(hostname) at $(date)"

python SLP_Ade/run_task.py --task-id "$SLURM_ARRAY_TASK_ID"

EXIT_CODE=$?
FINISH_LINE="Task $SLURM_ARRAY_TASK_ID (job $SLURM_ARRAY_JOB_ID) finished with exit code $EXIT_CODE at $(date)"

# This runs on a compute node, so its stdout goes to this task's own
# logs/task_%A_%a.out -- it can never reach the login-node terminal, and one
# file per task means watching progress is chasing N files. So ALSO append the
# finish line to a single shared logs/completion.log. logs/ is on shared storage
# (same place you run generate_tasks.py / merge_results.py), so that file is
# visible on the login node -- watch all tasks finish live with:
#     tail -f logs/completion.log
# flock serialises the concurrent array tasks' appends so their lines don't
# interleave; fd 9 is opened in append mode (>>) on the log itself, so the lock
# never truncates it.
echo "$FINISH_LINE"                                    # per-task .out (self-contained)
( flock 9; echo "$FINISH_LINE" >&9 ) 9>>logs/completion.log

exit $EXIT_CODE
