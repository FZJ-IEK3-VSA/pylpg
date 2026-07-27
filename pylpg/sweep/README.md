# pylpg.sweep — Parallelised LPG Simulations on SLURM

This package contains everything needed to run large-scale LPG household simulations in parallel on a SLURM cluster.  
All configuration lives in `config.py` and the simulation logic in `simulation.py`; the SLURM entry points are thin wrappers around them.

Every entry point is a module, so run them with `python -m pylpg.sweep.<name>` from the repo root (running the files directly, e.g. `python pylpg/sweep/generate_tasks.py`, also works).

> For a detailed developer-facing account of the code changes behind this workflow (the new `LPGExecutor` behaviour, the new execute function, and the whole `pylpg/sweep/` subsystem), see [CHANGELOG.md](CHANGELOG.md).

---

## Folder contents

| File                | Purpose                                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------------------- |
| `config.py`         | All tunable sweep parameters (the `# ---- CONFIG ----` block) and the output paths derived from `BASE_OUTPUT_DIR` |
| `keys.py`           | The `ClimateSetKey` / `TransportVariantKey` types a config is written in                                         |
| `simulation.py`     | Helper functions, the shared `run_lpg_simulation()` primitive, and the sequential runner (also works standalone) |
| `generate_tasks.py` | Enumerates all parameter combinations, writes `tasks.json`                                                       |
| `run_task.py`       | SLURM array worker — executes one task from `tasks.json`                                                         |
| `merge_results.py`  | Assembles per-task HDF5 files into final per-template HDF5 files                                                 |

