# SLP_Ade — Parallelised LPG Simulations on SLURM

This folder contains everything needed to run large-scale LPG household simulations in parallel on a SLURM cluster.  
All configuration lives in `config.py` and the simulation logic in `simulation.py`; the three SLURM scripts are thin wrappers around them.

---

## Folder contents

| File | Purpose |
|---|---|
| `config.py` | All tunable sweep parameters (the `# ---- CONFIG ----` block) |
| `simulation.py` | Helper functions, the shared `run_lpg_simulation()` primitive, and the sequential runner (also works standalone) |
| `generate_tasks.py` | Enumerates all parameter combinations, writes `tasks.json` |
| `run_task.py` | SLURM array worker — executes one task from `tasks.json` |
| `merge_results.py` | Assembles per-task HDF5 files into final per-template HDF5 files |
| `submit_array.sh` | SLURM batch script |

---

## Configuration

All parameters are set in `config.py` under `# ---- CONFIG ----`:

| Variable | Description | Default |
|---|---|---|
| `YEAR` | Simulation year | `2022` |
| `HOUSEHOLD_TEMPLATE_KEYS` | List of template names, or `None` for all | `None` (all) |
| `CLIMATE_SET_KEYS` | List of `(geo_location_key, temp_profile_key, tag)` tuples, or `None` for all combinations | 3 German cities |
| `TRANSPORT_VARIANT_KEYS` | List of `TransportVariantKey` presets | no-transport + home-charging |
| `RUNS_PER_COMBO_MAP` | Dict mapping combo-tag patterns to run counts | `{"no_transport": 1, "home_charge_bus_cars_30km": 3}` |
| `HOUSETYPE` | LPG house type | `HT20_Single_Family_House_no_heating_cooling` |
| `LPG_BINARY_PATH` | Custom LPG binary, or `None` for auto-download | `None` |
| `SAVE_CSV` / `SAVE_HDF5` | Output format switches | `False` / `True` |

---

## Workflow

### 1. Configure

Edit `config.py` to set your templates, climate presets, transport variants, and run counts.

### 2. Generate the task manifest

Run once on the **login node**:

```bash
python SLP_Ade/generate_tasks.py
```

This writes `tasks.json` **and** `task_count.txt` into `SLP_Ade/`, e.g.:

```
Generated 42 tasks  ->  /path/to/pylpg/SLP_Ade/tasks.json
Wrote task count        ->  /path/to/pylpg/SLP_Ade/task_count.txt
Submit with:  bash SLP_Ade/submit_array.sh   (reads task_count.txt automatically)
Or manually:  sbatch --array=0-41 SLP_Ade/submit_array.sh
```

### 3. Submit the job array

No manual range editing needed — just run:

```bash
bash SLP_Ade/submit_array.sh
```

The script reads `task_count.txt`, then re-submits itself as a SLURM array job covering `0 .. count-1` (capped at `MAX_CONCURRENT` concurrent tasks, default 50). Launch it with `bash` on the login node; `sbatch SLP_Ade/submit_array.sh` also works but runs the one-line bootstrap inside a compute-node allocation. The bootstrap also **pre-fetches the LPG binary once** on the login node, so the first wave of concurrent tasks doesn't race to download it.

Each array element runs one independent simulation and writes its result to `slurm_output/task_NNNNNN.h5`.  
One file per task means there are **no concurrent write conflicts**.

Each task also runs its LPG calculation in its own working directory `C<task_id>` (a ~155 MB binary+DB copy), isolating concurrent runs. To keep that off shared storage, `submit_array.sh` sets `LPG_WORK_DIR` to node-local scratch (`$TMPDIR`); `run_task.py` passes `calculation_index=task_id` so no two tasks share a directory.

### 4. Merge results

After all jobs finish:

```bash
python SLP_Ade/merge_results.py
```

Output:
- `multi_runs_output/<template_name>.h5` — one file per household template, with hierarchy:  
  `/<climate_tag>/<transport_tag>/run_<N>/<data_type>`
- `multi_runs_output/runs_metadata.csv` — summary of every merged run

---

## Running locally (no SLURM)

**Sequential** (original multi-run mode):

```bash
python SLP_Ade/simulation.py
```

**Single task** (for testing one array element):

```bash
python SLP_Ade/run_task.py --task-id 0
```

---

## How the scripts relate

```
config.py               CONFIG (all sweep parameters)
│
simulation.py           helper functions, run_lpg_simulation()
│  (imports config.py)
│
├── generate_tasks.py   reads CONFIG → writes tasks.json
│
├── run_task.py         reads tasks.json[N] → calls run_lpg_simulation()
│                                           → writes slurm_output/task_N.h5
│
└── merge_results.py    reads slurm_output/*.h5 + tasks.json
                        → writes multi_runs_output/<template>.h5
```

`run_lpg_simulation()` defined in `simulation.py` is the single shared execution primitive — both the sequential `execute_single_run()` and the SLURM worker `run_task.py` call it.

---

## SLURM resource defaults

Defined in `submit_array.sh` — adjust to your cluster limits:

| Directive | Default | Notes |
|---|---|---|
| `--cpus-per-task` | `1` | LPG runs are single-threaded |
| `--mem` | `4G` | Typical usage <2 GB; 4 GB gives headroom |
| `--time` | `2:00:00` | Safe default for a single-year simulation |
| `MAX_CONCURRENT` | max 50 concurrent | Concurrency cap applied to the auto-generated `--array` range; tune to cluster fair-use policy |

Two environment variables (exported in `submit_array.sh`) control where data goes:

| Variable | Default | Purpose |
|---|---|---|
| `LPG_OUTPUT_DIR` | `slurm_output/` | Where per-task `task_NNNNNN.h5` results are written |
| `LPG_WORK_DIR` | `$TMPDIR` | Base for each task's `C<task_id>` LPG calc dir; keep on node-local scratch |

Both fall back to in-repo defaults when unset, so local testing works without the cluster.

Logs are written to `logs/task_<jobid>_<arrayid>.out/.err`.
