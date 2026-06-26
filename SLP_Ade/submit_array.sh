#!/bin/bash
# SLURM job-array submission script for pylpg multi-simulations.
#
# Workflow
# --------
# 1. Generate the task manifest (once, on the login node):
#       python SLP_Ade/generate_tasks.py
#    This creates tasks.json AND task_count.txt (the number of tasks).
#
# 2. Submit the array — the range is read automatically from task_count.txt:
#       bash SLP_Ade/submit_array.sh
#    Launch it with `bash` on the login node (not `sbatch`). The script reads
#    the count and re-submits itself as an array job with the correct range.
#    (`sbatch SLP_Ade/submit_array.sh` also works, but then the one-line
#     bootstrap runs inside a compute-node allocation instead of on the login
#     node.)
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
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00

# Log files – one per array element: logs/task_<jobid>_<arrayid>.{out,err}
#SBATCH --output=logs/task_%A_%a.out
#SBATCH --error=logs/task_%A_%a.err

# NOTE: --array is deliberately NOT a #SBATCH directive. SLURM parses those
# directives before the script body runs, so it cannot read the task count from
# a file. Instead the bootstrap block below reads task_count.txt and re-submits
# this script with the correct --array range. Cap on concurrent array tasks
# (tune to your cluster's fair-use policy):
MAX_CONCURRENT=50

# ---------------------------------------------------------------------------
# Bootstrap: when launched outside of an array (no $SLURM_ARRAY_TASK_ID),
# read the task count and re-submit ourselves with the right --array range.
# ---------------------------------------------------------------------------
if [ -z "${SLURM_ARRAY_TASK_ID:-}" ]; then
    # cd to the repo root using this script's real location:
    # realpath -> absolute path, dirname -> SLP_Ade/, /.. -> repo root.
    cd "$(dirname "$(realpath "$0")")/.." || exit 1

    COUNT_FILE="SLP_Ade/task_count.txt"
    if [ ! -f "$COUNT_FILE" ]; then
        echo "ERROR: $COUNT_FILE not found. Run 'python SLP_Ade/generate_tasks.py' first." >&2
        exit 1
    fi

    COUNT="$(cat "$COUNT_FILE")"
    case "$COUNT" in
        ''|*[!0-9]*)
            echo "ERROR: invalid task count '$COUNT' in $COUNT_FILE" >&2
            exit 1
            ;;
    esac
    if [ "$COUNT" -lt 1 ]; then
        echo "ERROR: task count must be >= 1 (got $COUNT)" >&2
        exit 1
    fi

    echo "Submitting array 0-$((COUNT - 1))%${MAX_CONCURRENT} (${COUNT} tasks)"
    exec sbatch --array="0-$((COUNT - 1))%${MAX_CONCURRENT}" SLP_Ade/submit_array.sh
fi

# ---------------------------------------------------------------------------
# Array element: this runs once per task with $SLURM_ARRAY_TASK_ID set.
# ---------------------------------------------------------------------------

# Work from the directory the array was submitted from (the repo root, since the
# bootstrap above submits from there); fall back to resolving via this script.
cd "${SLURM_SUBMIT_DIR:-$(dirname "$(realpath "$0")")/..}" || exit 1

# ---------------------------------------------------------------------------
# Environment setup – adapt to your cluster's module system
# ---------------------------------------------------------------------------

# Example for a module-based cluster:
# module purge
# module load python/3.11

# Activate the project virtual environment (path relative to repo root):
source pyLPG_env/bin/activate

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

python SLP_Ade/run_task.py --task-id "$SLURM_ARRAY_TASK_ID"

EXIT_CODE=$?
echo "Task $SLURM_ARRAY_TASK_ID finished with exit code $EXIT_CODE at $(date)"
exit $EXIT_CODE
