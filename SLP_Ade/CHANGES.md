# SLP_Ade — Change Guide (since `new-python-bindings-for-citysim`)

This document is a **developer-facing** record of the code changes made on this branch
after it split off from `new-python-bindings-for-citysim` (merge-base `453071d`). It
explains *what* changed and *why*, at the code level. For **how to run** the workflow, see
[README.md](README.md).

The work falls into two parts:

1. **Core library changes** to [../pylpg/lpg_execution.py](../pylpg/lpg_execution.py) that
   made the parallel workflow possible (a new execution primitive and a reworked
   `LPGExecutor`).
2. **A new subsystem**, the entire `SLP_Ade/` folder — a fan-out/fan-in SLURM workflow for
   running thousands of LPG simulations in parallel.

Pure docstring/comment/formatting/rename commits are intentionally omitted here; only
behaviour-relevant changes are documented.

---

## 1. Core library changes — `pylpg/lpg_execution.py`

All changes here live in [../pylpg/lpg_execution.py](../pylpg/lpg_execution.py). They are
the foundation the `SLP_Ade/` workflow is built on.

### 1.1 New execution primitive: `execute_lpg_with_householddata_enabled_flex_and_transport_custom()`

A new public function was added alongside the existing `execute_lpg_with_householdata()`.
It is the **single execution primitive** that the entire `SLP_Ade/` workflow calls (via
`run_lpg_simulation()` in [simulation.py](simulation.py)).

What it adds over the previous `execute_lpg_with_householdata()`:

- **Decoupled climate inputs.** It takes `geographic_location` **and**
  `temperature_profile` as *separate* `JsonReference` arguments, instead of bundling a
  location with an implied temperature profile. This lets a sweep pair any location with
  any temperature series (e.g. Chemnitz location + Dresden temperature).
- **Explicit flexibility / transport toggles.** `enable_flexibility` and
  `enable_transportation` booleans drive which `CalcOption`s get appended to the request:
  - `enable_transportation` → `CalcOption.TansportationDeviceJsons`
    (**note the upstream typo — missing "r" — it is correct as written and must be matched**).
  - `enable_flexibility` → `CalcOption.JsonHouseholdSumFiles`,
    `CalcOption.JsonHouseholdSumFilesNoFlex`, and `CalcOption.FlexibilityEvents`.
  - `CalcOption.BodilyActivityStatistics` is **always** appended (bodily-activity output
    is unconditional).
- **`working_directory` passthrough.** Forwards a `working_directory` argument to
  `LPGExecutor` (see §1.2) so per-calculation dirs can be relocated to node-local scratch.
- **`lpg_binary_path` passthrough.** Like the other execute functions (§1.4), it accepts a
  custom binary path.

It also sets `TargetHeatDemand` / `TargetCoolingDemand` when
`target_heating_demand` / `target_cooling_demand` are supplied, and applies `random_seed`,
`start`/`end` dates, and `energy_intensity` on the calc spec.

### 1.2 `LPGExecutor.__init__` rework — package dir vs working dir

`LPGExecutor.__init__` was reworked to separate **where the binaries live** from **where a
calculation runs**:

- **`self.package_directory`** — the pylpg package folder. Binaries are always resolved
  from and (on first use) downloaded into here. This never moves.
- **`self.working_directory`** — the base for the per-calculation `C<idx>` folders. It
  defaults to the package directory, but when a `working_directory` argument is passed it
  is used instead (and created with `mkdir(parents=True, exist_ok=True)`).

Why this matters: each calculation copies the ~155 MB binary + database into its own
`C<idx>/` dir. On a cluster, pointing `working_directory` at fast **node-local scratch**
(e.g. `$TMPDIR`) keeps those copies off shared storage — while binaries are still read
from / downloaded into the package dir exactly once. This split is what makes the parallel
SLURM runs both correct (no shared `C<idx>`) and fast (scratch-local I/O).

### 1.3 Custom binary resolution + `_lpg_binary_details_for_platform()` helper

The platform → (binary path, executable name) logic was extracted into a module-level
helper, `_lpg_binary_details_for_platform(working_directory)`, returning e.g.
`(<dir>/LPG_win, "simengine2.exe")` on Windows or `(<dir>/LPG_linux, "simengine2")` on
Linux (and raising on unknown platforms).

`__init__` now resolves the binary in one of two ways:

