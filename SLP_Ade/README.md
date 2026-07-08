# SLP_Ade — Parallelised LPG Simulations on SLURM

This folder contains everything needed to run large-scale LPG household simulations in parallel on a SLURM cluster.  
All configuration lives in `config.py` and the simulation logic in `simulation.py`; the three SLURM scripts are thin wrappers around them.

> For a detailed developer-facing account of the code changes behind this workflow (the new `LPGExecutor` behaviour, the new execute function, and the whole `SLP_Ade/` subsystem), see [CHANGELOG.md](CHANGELOG.md).

---

## Folder contents

| File                | Purpose                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `config.py`         | All tunable sweep parameters (the `# ---- CONFIG ----` block)                                                    |
| `simulation.py`     | Helper functions, the shared `run_lpg_simulation()` primitive, and the sequential runner (also works standalone) |
| `generate_tasks.py` | Enumerates all parameter combinations, writes `tasks.json`                                                       |
| `run_task.py`       | SLURM array worker — executes one task from `tasks.json`                                                         |
| `merge_results.py`  | Assembles per-task HDF5 files into final per-template HDF5 files                                                 |
| `submit_array.sh`   | SLURM batch script                                                                                               |

---

## Configuration

All parameters are set in `config.py` under `# ---- CONFIG ----`:

| Variable                  | Description                                                                                | Default                                               |
| ------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| `YEAR`                    | Simulation year                                                                            | `2022`                                                |
| `HOUSEHOLD_TEMPLATE_KEYS` | List of template names, or `None` for all                                                  | `None` (all)                                          |
| `CLIMATE_SET_KEYS`        | List of `ClimateSetKey` presets (geo location + temp profile + tag), or `None` for all combinations | 3 German cities                             |
| `TRANSPORT_VARIANT_KEYS`  | List of `TransportVariantKey` presets                                                      | no-transport + home-charging                          |
| `RUNS_PER_COMBO_MAP`      | Dict mapping combo-tag patterns to run counts                                              | `{"no_transport": 1, "home_charge_bus_cars_30km": 3}` |
| `HOUSETYPE`               | LPG house type                                                                             | `HT20_Single_Family_House_no_heating_cooling`         |
| `LPG_BINARY_PATH`         | Custom LPG binary, or `None` for auto-download                                             | `None`                                                |
| `SAVE_CSV` / `SAVE_HDF5`  | Output format switches                                                                     | `False` / `True`                                      |

---

## Workflow

### 1. Configure

Edit `config.py` to set your templates, climate presets, transport variants, and run counts.

### 2. Generate the task manifest

Run once on the **login node**:

```bash
python SLP_Ade/generate_tasks.py
```

This writes `tasks.json` into `SLP_Ade/`, e.g.:

```
Generated 42 tasks  ->  /path/to/pylpg/SLP_Ade/tasks.json
Submit with:  bash SLP_Ade/submit_array.sh   (reads the count from tasks.json automatically)
Or manually:  sbatch --array=0-41 SLP_Ade/submit_array.sh
```

### 3. Submit the job array

No manual range editing needed — just run:

```bash
bash SLP_Ade/submit_array.sh
```

The script counts the entries in `tasks.json`, then re-submits itself as a SLURM array job covering `0 .. count-1` (capped at `MAX_CONCURRENT` concurrent tasks, default 50). Launch it with `bash` on the login node; `sbatch SLP_Ade/submit_array.sh` also works but runs the one-line bootstrap inside a compute-node allocation. The bootstrap also **pre-fetches the LPG binary once** on the login node, so the first wave of concurrent tasks doesn't race to download it.

