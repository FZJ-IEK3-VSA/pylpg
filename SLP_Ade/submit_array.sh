#!/bin/bash
# SLURM job-array submission script for pylpg multi-simulations.
#
# Workflow
# --------
# 1. Generate the task manifest (once, on the login node):
#       python SLP_Ade/generate_tasks.py
#    This creates tasks.json and prints the required --array range.
#
# 2. Update the --array directive below to match the printed range, then submit:
#       sbatch SLP_Ade/submit_array.sh
#
# 3. After all jobs finish, merge per-task outputs into the final HDF5 files:
#       python SLP_Ade/merge_results.py
#
# Resource guidance
# -----------------
# Each LPG run is single-threaded (--cpus-per-task=1).
# Memory usage is typically <2 GB per run; 4 GB gives headroom.
# Wall time depends on the simulation year and household complexity; 2 h is
# a safe default for a single year.  Adjust all three to your cluster limits.

#SBATCH --job-name=pylpg_array

# *** UPDATE the upper bound to (number of tasks - 1) from generate_tasks.py ***
# The %50 suffix caps concurrency at 50 simultaneous jobs; tune to cluster policy.
#SBATCH --array=0-9%50

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00

# Log files – one per array element: logs/task_<jobid>_<arrayid>.{out,err}
#SBATCH --output=logs/task_%A_%a.out
#SBATCH --error=logs/task_%A_%a.err

# ---------------------------------------------------------------------------
# Environment setup – adapt to your cluster's module system
# ---------------------------------------------------------------------------

# Example for a module-based cluster:
# module purge
# module load python/3.11

# Activate the project virtual environment (path relative to submission dir):
source pyLPG_env/bin/activate

# cd to the repository root regardless of where sbatch was called from:
# realpath resolves submit_array.sh to an absolute path, dirname strips the
# filename (leaving SLP_Ade/), and /.. steps up one level to the repo root.
cd "$(dirname "$(realpath "$0")")/.."

# Output directory for per-task HDF5 files on the cluster.
# run_task.py and merge_results.py both read this variable; they fall back to
# slurm_output/ inside the repo when it is not set (useful for local testing).
export LPG_OUTPUT_DIR="/fast/central/projects/2026-a-tarasenko-SLP_Ade/first_training_set"

# Create log directory if it does not yet exist
mkdir -p logs

# ---------------------------------------------------------------------------
# Run the worker for this array element
# ---------------------------------------------------------------------------
echo "Starting task $SLURM_ARRAY_TASK_ID on $(hostname) at $(date)"

python SLP_Ade/run_task.py --task-id "$SLURM_ARRAY_TASK_ID"                     # TODO: for schleife für tasks?

EXIT_CODE=$?
echo "Task $SLURM_ARRAY_TASK_ID finished with exit code $EXIT_CODE at $(date)"
exit $EXIT_CODE