- **`lpg_binary_path` given** — download is skipped. If the path is a **file**, it is used
  directly (parent dir + filename). If it is a **directory**, the platform-default
  executable name is looked up inside it via `_lpg_binary_details_for_platform`. Otherwise
  a `FileNotFoundError` is raised.
- **`lpg_binary_path` omitted** — the platform default is used, and the binary is
  downloaded into `package_directory` if not already present.

The helper is reused outside the class too: the `submit_array.sh` pre-flight step imports
it to locate/pre-download the binary on the login node (see §2.6).

### 1.4 `lpg_binary_path` threaded through every execute function

The optional `lpg_binary_path: Optional[Union[Path, str]] = None` argument was added to
**all** public execution helpers so a custom LPG build can be used per call without a
download:

- `execute_lpg_tsib()`
- `execute_lpg_single_household()`
- `execute_lpg_with_householdata()`
- `execute_lpg_with_householddata_enabled_flex_and_transport_custom()` (§1.1)
- `execute_lpg_with_many_householdata()`
- `execute_lpg_with_householdata_with_csv_save()`
- `execute_grid_calc()`

The user-facing behaviour (file vs directory path, platform-default lookup) is documented
in the root [../README.md](../README.md) under *"Choosing The LPG Binary At Runtime"*.

> Note: the root README's example uses the shorthand name
> `execute_lpg_with_householddata_custom(...)`; the actual function is
> `execute_lpg_with_householddata_enabled_flex_and_transport_custom`.

### 1.5 Flexibility outputs: NoFlex profiles keyed distinctly + event log surfaced

When `enable_flexibility=True`, the LPG emits two extra kinds of output that were
previously being lost. Both are now surfaced correctly.

**NoFlex profiles — distinct keys, no more collision.** With flexibility on, the LPG writes
`Sum.NoFlexDevices.<LoadType>.<HHKey>.json` files: the same load profiles *without* the
flexible-device shifting applied. These carry an **identical** `LoadTypeName`/`HHKey` to
their flexible counterparts. The old reader built each column key as
`<LoadTypeName>_<HHKey>`, so the flexible and NoFlex profiles mapped to the *same* column.
Worse, `read_all_json_results_in_directory()` first globbed `Sum.*.json` (which already
matches the NoFlex files) **and then** globbed `*NoFlex*.json` again and appended those,
so the NoFlex profile was processed last and silently **overwrote** the flexible one —
enabling flexibility actually made the output show the *no-flexibility* series. The reader
now:

- drops the redundant second `*NoFlex*.json` glob (the `Sum.*.json` glob already covers
  them), and
- detects NoFlex files by filename and keys them `<LoadTypeName>_NoFlex_<HHKey>`.

So a flexibility run now carries both series as their own columns / data types
(`<LoadType>` and `<LoadType>_NoFlex`); their difference is the effect of flexibility.

**Flexibility event log — now read.** The LPG also writes one
`FlexibilityEvents.<HHKey>.json` per household into `results/**Reports**/` (not `Results/`,
which is why the profile reader never saw it). Each file is a JSON list of load-shifting
events — an event log, not a minute profile. A new
`LPGExecutor.read_flexibility_events()` flattens every household's events
(`pandas.json_normalize`, one row per event, tagged with `HHKey`; nested list/dict cells
JSON-encoded so the frame is HDF5-`fixed`-safe) into one DataFrame. When flexibility is
enabled, `execute_lpg_with_householddata_enabled_flex_and_transport_custom()` attaches it
to the result frame as `df.attrs["flexibility_events"]` (frame metadata, since its shape
differs from the profiles). The `SLP_Ade` workflow stores it as its own `FlexibilityEvents`
group (see §2.2 / §2.4).

---

## 2. The `SLP_Ade/` workflow (new subsystem)

`SLP_Ade/` is an entirely new fan-out/fan-in pipeline for large parameter sweeps on a
SLURM cluster. Python never simulates anything — it expands a config into independent
tasks, runs each as an array element, and reassembles the outputs.

