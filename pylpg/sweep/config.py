"""Configuration for the multi-simulation sweep.

All tunable parameters for the parameter sweep live here, isolated from the
execution logic in ``simulation.py``.  ``generate_tasks.py``, ``run_task.py``
and the sequential runner all import from this single source of truth, so the
SLURM task manifest and the local runner can never drift apart.

To change what gets simulated, edit the values under ``# ---- CONFIG ----``.

For a stripped-down starting point, copy ``examples/sweep_config_minimal.py``
over this file: it defines the same names with the smallest sweep that still
runs (one template, one climate, one transport variant, one run).
"""

import os
from pathlib import Path
import inspect
from typing import Optional

from pylpg import lpgdata
from pylpg.sweep.keys import ClimateSetKey, TransportVariantKey


# --- Output paths -------------------------------------------------------------
# Flip ONE flag to move between cluster and local runs:
#   RUN_ON_CLUSTER = True  -> results go to the shared project storage on the
#                             cluster (CLUSTER_BASE_OUTPUT_DIR below).
#   RUN_ON_CLUSTER = False -> local testing: results go into the repo's own
#                             multi_runs_output/ folder (base = repo root).
# Everything else derives from the chosen base, so this single flag is all you
# change to switch machines.
RUN_ON_CLUSTER = True

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Cluster: shared, fast project storage (outside the repo). Set this to your own
# output location, or override it at runtime via the LPG_OUTPUT_DIR env var.
CLUSTER_BASE_OUTPUT_DIR = Path("/path/to/cluster/output")
# Local testing: use the repo root as the base, so merged files land in
# <repo>/multi_runs_output/ (exactly where local runs wrote before) and the
# temporary <repo>/tasks/ dir sits alongside it (gitignored, and removed by
# merge_results.py after each successful merge).
LOCAL_BASE_OUTPUT_DIR = _REPO_ROOT

# BASE_OUTPUT_DIR is the single knob every script derives its subdirectories
# from. LPG_OUTPUT_DIR overrides it (in either mode) for one-off runs -- applied
# to EVERY script at once (the array worker that writes task files AND the
# interactive merge that reads them), so writer and reader can never look in
# different directories. If you export it, export it in every shell you use (the
# submit_array.sh job AND the shell you run merge_results.py in), otherwise that
# script falls back to the default selected by RUN_ON_CLUSTER here.
#
# Layout created on demand under BASE_OUTPUT_DIR:
#   tasks.json          the task manifest written by generate_tasks.py and read
#                       by run_task.py + merge_results.py.
#   tasks/              per-task task_<NNNNNN>.h5 files written by run_task.py.
#                       These are temporary: merge_results.py folds them into the
#                       merged files and then deletes them.
#   multi_runs_output/  final merged <template>.h5 files + runs_metadata.csv,
#                       written by merge_results.py and by the sequential runner.
BASE_OUTPUT_DIR = Path(
    os.environ.get("LPG_OUTPUT_DIR")
    or (CLUSTER_BASE_OUTPUT_DIR if RUN_ON_CLUSTER else LOCAL_BASE_OUTPUT_DIR)
)

# The generated task manifest. It lives under BASE_OUTPUT_DIR like every other
# sweep artefact rather than next to this module, because this module ships
# inside the installed pylpg package -- a generated file has no business being
# written there. Generator and both readers import this one name, so they can
# never disagree about where the manifest is.
TASKS_FILE = BASE_OUTPUT_DIR / "tasks.json"

# Temporary per-task files: run_task.py writes one HDF5 per SLURM array task
# here; merge_results.py reads them and deletes them after a successful merge.
TASK_OUTPUT_DIR = BASE_OUTPUT_DIR / "tasks"

# Final merged output: one HDF5 per household template plus runs_metadata.csv.
# Shared by merge_results.py and the sequential runner in simulation.py.
MERGED_OUTPUT_DIR = BASE_OUTPUT_DIR / "multi_runs_output"

# NOTE: directories are created at their point of use (mkdir(parents=True,
# exist_ok=True)), never at import time -- importing this config on a laptop must
# not try to create a cluster path, and must not drop stray dirs into the repo.


# Output format options
SAVE_CSV = False  # Save individual CSV files per run
SAVE_HDF5 = True  # Save runs to HDF5 files (one file per household template)


# ---- CONFIG ------------------------------------------------------------------------------------------------------------------------------------------
YEAR = 2022

# Simulation date range as ISO "YYYY-MM-DD" strings. Both MUST be set before
# running: they are left as None on purpose so that run_lpg_simulation raises a
# ValueError if the date range is never addressed, rather than silently falling
# back to a hardcoded window.
START_DATE: Optional[str] = "2020-01-01"  # e.g. "2020-01-01"
END_DATE: Optional[str] = "2020-12-31"    # e.g. "2020-01-31"

