"""Minimal working sweep configuration.

This is a TEMPLATE, and the smallest configuration that still produces a
complete sweep: **one** household template x **one** climate x **one**
transport variant x **one** run = a single task. Use it as a starting point
instead of trimming down the full ``pylpg/sweep/config.py``.

Usage
-----
Copy it over the config module the sweep imports, then edit it in place::

    cp examples/sweep_config_minimal.py pylpg/sweep/config.py
    python -m pylpg.sweep.generate_tasks     # -> <base>/tasks.json (1 task)
    python -m pylpg.sweep.run_task --task-id 0
    python -m pylpg.sweep.merge_results

(Keep a copy of the original ``pylpg/sweep/config.py`` first if you want to go
back to the full sweep.)

Every name defined below is imported by ``generate_tasks.py``, ``run_task.py``,
``merge_results.py`` and ``simulation.py``, so all of them must stay defined.
The structural key types come from ``pylpg.sweep.keys`` rather than from the
config module, precisely so this file can import them after replacing it.

Scaling this up
---------------
- more templates -> add names to ``HOUSEHOLD_TEMPLATE_KEYS`` (or set it to
  ``None`` for every template in the catalog)
- more climates -> add ``ClimateSetKey`` entries to ``CLIMATE_SET_KEYS``
- more transport -> add ``TransportVariantKey`` entries with
  ``simulate_transportation=True`` and the relevant ``lpgdata`` set names
- more repeats -> raise the counts in ``RUNS_PER_COMBO_MAP``

The task count is the product of all four.
"""

import os
from pathlib import Path
from typing import Optional

from pylpg import lpgdata
from pylpg.sweep.keys import ClimateSetKey, TransportVariantKey, require_non_empty


# --- Output paths -------------------------------------------------------------
# One knob. Everything else derives from it, so switching machines is a
# one-path change and nothing is ever written into the repo. The
# LPG_OUTPUT_DIR env var overrides it for a single run -- export it in EVERY
# shell of the pipeline (the array job AND the shell running merge_results.py),
# or writer and reader will look in different places.
BASE_OUTPUT_DIR = Path(
    os.environ.get("LPG_OUTPUT_DIR") or Path.home() / "pylpg_sweep_output"
)

# The three artefacts of a sweep. Directories are created at their point of use,
# never at import time.
TASKS_FILE = BASE_OUTPUT_DIR / "tasks.json"            # manifest
TASK_OUTPUT_DIR = BASE_OUTPUT_DIR / "tasks"            # temporary per-task .h5
MERGED_OUTPUT_DIR = BASE_OUTPUT_DIR / "multi_runs_output"  # final per-template .h5


# Output format options
SAVE_CSV = False  # Save individual CSV files per run
SAVE_HDF5 = True  # Save runs to HDF5 files (one file per household template)


# ---- CONFIG ------------------------------------------------------------------
YEAR = 2022

# Simulation date range as ISO "YYYY-MM-DD" strings. Both MUST be set: a None
# here makes run_lpg_simulation raise rather than silently pick a window. One
# week keeps this example fast; widen it for a real run.
START_DATE: Optional[str] = "2020-01-01"
END_DATE: Optional[str] = "2020-01-07"

# Exactly one household template. Values are lpgdata.HouseholdTemplates
# *attribute names*, not the template strings themselves.
# Set to None to sweep every template in the catalog.
HOUSEHOLD_TEMPLATE_KEYS = [
    "CHR01_Couple_both_at_Work",
]

# Exactly one climate. The tag is load-bearing: it becomes the climate level of
# the HDF5 hierarchy (/<climate_tag>/<transport_tag>/run_<N>/...) and part of
# the combo_tag used to name per-run output files, so keep it filesystem-safe.
# Set to None to generate all location/temperature-profile combinations.
CLIMATE_SET_KEYS = [
    ClimateSetKey(
        lpgdata.GeographicLocations.Germany_Berlin.Name,
        lpgdata.TemperatureProfiles.Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de.Name,
        "berlin",
    ),
]

# Exactly one transport variant: the no-transport baseline (pure residential
# load), so every set key is None. To add an EV variant, pass
# simulate_transportation=True plus the .Name of the relevant
# lpgdata.ChargingStationSets / TransportationDeviceSets / TravelRouteSets.
TRANSPORT_VARIANT_KEYS = [
    TransportVariantKey(False, None, None, None, "no_transport"),
]

# Reject selections that would expand to a zero-task sweep. None means "all of
# them" for the first two, but is not an option for TRANSPORT_VARIANT_KEYS --
# its consumers iterate the list directly.
require_non_empty(HOUSEHOLD_TEMPLATE_KEYS, "HOUSEHOLD_TEMPLATE_KEYS",
                  allow_none=True, none_means="sweep every template")
require_non_empty(CLIMATE_SET_KEYS, "CLIMATE_SET_KEYS",
                  allow_none=True, none_means="generate all climate combinations")
require_non_empty(TRANSPORT_VARIANT_KEYS, "TRANSPORT_VARIANT_KEYS", allow_none=False)

HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling

#: Custom LPG binary. None -> use the official release, downloaded on first use.
LPG_BINARY_PATH = None

# How many independent runs (different random seeds) per parameter combination.
# Keys are matched as substrings against the combo_tag.
RUNS_PER_COMBO_MAP = {
    "no_transport": 1,
}


def get_runs_for_combo(combo_tag: str) -> int:
    """Determine the number of runs for a given combination tag.

    Looks up the combo_tag in RUNS_PER_COMBO_MAP to find matching patterns.
    Returns the configured number of runs, or a default of 1 if no pattern matches.

    :param str combo_tag: The combination tag to look up.
    :return int: Number of runs for this combination.
    """
    for pattern, runs in RUNS_PER_COMBO_MAP.items():
        if pattern in combo_tag:
            return runs
    return 1  # Default fallback for unmapped combinations
# ---- END CONFIG --------------------------------------------------------------
