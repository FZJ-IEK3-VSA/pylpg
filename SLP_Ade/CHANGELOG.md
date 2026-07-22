# SLP_Ade — Changelog / Change Guide (since `new-python-bindings-for-citysim`)

This document is a **developer-facing** record of the code changes made on this branch
after it split off from `new-python-bindings-for-citysim` (merge-base `453071d`). It
explains *what* changed and *why*, at the code level, and is kept current with the branch —
it is a living description of the branch's final state, not an append-only release log. For
**how to run** the workflow, see [README.md](README.md).

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
- **Idle-mode toggle.** A later addition: `enable_idle_mode` drives
  `CalcSpec.set_EnableIdlemode(...)` so a household template can no longer abort the run by
  boxing a person into a timestep with zero available affordances (see §1.8).
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

Why this matters: on a cluster, pointing `working_directory` at fast **node-local scratch**
(e.g. `$TMPDIR`) keeps each calculation's output (its `calcspec.json` and `results/` subtree)
off shared storage, while binaries are still read from / downloaded into the package dir
exactly once. This split is what makes the parallel SLURM runs both correct (no shared
`C<idx>`) and fast (scratch-local I/O). (Originally each `C<idx>` also received a full
~155 MB copy of the binary + database folder; **§1.6 removed that** — the calc dir now holds
only the run's own inputs/outputs.)

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

### 1.6 No per-calculation copy — run in place, share the read-only database

`LPGExecutor` no longer copies the ~155 MB binary + database folder into each `C<idx>/`
dir. Two changes in [../pylpg/lpg_execution.py](../pylpg/lpg_execution.py):

- **`__init__`** — the `shutil.copytree(src, C<idx>)` was replaced by an `os.makedirs()`
  of an **empty** `C<idx>/`. The engine was already invoked *in place* from the source
  binary directory (`lpg_simengine_filepath()` builds its path from
  `calculation_src_directory`, not the copy), so the copied DLLs were never actually used —
  only `C<idx>` as the process `cwd` mattered, for `calcspec.json` and the `results/` output.
- **`make_default_lpg_settings`** — `PathToDatabase` changed from the relative
  `"profilegenerator.db3"` (which resolved into the per-calc copy) to the **absolute path of
  the shared source db3** (`Path(self.calculation_src_directory, "profilegenerator.db3").resolve()`).

**Why this is safe (verified empirically).** The engine opens `profilegenerator.db3`
**read-only**:

- The db3 is **byte-identical (SHA-256) before and after** a full 31-day flexibility run,
  and the calc-dir copy was byte-identical to the source — the run never mutates it.
- No SQLite `-journal` / `-wal` / `-shm` / lock side-files are created next to the db3.
- **Two concurrent** runs pointed at the *same* source db3 both completed successfully
  (full 28-profile output each), so shared read-only access is safe for concurrent SLURM
  array workers.

**Effect.** Every calc / SLURM task now skips the ~155 MB copy — near-instant startup and
much less I/O. Output isolation is unchanged: each run still gets its own `C<idx>` (unique
`calculation_index`) holding only its `calcspec.json` + `results/`. `working_directory` /
`LPG_WORK_DIR` still usefully steers that (smaller) output I/O to node-local scratch.

**Cluster caveat.** The binary + db3 are now read *live* from `LPG_BINARY_PATH` on every
run instead of being copied to scratch once, so that path (the `linux-x64/publish` build in
[config.py](config.py)) should live on reasonably fast storage on the cluster.

### 1.7 `error_tolerating_directory_clean()` — guard now checks the *resolved* path

`LPGExecutor.error_tolerating_directory_clean()` has a safety net: it refuses to clean a
path shorter than 10 characters (a crude guard against accidentally wiping `/` or `C:\`).
That guard was being applied to the **raw** path string. Because §1.2/§1.6 made the
per-calculation dir a short *relative* path (e.g. `C1` when `working_directory` defaults to
the current dir), a legitimate calc dir could trip the guard and abort the clean. The method
now resolves to an **absolute path first** (`str(Path(path).resolve())`) and length-checks
that: a normal relative calc dir resolves to a long absolute path and passes, while a
genuinely dangerous short path (the filesystem root) still trips it. A docstring was added
explaining the intent so the length constant is not mistaken for arbitrary.

### 1.8 Idle-mode — stop child-affordance dead-ends from aborting a run

`execute_lpg_with_householddata_enabled_flex_and_transport_custom()` gained an
`enable_idle_mode: bool = False` parameter that calls `CalcSpec.set_EnableIdlemode(...)`.

The problem it solves: the LPG treats "a person has **0 available affordances** at some
timestep" as a fatal `DataIntegrityException` and aborts the whole run (writing no results,
so the execute function returns `None` and the task is lost). This dead-end is **stochastic
and concentrated in households with young children** — children have few permissible
affordances, so a random schedule can leave them all simultaneously occupied. On the first
full sweep, every task that failed this way was a child-bearing household. Idle-mode injects
a fallback "Idle" activity so the stuck person does nothing for those steps instead of
aborting, which is what lets a large parameter sweep complete rather than silently drop those
runs.

- **Trade-off (documented in the parameter docstring):** the affected steps show a brief
  "doing nothing" (no activity-driven appliance load) in place of a real activity — a minor
  behavioural artifact accepted in exchange for the run completing.
- **Default is `False`** in the core function, preserving the stricter fail-loud behaviour
  for callers that would rather a broken template error out. The `SLP_Ade` workflow opts in
  unconditionally (see §2.2).

### 1.9 Engine exit code is now checked — non-zero raises instead of "no results"

`execute_lpg_binaries()` previously fired the `simengine2 processhousejob` subprocess and
ignored its exit code (its return type was `Any`, effectively `None`). A run that the engine
aborted (e.g. the `DataIntegrityException` above, or any other fatal error) therefore surfaced
only much later as a confusing "no results returned" far from the real cause.

It now captures the `subprocess.run(...)` result and, on a non-zero `returncode`, raises a
`RuntimeError` naming the **exit code** and the **calculation directory** (whose `Log.*.txt`
files hold the real cause). Return type is now `None`. This turns a silent, misattributed
failure into an immediate, located one — and pairs with the `SLP_Ade` worker's own no-data
guard (§2.4), which catches the cases the engine reports as success but with no usable output.

---

## 2. The `SLP_Ade/` workflow (new subsystem)

`SLP_Ade/` is an entirely new fan-out/fan-in pipeline for large parameter sweeps on a
SLURM cluster. Python never simulates anything — it expands a config into independent
tasks, runs each as an array element, and reassembles the outputs.

```
config.py            CONFIG: templates × climate sets × transport variants × runs
      │
generate_tasks.py    cartesian product → tasks.json                     [FAN-OUT]
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
- **String-key strategy.** Config stores JSON-serialisable **string keys** into the
  `lpgdata.*` catalogs rather than objects. Household templates (plain strings in
  `lpgdata`) are keyed by their Python attribute name; the `JsonReference` catalogs
  (locations, temperature profiles, transport sets) are keyed by their `.Name` reference
  string (e.g. `lpgdata.GeographicLocations.Germany_Berlin.Name` → `"(Germany) Berlin"`).
  `collect_lpg_references_by_name()` in [simulation.py](simulation.py) resolves a `.Name`
  back to the **full `JsonReference`** (Name **and** Guid), so the exact catalog object
  reaches the LPG request. This replaced the earlier `get_attr_key()` reverse-lookup, which
  is gone.
- **Decoupled climate presets — now a dataclass.** `CLIMATE_SET_KEYS` entries are
  **`ClimateSetKey`** (frozen dataclass: `geographic_location_key`,
  `temperature_profile_key`, `tag`), replacing the earlier `(geo, temp, tag)` tuples — the
  same treatment `TransportVariantKey` already got, so both swept dimensions read the same
  way and `.tag` / `.geographic_location_key` are named rather than positional. Location and
  temperature profile stay independent (matching §1.1); `None` still means "all
  combinations". The consumers were updated in lockstep: `make_climate_variants()` in
  [simulation.py](simulation.py) and the fan-out loop in
  [generate_tasks.py](generate_tasks.py) iterate `ClimateSetKey` fields instead of unpacking
  a tuple.
- **Runs per combination.** `RUNS_PER_COMBO_MAP` + `get_runs_for_combo(combo_tag)` decide
  how many stochastic repeats each combination gets (pattern match on the combo tag, with
  a default fallback), so transport variants can be sampled more heavily than baselines.
- **One `RUN_ON_CLUSTER` flag switches machines.** A single boolean selects every
  environment-specific value at once, so moving between a laptop and the cluster is a
  one-line change:
  - **Output base.** `BASE_OUTPUT_DIR` resolves to `CLUSTER_BASE_OUTPUT_DIR` (shared project
    storage, outside the repo) when `RUN_ON_CLUSTER` is `True`, else `LOCAL_BASE_OUTPUT_DIR`
    (the repo root). `$LPG_OUTPUT_DIR` overrides it in either mode. Everything else derives
    from this one knob (see the output-path bullet below).
  - **Binary path.** `LPG_BINARY_PATH` selects between `CLUSTER_LPG_BINARY_PATH` (the
    `linux-x64/publish` build) and `LOCAL_LPG_BINARY_PATH` (the `win-x64/publish` build) off
    the same flag, replacing the earlier single hard-coded path with a commented alternative.
- **Single output knob → derived subdirs.** `BASE_OUTPUT_DIR` is the *only* output path
  anyone sets; the two dirs every script uses derive from it:
  - `TASK_OUTPUT_DIR = BASE_OUTPUT_DIR / "tasks"` — temporary per-task `task_<NNNNNN>.h5`
    files ([run_task.py](run_task.py) writes them, [merge_results.py](merge_results.py)
    reads and deletes them).
  - `MERGED_OUTPUT_DIR = BASE_OUTPUT_DIR / "multi_runs_output"` — the final merged
    per-template files + `runs_metadata.csv` (merge step and sequential runner).

  Because both derive from one value (honouring `$LPG_OUTPUT_DIR`), the array worker that
  *writes* task files and the interactive merge that *reads* them can never look in different
  directories — the failure mode where a `submit_array.sh` `export` was invisible to a
  login-shell merge. This replaced the earlier split `OUTPUT_DIR` / `SLURM_OUTPUT_DIR`
  constants. **Directories are created at point of use** (`mkdir(parents=True,
  exist_ok=True)`), never at import, so importing config on a laptop never tries to create a
  cluster path or drops stray dirs into the repo.
- **Full training set.** `HOUSEHOLD_TEMPLATE_KEYS` is now ten representative archetypes
  spanning the demographic space (size 1→6, working/non-working, young/retired, with/without
  children, single parent, student, multigenerational). With three climate sets and the
  transport variants' run counts, total tasks = `10 × 3 × (1 + 3) = 120`.
- **Live cluster-run values (currently committed).** Two config knobs are set for a real
  full-scale run, not a smoke test — worth knowing when reading the repo and before running
  locally:
  - `RUN_ON_CLUSTER = True` — output base and binary path both resolve to their **cluster**
    values (§2.1 flag bullet). Flip to `False` for a laptop run.
  - `END_DATE = "2020-12-31"` — the simulation window is now a **full calendar year**
    (was a 31-day January window), matching the DATASET docs' "full calendar year" profiles
    (§3). This is what drives the ~1.5 GB-per-template output sizes.

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
  - **Idle-mode is always on here** (`enable_idle_mode=True`, hard-coded). The sweep prefers
    a completed run with a minor artifact over losing every child-bearing-household task to a
    `DataIntegrityException` (§1.8). The docstring records the observed impact and trade-off
    and points at the core parameter for the full rationale.
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
root, one entry per independent run.

- **String-key-only manifest.** Each task stores only string keys into the `lpgdata.*`
  catalogs, keeping `tasks.json` fully JSON-serialisable; the worker resolves keys back to
  objects at runtime.
- **Deterministic seeding.** `_deterministic_seed(combo_tag, run_idx)` derives a 31-bit
  seed from `MD5("<combo_tag>_<run_idx>")`, so the manifest is **reproducible** — the same
  config always yields the same seeds regardless of when/where it is generated. (Contrast
  with the sequential runner in [simulation.py](simulation.py), which uses a time-based
  seed for interactive exploration.)
- **No separate count file.** `submit_array.sh` derives its `--array` range directly from
  `len(tasks.json)`, so the manifest is the single source of truth for the task count
  (no manual, drift-prone edit).

### 2.4 `run_task.py` — the array worker

[run_task.py](run_task.py) runs one task: it reads `tasks.json[N]` (N from `--task-id`,
defaulting to `$SLURM_ARRAY_TASK_ID`), resolves string keys back to `lpgdata` objects, and
calls `run_lpg_simulation()`.

- **Per-task isolation.** It passes `calculation_index=task_id`, so concurrent array
  elements never share a `C<idx>` working directory. `clear_previous_calc=True` guarantees
  a clean dir if a task id is requeued.
- **One file per task.** Each task writes a single `TASK_OUTPUT_DIR/task_<NNNNNN>.h5`
  (i.e. `<base>/tasks/`; `/data/<data_type>` + `/metadata`), so there are **zero concurrent
  HDF5 write conflicts**. The directory is the derived `TASK_OUTPUT_DIR` from config (§2.1),
  overridable via `$LPG_OUTPUT_DIR`. When flexibility is enabled, the flexibility event log
  rides along as a `/data/FlexibilityEvents` group (§1.5), so the generic `/data/*` copy in
  the merge step (§2.5) carries it through with no special-casing.
- **No-data guard — never write a file that looks complete but isn't.** Two distinct
  no-data outcomes are both caught before the HDF5 write:
  - `df is None` — the engine wrote no `results/Results` directory at all (paired with the
    exit-code check in §1.9).
  - `df.empty` — the directory existed but held no `Sum.*.json` profiles: a **silent,
    exit-0 empty run** (observed occasionally on transport tasks). Without this guard the
    task would be saved as a metadata-only file that looks successful to the merge step.
- **Error handling via exceptions, not `sys.exit` scattered mid-code.** A dedicated
  `NoResultsError(RuntimeError)` is raised for the no-data case; `main()` raises
  `FileNotFoundError` when `tasks.json` is missing and `IndexError` when the task id is out
  of range (replacing inline `sys.exit(...)` calls, and clearing the `#TODO: replace
  sys.exit with exception` note). The single process-boundary `try/except` in `__main__`
  translates **exactly those anticipated failures** into a one-line stderr message + `exit 1`
  (which SLURM records as a failed array task), while any *unexpected* exception is left to
  propagate as a full traceback — more useful than a terse message in cluster logs.

### 2.5 `merge_results.py` — fan-in

[merge_results.py](merge_results.py) assembles all per-task files from `TASK_OUTPUT_DIR`
(`<base>/tasks/`) into per-template HDF5 files under `MERGED_OUTPUT_DIR`
(`<base>/multi_runs_output/`), reproducing the sequential layout
`/<climate_tag>/<transport_tag>/run_<N>/<data_type>` (+ `_metadata`). Both paths are the
derived config values (§2.1), so this reader can never diverge from where the workers wrote.
It also:

- writes `runs_metadata.csv` (same dir) summarising every merged run,
- **reports missing tasks** — any `task_id` present in `tasks.json` but lacking an output
  file is listed, so failed/incomplete array elements are visible, and
- **deletes the per-task files after a successful merge.** The task files are temporary:
  once every one has been folded into the merged files they are removed, so nothing
  accumulates outside the merged output (the now-empty `tasks/` dir is dropped too, best
  effort). Only files that were actually merged are deleted — anything skipped (bad name /
  unknown task id) is left in place for inspection — and deletion happens only after the
  merge loop finishes without raising, so the merged files are complete on disk first. Pass
  **`--keep-tasks`** to retain them. To support the flag, the body was split into a
  `merge_all(keep_tasks=False)` worker and a thin `argparse` `main()`.

### 2.6 `submit_array.sh` — self-resubmitting batch script

[submit_array.sh](submit_array.sh) is a thin SLURM wrapper with several notable design
points:

- **Auto-ranged array via a self-resubmit bootstrap.** `--array` is deliberately **not** a
  `#SBATCH` directive (SLURM parses those before the script body runs, so it cannot read a
  file). Instead, when launched with no `$SLURM_ARRAY_TASK_ID`, the script counts the
  entries in `tasks.json` and re-submits itself with
  `--array=0-(N-1)%MAX_CONCURRENT` (`MAX_CONCURRENT` caps concurrency, default 50).
- **Login-node binary pre-fetch.** Before submitting, the bootstrap imports
  `_lpg_binary_details_for_platform` (§1.3) and downloads the LPG binary once on the login
  node if missing — otherwise the first wave of concurrent tasks would all race to
  download into `pylpg/` and corrupt the folder.
- **Scratch wiring.** Output location is *not* exported here — the single source of truth is
  `BASE_OUTPUT_DIR` in [config.py](config.py) (§2.1), which both the worker and the merge
  import; the `export LPG_OUTPUT_DIR=…` line is left commented, precisely because an export
  in this batch script is invisible to an interactive login-node merge. What it *does*
  export is `LPG_WORK_DIR` (base for the `C<task_id>` calc dirs), pointed at node-local
  scratch to keep each run's result I/O off shared storage.
- **Shared completion log.** Each array element runs on a compute node, so its finish line
  only reaches that task's own `logs/task_%A_%a.out` — never the login-node terminal, and
  watching N per-task files is impractical. Every task now *also* appends its finish line
  (task id, job id, exit code, timestamp) to a single shared `logs/completion.log` under an
  `flock` (fd 9 opened append-mode so the lock never truncates), so concurrent appends don't
  interleave and progress can be watched live with `tail -f logs/completion.log`.

---

## 3. Supporting changes

- **`requirements.txt`** — added `tables` (PyTables). Required for the HDF5 output in
  `SLP_Ade/`; without it, `pd.HDFStore(...)` calls fail.
- **`.gitignore`** — now ignores `pyLPG_env/`, `SLP_Ade/__pycache__/`, the generated
  `tasks.json`, the `multi_runs_output/` output directory, `/tasks/` (the local-mode
  temporary per-task files — normally deleted by the merge, but ignored in case a merge is
  interrupted), and `logs/` (the SLURM per-task `.out` files and the shared
  `completion.log` from §2.6).
- **Dataset documentation.** [DATASET.md](DATASET.md) and its German twin
  [DATASET.de.md](DATASET.de.md) describe the **generated HDF5 dataset** for the currently
  committed config: the ten per-template files (~1.5 GB each, ≈15.7 GB total), the
  `/<climate>/<transport>/run_<N>/<data_type>` group layout, the load types and
  flexibility/`NoFlex`/event data types, `runs_metadata.csv`, and read instructions
  (PyTables, `blosc`-9 `fixed` format). These are **data-consumer-facing** docs (how to read
  the output), distinct from this changelog (how the code got there) and the README (how to
  run it). They describe the full-calendar-year, 120-run sweep, so they must be kept in step
  with the config knobs in §2.1 if the sweep shape changes.
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

## 4. Open issues, TODOs, and remarks

Living backlog for whoever picks this branch up next. Kept alongside the change record so the
"what's left" travels with the "what changed". Line numbers are approximate — grep the marker
text if they have drifted.

### 4.1 Open `TODO` markers in the code

Two remaining, independent of each other. None block a run.

- **~~Drop `get_attr_key()`; store the `JsonReference` string directly~~** — *Done.* Config
  now stores each location/temperature/transport set as its `JsonReference.Name` string
  (`CLIMATE_SET_KEYS` in [config.py](config.py)), the manifest carries those `.Name`
  strings, and both the worker ([run_task.py](run_task.py)) and the sequential runner
  ([simulation.py](simulation.py)) resolve them back to the full reference via
  `collect_lpg_references_by_name()`. `get_attr_key()` was removed. Household templates stay
  keyed by attribute name (they are plain strings, not `JsonReference`s), so their `getattr`
  resolve is unchanged.
- **Simplify deterministic seeding** — [generate_tasks.py](generate_tasks.py#L50):
  `_deterministic_seed()` hashes `MD5("<combo_tag>_<run_idx>")`. The TODO suggests just using
  `run_idx` as the seed. ⚠️ Not a free swap: the current hash makes seeds **distinct across
  combos** (two combos' `run_0` differ); a bare `run_idx` would give every combo the *same*
  seed sequence. Decide whether cross-combo seed independence matters before simplifying.
- **Turn the binary-path check into a raising validator** —
  [simulation.py](simulation.py#L322): the note proposes replacing the current
  path-existence handling with a `check_lpg_binary_source()` that raises explicitly on a
  missing path, instead of the softer current behaviour. Aligns with the exception-first
  error handling already adopted in [run_task.py](run_task.py) (§2.4) and
  `execute_lpg_binaries()` (§1.9).

### 4.2 Larger follow-ups (design, not markers)

- **`HOUSETYPE` is still a scalar.** Templates, climate sets, and transport variants all
  iterate over key lists, but the house type is a single value in [config.py](config.py).
  Making it a swept dimension would mean: iterate house-type keys in
  [generate_tasks.py](generate_tasks.py), resolve the key back in [run_task.py](run_task.py),
  and accept the house type as a parameter in [simulation.py](simulation.py).
- **Root-cause the silent empty transport runs.** The `df.empty` guard (§2.4) currently
  *tolerates* exit-0 runs that produced no `Sum.*.json` profiles (seen on some transport
  tasks) by failing the task cleanly. Why the engine reports success with no output is not yet
  understood — worth investigating before treating the guard as the final answer, since these
  tasks are silently dropped from the merged dataset (they surface only in
  `merge_results.py`'s missing-task report).

### 4.3 Operational remarks / caveats

- **The committed config is a live cluster run.** `RUN_ON_CLUSTER = True` and a full-year
  `END_DATE` are checked in (§2.1). A laptop run needs `RUN_ON_CLUSTER = False`; leaving it
  `True` points output/binary paths at cluster locations that will not exist locally.
- **Idle-mode is a deliberate accuracy trade-off, applied to every sweep run.** The
  `SLP_Ade` output contains brief "Idle" filler activities wherever the LPG would otherwise
  have dead-ended a child-bearing household (§1.8 / §2.2). This is by design (completeness
  over a rare artifact) but is a property of the dataset consumers should know — noted here
  so it is not mistaken for a bug later. The core function still defaults idle-mode `False`.
- **Binary + db3 are read live on the cluster.** Since §1.6 removed the per-calc copy, the
  `LPG_BINARY_PATH` build and shared read-only `profilegenerator.db3` are read on every run;
  they should sit on reasonably fast cluster storage (§1.6 cluster caveat).
- **Keep the three doc surfaces in step.** README = how to run; this CHANGELOG = how/why the
  code changed; [DATASET.md](DATASET.md)/[DATASET.de.md](DATASET.de.md) = how to read the
  output. A change to the sweep shape (templates, climate/transport sets, run counts, date
  range) touches all three — the DATASET docs in particular hard-code the "120 runs / ten
  templates / full year" numbers.