```
config.py            CONFIG: templates × climate sets × transport variants × runs
      │
generate_tasks.py    cartesian product → tasks.json (+ task_count.txt)   [FAN-OUT]
      │
      ▼
 ┌────────────── SLURM array (one element per task) ──────────────┐
 │  run_task.py[0]   run_task.py[1]   ...   run_task.py[N-1]       │
 │      │                │                       │                 │
 │  task_000000.h5   task_000001.h5    ...   task_00NNNN.h5        │
 └────────────────────────────────────────────────────────────────┘
      │
      ▼
merge_results.py     per-task files → per-template HDF5 files       [FAN-IN]
```

Every entry point shares one execution primitive (`run_lpg_simulation`) and one config
module, so the sequential runner and the SLURM path can never drift apart.

### 2.1 `config.py` — single source of truth

[config.py](config.py) holds the `# ---- CONFIG ----` block, isolated from execution
logic so `generate_tasks.py`, `run_task.py`, and the sequential runner all read one place.

Key design points:

- **`TransportVariantKey`** (frozen dataclass) — a named preset for a transport variant
  (`simulate_transportation`, charging/device/route set keys, `tag`), replacing earlier
  ad-hoc tuples.
- **String-key strategy.** `get_attr_key(cls, value)` reverse-looks-up the *attribute
  name* for an `lpgdata` value, so config stores JSON-serialisable **string keys** into
  the `lpgdata.*` catalogs rather than objects.
- **Decoupled climate presets.** `CLIMATE_SET_KEYS` entries are
  `(geo_location_key, temperature_profile_key, tag)` triples — location and temperature
  profile are independent (matching §1.1). `None` means "all combinations".
- **Runs per combination.** `RUNS_PER_COMBO_MAP` + `get_runs_for_combo(combo_tag)` decide
  how many stochastic repeats each combination gets (pattern match on the combo tag, with
  a default fallback), so transport variants can be sampled more heavily than baselines.

### 2.2 `simulation.py` — shared primitive + sequential runner

[simulation.py](simulation.py) holds the shared execution primitive and a standalone
sequential runner (`python SLP_Ade/simulation.py`).

- **`run_lpg_simulation()`** — the one primitive called by *both* the sequential
  `execute_single_run()` and the SLURM worker [run_task.py](run_task.py). It builds a
  templated `HouseholdData` and calls the new core function (§1.1).
  - **Back-compat forwarding.** It inspects the target function's signature
    (`inspect.signature(...).parameters`) and only forwards `lpg_binary_path` /
    `working_directory` if the installed pylpg actually supports them — so an older pylpg
    without those parameters still works. `working_directory` is taken from the
    `LPG_WORK_DIR` environment variable.
- **Helper functions** (also reused by the SLURM scripts and tests):
  `collect_lpg_members()` (introspect all members of an `lpgdata` catalog by type),
  `select_by_keys()`, `resolve_optional_key()`, `make_climate_variants()`,
  `make_transport_variants()` + the resolved `TransportVariant` dataclass,
  `safe_name()` (filesystem/HDF5-safe keys), `split_dataframe_by_type()` (regroup result
  columns by the prefix before the last `_`), `attach_flexibility_events()` (fold the
  flexibility event log from `df.attrs` into the data-type map as a `FlexibilityEvents`
  group — see §1.5), `create_combo_tag()`, and `save_as_HDF5()`.
- **HDF5 layout.** The sequential runner writes one file per template with the hierarchy
  `/<climate_tag>/<transport_tag>/run_<N>/<data_type>` (+ a `_metadata` node) — the same
  layout the merge step reproduces (§2.5).

### 2.3 `generate_tasks.py` — fan-out to a flat manifest

[generate_tasks.py](generate_tasks.py) expands the CONFIG cartesian product (templates ×
climate sets × transport variants × runs-per-combo) into a flat `tasks.json` at the repo
root, one entry per independent run, plus `task_count.txt`.

- **String-key-only manifest.** Each task stores only string keys into the `lpgdata.*`
  catalogs, keeping `tasks.json` fully JSON-serialisable; the worker resolves keys back to
  objects at runtime.
- **Deterministic seeding.** `_deterministic_seed(combo_tag, run_idx)` derives a 31-bit
  seed from `MD5("<combo_tag>_<run_idx>")`, so the manifest is **reproducible** — the same
  config always yields the same seeds regardless of when/where it is generated. (Contrast
  with the sequential runner in [simulation.py](simulation.py), which uses a time-based
  seed for interactive exploration.)
- **`task_count.txt`** is written so `submit_array.sh` can derive its `--array` range
  automatically instead of a manual, drift-prone edit.