# The first training set covered these 10 representative archetypes with the
# full sweep (3 climates x 2 transport variants x multiple runs). Their merged
# .h5 files already exist in the output dir, so the flat runs skip them.
DONE_TEMPLATE_KEYS = [
    "CHR01_Couple_both_at_Work",
    "CHR05_Family_3_children_both_with_work",
    "CHR07_Single_with_work",
    "CHR08_Single_woman_2_children_with_work",
    "CHR13_Student_with_Work",
    "CHR15_Multigenerational_Home_working_couple_2_children_2_seniors",
    "CHR16_Couple_over_65_years",
    "CHR18_Family_2_children_parents_without_work",
    "CHR23_Single_man_over_65_years",
    "CHR27_Family_both_at_work_2_children",
]

# Flat runs: every REMAINING household template gets exactly ONE run with the
# single fixed climate + transport below (Berlin, no-transport baseline).
# Computed as "all templates minus the 10 already done" so it stays correct if
# the catalog changes; inspect.getmembers is sorted by name, so the resulting
# order (and hence task ids) is deterministic. Total tasks =
# len(HOUSEHOLD_TEMPLATE_KEYS) x 1 climate x 1 transport x 1 run = 56.
# Set to None to use all templates in lpgdata.HouseholdTemplates.
HOUSEHOLD_TEMPLATE_KEYS = [
    name
    for name, value in inspect.getmembers(lpgdata.HouseholdTemplates)
    if not name.startswith("_")
    and isinstance(value, str)
    and name not in DONE_TEMPLATE_KEYS
]

# Climate presets keep geographic location and temperature profile separate.
# Flat runs use a SINGLE fixed climate (Berlin). The Hamburg and
# Chemnitz/Dresden presets from the first training set are intentionally dropped
# here so each template gets exactly one run.
# (geographic_location_key, temperature_profile_key, tag)
CLIMATE_SET_KEYS = [
    ClimateSetKey(
        lpgdata.GeographicLocations.Germany_Berlin.Name,
        lpgdata.TemperatureProfiles.Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de.Name,
        "berlin_loc_berlin_temp",
    ),
]
# Set to None to generate all location/temperature-profile combinations.

# Key-based transport presets.
# Flat runs use only the no-transport baseline (pure residential load), so each
# template is a single run. The EV/home-charging variant from the first
# training set is intentionally dropped here.
# When a variant enables transport, give each set as its ``.Name`` string (e.g.
# ``lpgdata.ChargingStationSets.Charging_At_Home_with_11_kW.Name``), exactly like
# CLIMATE_SET_KEYS above. The flat runs use the no-transport baseline, so every
# set key is None here.
TRANSPORT_VARIANT_KEYS = [
    TransportVariantKey(False, None, None, None, "no_transport"),
]

HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling

#: Custom binary path for LPG. The RUN_ON_CLUSTER flag selects between the two
#: builds below (Linux on the cluster, Windows locally). Set each to the path of
#: your own built SimEngine2 binary, or leave it as None to use the official
#: release downloaded automatically by the package.
CLUSTER_LPG_BINARY_PATH = None  # e.g. "/path/to/linux-x64/publish/SimEngine2"; None -> auto-download
LOCAL_LPG_BINARY_PATH = None    # e.g. r"C:\path\to\win-x64\publish\SimEngine2.exe"; None -> auto-download
LPG_BINARY_PATH = CLUSTER_LPG_BINARY_PATH if RUN_ON_CLUSTER else LOCAL_LPG_BINARY_PATH

# Define runs per combination. You can specify:
# - A dict mapping combo_tag patterns to run counts
# - Or use a function to determine runs based on parameters
RUNS_PER_COMBO_MAP = {
    "no_transport": 1,           # Baseline: 1 run only
    "home_charge_bus_cars_30km": 3,  # Transport variants: 3 runs
}


def get_runs_for_combo(combo_tag: str) -> int:
    """Determine the number of runs for a given combination tag.

    Looks up the combo_tag in RUNS_PER_COMBO_MAP to find matching patterns.
    Returns the configured number of runs, or a default of 2 if no pattern matches.

    :param str combo_tag: The combination tag to look up.
    :return int: Number of runs for this combination.
    """
    for pattern, runs in RUNS_PER_COMBO_MAP.items():
        if pattern in combo_tag:
            return runs
    return 2  # Default fallback: 2 runs for unmapped combinations
# ---- END CONFIG ------------------------------------------------------------------------------------------------------------------------------------------