Each array element runs one independent simulation and writes its result to `<base>/tasks/task_NNNNNN.h5`, where `<base>` is `BASE_OUTPUT_DIR` from `config.py` (see [Output location](#output-location)).  
One file per task means there are **no concurrent write conflicts**. These per-task files are temporary — `merge_results.py` deletes them once they are merged.

Each task also runs its LPG calculation in its own working directory `C<task_id>`, isolating concurrent runs. The directory holds only that task's `calcspec.json` and `results/` output — the engine runs in place from the source binary directory and all tasks share the read-only `profilegenerator.db3`, so nothing large is copied per task. To keep the result output off shared storage, `submit_array.sh` sets `LPG_WORK_DIR` to node-local scratch (`$TMPDIR`); `run_task.py` passes `calculation_index=task_id` so no two tasks share a directory.

### 4. Merge results

After all jobs finish:

```bash
python SLP_Ade/merge_results.py
```

Output (under `<base>/multi_runs_output/`, where `<base>` is `BASE_OUTPUT_DIR`):

- `<template_name>.h5` — one file per household template, with hierarchy:  
  `/<climate_tag>/<transport_tag>/run_<N>/<data_type>`
- `runs_metadata.csv` — summary of every merged run

Once every task is folded in, the temporary `<base>/tasks/task_NNNNNN.h5` files are
**deleted** (pass `--keep-tasks` to keep them). Nothing is written into the repo.

The `<data_type>` groups are the per-load-type profiles (e.g. `Electricity`, `Hot_water`).
When flexibility is enabled (it is by default in `run_lpg_simulation`), two extra kinds of
`<data_type>` appear:

- `<LoadType>_NoFlex` — the same load profile **without** flexible-device shifting applied.
  Comparing `<LoadType>` against `<LoadType>_NoFlex` is how you read out the effect of
  flexibility. (Flexibility itself is not a load type, so there is no standalone
  "flexibility" series.)
- `FlexibilityEvents` — the load-shifting **event log** (one row per event: flexible
  device, its loads, timing), flattened from the LPG's per-household
  `FlexibilityEvents.<HHKey>.json` reports. This is a records table, not a time series.

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
│                                           → writes <base>/tasks/task_N.h5
│
└── merge_results.py    reads <base>/tasks/*.h5 + tasks.json
                        → writes <base>/multi_runs_output/<template>.h5
                        → deletes the merged <base>/tasks/*.h5
```

`run_lpg_simulation()` defined in `simulation.py` is the single shared execution primitive — both the sequential `execute_single_run()` and the SLURM worker `run_task.py` call it.

---

## SLURM resource defaults

Defined in `submit_array.sh` — adjust to your cluster limits:

| Directive         | Default           | Notes                                                                                          |
| ----------------- | ----------------- | ---------------------------------------------------------------------------------------------- |
| `--cpus-per-task` | `1`               | LPG runs are single-threaded                                                                   |
| `--mem`           | `4G`              | Typical usage <2 GB; 4 GB gives headroom                                                       |
| `--time`          | `2:00:00`         | Safe default for a single-year simulation                                                      |
| `MAX_CONCURRENT`  | max 50 concurrent | Concurrency cap applied to the auto-generated `--array` range; tune to cluster fair-use policy |

## Output location

**Switch cluster ↔ local with one flag** in `config.py`:

| `RUN_ON_CLUSTER` | `BASE_OUTPUT_DIR` becomes            | Where results go                                    |
| ---------------- | ------------------------------------ | --------------------------------------------------- |
| `True`           | `CLUSTER_BASE_OUTPUT_DIR` (`/fast/…`) | shared project storage on the cluster               |
| `False`          | the repo root                        | the repo's own `multi_runs_output/` (local testing) |

Every result path derives from that one base, `BASE_OUTPUT_DIR`, and the scripts
create these subdirectories inside it on demand:

| Subdirectory of `BASE_OUTPUT_DIR` | Written by         | Contents                                                     |
| --------------------------------- | ------------------ | ------------------------------------------------------------ |
| `tasks/`                          | `run_task.py`      | temporary `task_<NNNNNN>.h5` (deleted by `merge_results.py`) |
| `multi_runs_output/`              | `merge_results.py` | final `<template>.h5` + `runs_metadata.csv`                  |

Because both the writer (`run_task.py`) and the reader (`merge_results.py`)
import the same `BASE_OUTPUT_DIR`, an array worker under SLURM and an interactive
merge on the login node can never look in different directories. `LPG_OUTPUT_DIR`
overrides the base in either mode for one-off runs — if you export it, do so in
**both** shells (the `submit_array.sh` job *and* the shell you run
`merge_results.py` in), otherwise the merge falls back to the `config.py` default.

`merge_results.py` deletes the per-task `tasks/*.h5` files once they are merged;
pass `--keep-tasks` to retain them.

One further environment variable (exported in `submit_array.sh`) controls where
each task's scratch LPG calc dir goes:

| Variable       | Default   | Purpose                                                                    |
| -------------- | --------- | -------------------------------------------------------------------------- |
| `LPG_WORK_DIR` | `$TMPDIR` | Base for each task's `C<task_id>` LPG calc dir; keep on node-local scratch |

Logs are written to `logs/task_<jobid>_<arrayid>.out/.err`.
