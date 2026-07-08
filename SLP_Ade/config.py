"""Configuration for the SLP_Ade multi-simulation sweep.

All tunable parameters for the parameter sweep live here, isolated from the
execution logic in ``simulation.py``.  ``generate_tasks.py``, ``run_task.py``
and the sequential runner all import from this single source of truth, so the
SLURM task manifest and the local runner can never drift apart.

To change what gets simulated, edit the values under ``# ---- CONFIG ----``.
"""

import os
from pathlib import Path
from dataclasses import dataclass
import inspect
from typing import Any, Optional

from pylpg import lpgdata


# --- Output paths -------------------------------------------------------------
# Flip ONE flag to move between cluster and local runs:
#   RUN_ON_CLUSTER = True  -> results go to the shared project storage on the
#                             cluster (CLUSTER_BASE_OUTPUT_DIR below).
#   RUN_ON_CLUSTER = False -> local testing: results go into the repo's own
#                             multi_runs_output/ folder (base = repo root).
# Everything else derives from the chosen base, so this single flag is all you
# change to switch machines.
RUN_ON_CLUSTER = False

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Cluster: shared, fast project storage (outside the repo).
CLUSTER_BASE_OUTPUT_DIR = Path(
    "/fast/central/projects/2026-a-tarasenko-SLP_Ade/first_training_set"
)
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
#   tasks/              per-task task_<NNNNNN>.h5 files written by run_task.py.
#                       These are temporary: merge_results.py folds them into the
#                       merged files and then deletes them.
#   multi_runs_output/  final merged <template>.h5 files + runs_metadata.csv,
#                       written by merge_results.py and by the sequential runner.
BASE_OUTPUT_DIR = Path(
    os.environ.get("LPG_OUTPUT_DIR")
    or (CLUSTER_BASE_OUTPUT_DIR if RUN_ON_CLUSTER else LOCAL_BASE_OUTPUT_DIR)
)

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


def get_attr_key(cls: type, attr_value: Any) -> str:
    """Get the attribute name from a class for a given attribute value.

    :param type cls: The class to search for the attribute.
    :param Any attr_value: The attribute value to find the name for.
    :return str: The attribute name.
    :raises ValueError: If the attribute is not found in the class.
    """
    for name, value in inspect.getmembers(cls):
        if not name.startswith("_") and value is attr_value:
            return name
    raise ValueError(f"Attribute not found in {cls.__name__}")


@dataclass(frozen=True)
class TransportVariantKey:
    """Configuration key for a transport variant.

    Attributes:
        simulate_transportation: Whether to enable transportation simulation.
        charging_set_key: Key for charging station set (or None).
        transport_device_set_key: Key for transportation device set (or None).
        travel_route_set_key: Key for travel route set (or None).
        tag: Short, filesystem-safe identifier for this variant. Load-bearing
            : it is the transport level of the HDF5 output
            hierarchy (``/<climate_tag>/<transport_tag>/run_<N>/...``), the
            substring key that ``RUNS_PER_COMBO_MAP`` / ``get_runs_for_combo()``
            match against to decide the run count, and part of the ``combo_tag``
            used for deterministic seeding.
    """
    simulate_transportation: bool
    charging_set_key: str
    transport_device_set_key: str
    travel_route_set_key: str
    tag: str


@dataclass(frozen=True)
class ClimateSetKey:
    """Configuration key for a climate variant (location + temperature profile).

    Attributes:
        geographic_location_key: Key into ``lpgdata.GeographicLocations``.
        temperature_profile_key: Key into ``lpgdata.TemperatureProfiles``, or
            None to fall back to the location's own default profile.
        tag: Short, filesystem-safe identifier for this variant. Load-bearing,
            exactly like ``TransportVariantKey.tag``: it is the climate level of
            the HDF5 output hierarchy (``/<climate_tag>/<transport_tag>/run_<N>/
            ...``) and part of the ``combo_tag`` used for deterministic seeding.
    """
    geographic_location_key: str
    temperature_profile_key: Optional[str]
    tag: str


# ---- CONFIG ------------------------------------------------------------------------------------------------------------------------------------------
YEAR = 2022

# Simulation date range as ISO "YYYY-MM-DD" strings. Both MUST be set before
# running: they are left as None on purpose so that run_lpg_simulation raises a
# ValueError if the date range is never addressed, rather than silently falling
# back to a hardcoded window.
START_DATE: Optional[str] = "2020-01-01"  # e.g. "2020-01-01"
END_DATE: Optional[str] = "2020-01-31"    # e.g. "2020-01-31"

# Set to None to use all templates in lpgdata.HouseholdTemplates.
# Ten representative archetypes spanning the demographic space (household size
# 1 -> 6, working / non-working, young / retired, with / without children,
# single parent, student, multigenerational). Total tasks = len(templates) x
# len(CLIMATE_SET_KEYS) x (runs summed over TRANSPORT_VARIANT_KEYS) = 10 x 3 x
# (1 + 3) = 120.
HOUSEHOLD_TEMPLATE_KEYS = [
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR01_Couple_both_at_Work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR05_Family_3_children_both_with_work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR07_Single_with_work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR08_Single_woman_2_children_with_work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR13_Student_with_Work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR15_Multigenerational_Home_working_couple_2_children_2_seniors),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR16_Couple_over_65_years),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR18_Family_2_children_parents_without_work),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR23_Single_man_over_65_years),
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR27_Family_both_at_work_2_children),
 ]

# Climate presets keep geographic location and temperature profile separate.
# (geographic_location_key, temperature_profile_key, tag)
CLIMATE_SET_KEYS = [
    ClimateSetKey(
        #lpgdata.GeographicLocations.Germany_Berlin.Name,        # TODO: remove get_attr_key() and use string from JSONReference
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Berlin),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "berlin_loc_berlin_temp",
    ),
    ClimateSetKey(
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Hamburg),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Hamburg_Germany_2007_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "hamburg_loc_hamburg_temp",
    ),
    ClimateSetKey(
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Chemnitz),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Dresden_Germany_2000_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "chemnitz_loc_dresden_temp",
    ),
]
# Set to None to generate all location/temperature-profile combinations.

# Key-based transport presets.
TRANSPORT_VARIANT_KEYS = [      # TODO: remove get_attr_key() and use string from JSONReference (as noted on CLIMATE_SET_KEYS above)
    TransportVariantKey(False, None, None, None, "no_transport"),
    TransportVariantKey(
        True,
        get_attr_key(lpgdata.ChargingStationSets, lpgdata.ChargingStationSets.Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity),
        get_attr_key(lpgdata.TransportationDeviceSets, lpgdata.TransportationDeviceSets.Bus_and_two_30_km_h_Cars),
        get_attr_key(lpgdata.TravelRouteSets, lpgdata.TravelRouteSets.Travel_Route_Set_for_30km_Commuting_Distance),
        "home_charge_bus_cars_30km",
    ),
]

HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling

#: Custom binary path for LPG. The RUN_ON_CLUSTER flag selects between the two
#: builds below (Linux on the cluster, Windows locally). Set the relevant one to
#: None to use the official release downloaded automatically by the package.
CLUSTER_LPG_BINARY_PATH = "/fast/home/a-tarasenko/SLP_Ade/LoadProfileGenerator/SimEngine2/bin/release/net9.0/linux-x64/publish/SimEngine2"
LOCAL_LPG_BINARY_PATH = r"C:\Tarasenko\GitHub\LoadProfileGenerator\SimEngine2\bin\release\net9.0\win-x64\publish\SimEngine2.exe"
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