### 2.4 `run_task.py` — the array worker

[run_task.py](run_task.py) runs one task: it reads `tasks.json[N]` (N from `--task-id`,
defaulting to `$SLURM_ARRAY_TASK_ID`), resolves string keys back to `lpgdata` objects, and
calls `run_lpg_simulation()`.

- **Per-task isolation.** It passes `calculation_index=task_id`, so concurrent array
  elements never share a `C<idx>` working directory. `clear_previous_calc=True` guarantees
  a clean dir if a task id is requeued.
- **One file per task.** Each task writes a single `slurm_output/task_<NNNNNN>.h5`
  (`/data/<data_type>` + `/metadata`), so there are **zero concurrent HDF5 write
  conflicts**. The output directory is overridable via `$LPG_OUTPUT_DIR`. When flexibility
  is enabled, the flexibility event log rides along as a `/data/FlexibilityEvents` group
  (§1.5), so the generic `/data/*` copy in the merge step (§2.5) carries it through with no
  special-casing.

### 2.5 `merge_results.py` — fan-in

[merge_results.py](merge_results.py) assembles all per-task files into per-template HDF5
files under `multi_runs_output/`, reproducing the sequential layout
`/<climate_tag>/<transport_tag>/run_<N>/<data_type>` (+ `_metadata`). It also:

- writes `multi_runs_output/runs_metadata.csv` summarising every merged run, and
- **reports missing tasks** — any `task_id` present in `tasks.json` but lacking an output
  file is listed, so failed/incomplete array elements are visible.

### 2.6 `submit_array.sh` — self-resubmitting batch script

[submit_array.sh](submit_array.sh) is a thin SLURM wrapper with two notable design points:

- **Auto-ranged array via a self-resubmit bootstrap.** `--array` is deliberately **not** a
  `#SBATCH` directive (SLURM parses those before the script body runs, so it cannot read a
  file). Instead, when launched with no `$SLURM_ARRAY_TASK_ID`, the script reads
  `task_count.txt` and re-submits itself with
  `--array=0-(N-1)%MAX_CONCURRENT` (`MAX_CONCURRENT` caps concurrency, default 50).
- **Login-node binary pre-fetch.** Before submitting, the bootstrap imports
  `_lpg_binary_details_for_platform` (§1.3) and downloads the LPG binary once on the login
  node if missing — otherwise the first wave of concurrent tasks would all race to
  download into `pylpg/` and corrupt the folder.
- **Scratch wiring.** It exports `LPG_OUTPUT_DIR` (per-task results) and `LPG_WORK_DIR`
  (base for `C<task_id>` calc dirs, pointed at `$TMPDIR` node-local scratch). Both fall
  back to in-repo defaults when unset, so local testing works without a cluster.

---

## 3. Supporting changes

- **`requirements.txt`** — added `tables` (PyTables). Required for the HDF5 output in
  `SLP_Ade/`; without it, `pd.HDFStore(...)` calls fail.
- **`.gitignore`** — now ignores `pyLPG_env/`, `SLP_Ade/__pycache__/`, the generated
  `tasks.json` / `task_count.txt`, and the `multi_runs_output/` output directory.
- **Tests**
  - [../test/test_slp_ade.py](../test/test_slp_ade.py) — new **fast** tests that never
    invoke LPG: `safe_name`, `split_dataframe_by_type`, `collect_lpg_members`,
    `select_by_keys`, `create_combo_tag`, `get_runs_for_combo`, deterministic-seed
    behaviour, and `build_task_list` coverage (sequential ids, key presence, run-index
    completeness, reproducibility, JSON-serialisability, climate/transport coverage).
  - [../test/test_pylpg.py](../test/test_pylpg.py) — new `LPGExecutor` tests for the
    core changes: `test_lpg_executor_uses_custom_binary_path`,
    `test_lpg_executor_custom_working_directory`, and
    `test_lpg_binary_details_for_platform`.

---

## 4. Known follow-ups

- **`HOUSETYPE` is still a scalar.** Templates, climate sets, and transport variants all
  iterate over key lists, but the house type is a single value in [config.py](config.py).
  Making it a swept dimension would mean: iterate house-type keys in
  [generate_tasks.py](generate_tasks.py), resolve the key back in [run_task.py](run_task.py),
  and accept the house type as a parameter in [simulation.py](simulation.py).