The SLURM batch script is **not** part of the package: it is a per-cluster file you own. Copy it from [`examples/submit_array.example.sh`](../../examples/submit_array.example.sh) — see [step 3](#3-submit-the-job-array).

---

## Configuration

All parameters are set in `config.py` under `# ---- CONFIG ----`. For the smallest sweep that still runs end to end (one template × one climate × one transport variant × one run), copy [`examples/sweep_config_minimal.py`](../../examples/sweep_config_minimal.py) over `config.py` and edit from there:

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
python -m pylpg.sweep.generate_tasks
```

This writes `tasks.json` to `BASE_OUTPUT_DIR` — alongside the sweep's other output, never inside the repo or the installed package — and prints the exact path and `--array` range:

```
Generated 42 tasks  ->  /path/to/output/tasks.json
Submit with:  sbatch --array=0-41 submit_array.sh
Cap concurrency by appending %K, e.g.  sbatch --array=0-41%50 submit_array.sh
```

### 3. Submit the job array

**First-time setup:** the batch script holds your cluster-specific paths, so it
is not tracked — any `submit_array.sh` is git-ignored. Create it once from the
tracked example in `examples/`, then edit the paths inside it:

```bash
cp examples/submit_array.example.sh submit_array.sh
# then set LPG_WORK_DIR (and optionally LPG_OUTPUT_DIR) in submit_array.sh
```

**Before the first submission,** make sure the LPG binary is already in `pylpg/`
(run one task locally, or `python -m pylpg.sweep.simulation` once). Otherwise the first
wave of array tasks all race to download it and corrupt `pylpg/`.

Then submit the array, passing the index range explicitly. Indices are 0-based
and index into `tasks.json`, so N tasks span `0 .. N-1` (the exact range is
printed by `generate_tasks.py`):

```bash
sbatch --array=0-55    submit_array.sh   # all 56 tasks
sbatch --array=0-55%50 submit_array.sh   # ... capped at 50 concurrent
sbatch --array=3,7,9   submit_array.sh   # re-run just these tasks
```

`--array` is passed on the command line rather than as a `#SBATCH` directive
because the task count changes per manifest; append `%K` to cap how many run
concurrently, tuned to your cluster's fair-use policy.

Each array element runs one independent simulation and writes its result to `<base>/tasks/task_NNNNNN.h5`, where `<base>` is `BASE_OUTPUT_DIR` from `config.py` (see [Output location](#output-location)).  
One file per task means there are **no concurrent write conflicts**. These per-task files are temporary — `merge_results.py` deletes them once they are merged.

Each task also runs its LPG calculation in its own working directory `C<task_id>`, isolating concurrent runs. The directory holds only that task's `calcspec.json` and `results/` output — the engine runs in place from the source binary directory and all tasks share the read-only `profilegenerator.db3`, so nothing large is copied per task. To keep the result output off shared storage, `submit_array.sh` sets `LPG_WORK_DIR` to node-local scratch (`$TMPDIR`); `run_task.py` passes `calculation_index=task_id` so no two tasks share a directory.

### 4. Merge results

After all jobs finish:

```bash
python -m pylpg.sweep.merge_results
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
python -m pylpg.sweep.simulation
```

**Single task** (for testing one array element):

```bash
python -m pylpg.sweep.run_task --task-id 0
```

---

## How the scripts relate

```
keys.py                 ClimateSetKey / TransportVariantKey
│
config.py               CONFIG (all sweep parameters) + BASE_OUTPUT_DIR paths
│
simulation.py           helper functions, run_lpg_simulation()
│  (imports config.py)
│
├── generate_tasks.py   reads CONFIG → writes <base>/tasks.json
│
├── run_task.py         reads <base>/tasks.json[N] → calls run_lpg_simulation()
│                                                  → writes <base>/tasks/task_N.h5
│
└── merge_results.py    reads <base>/tasks/*.h5 + <base>/tasks.json
                        → writes <base>/multi_runs_output/<template>.h5
                        → deletes the merged <base>/tasks/*.h5
```

`run_lpg_simulation()` defined in `simulation.py` is the single shared execution primitive — both the sequential `execute_single_run()` and the SLURM worker `run_task.py` call it.

---

## SLURM resource defaults

Defined in `submit_array.sh` — adjust to your cluster limits:

| Directive         | Default           | Notes                                                                                          |
| ----------------- | ----------------- | ---------------------------------------------------------------------------------------------- |
| `--cpus-per-task` | `1`         | LPG runs are single-threaded                                                        |
| `--mem`           | `2G`        | Typical usage <2 GB; raise for headroom on complex households                       |
| `--time`          | `2:00:00`   | Safe default for a single-year simulation                                           |
| `--array` cap `%K` | (you choose) | Concurrency cap appended to the `sbatch --array` range; tune to cluster fair-use policy |

## Output location

**Switch cluster ↔ local with one flag** in `config.py`:

| `RUN_ON_CLUSTER` | `BASE_OUTPUT_DIR` becomes            | Where results go                                    |
| ---------------- | ------------------------------------ | --------------------------------------------------- |
| `True`           | `CLUSTER_BASE_OUTPUT_DIR` (`/fast/…`) | shared project storage on the cluster               |
| `False`          | the repo root                        | the repo's own `multi_runs_output/` (local testing) |

Every result path derives from that one base, `BASE_OUTPUT_DIR`, and the scripts
create these subdirectories inside it on demand:

| Path under `BASE_OUTPUT_DIR` | Written by          | Contents                                                     |
| ---------------------------- | ------------------- | ------------------------------------------------------------ |
| `tasks.json`                 | `generate_tasks.py` | the task manifest, read by `run_task.py` + `merge_results.py` |
| `tasks/`                     | `run_task.py`       | temporary `task_<NNNNNN>.h5` (deleted by `merge_results.py`) |
| `multi_runs_output/`         | `merge_results.py`  | final `<template>.h5` + `runs_metadata.csv`                  |

Because all three scripts import the same `BASE_OUTPUT_DIR` — the generator
(`generate_tasks.py`), the writer (`run_task.py`) and the reader
(`merge_results.py`) — an array worker under SLURM and an interactive merge on
the login node can never look in different directories. `LPG_OUTPUT_DIR`
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
