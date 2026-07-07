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


# Output directory for the sequential (non-SLURM) runner.
OUTPUT_DIR = Path("multi_runs_output")
OUTPUT_DIR.mkdir(exist_ok=True)


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
        tag: Human-readable tag for this variant.
    """
    simulate_transportation: bool
    charging_set_key: str
    transport_device_set_key: str
    travel_route_set_key: str
    tag: str                # TODO: evaluate need for this tag


# ---- CONFIG ------------------------------------------------------------------------------------------------------------------------------------------
YEAR = 2022

# Set to None to use all templates in lpgdata.HouseholdTemplates.
HOUSEHOLD_TEMPLATE_KEYS = [
    get_attr_key(lpgdata.HouseholdTemplates, lpgdata.HouseholdTemplates.CHR01_Couple_both_at_Work)
 ]

# Climate presets keep geographic location and temperature profile separate.
# (geographic_location_key, temperature_profile_key, tag)
CLIMATE_SET_KEYS = [            # TODO: make this a dataclass instead of a tuple for clarity
    (
        #lpgdata.GeographicLocations.Germany_Berlin.Name,        # TODO: remove get_attr_key() and use string from JSONReference
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Berlin),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "berlin_loc_berlin_temp",       
    ),
    (
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Hamburg),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Hamburg_Germany_2007_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "hamburg_loc_hamburg_temp",
    ),
    (
        get_attr_key(lpgdata.GeographicLocations, lpgdata.GeographicLocations.Germany_Chemnitz),
        get_attr_key(lpgdata.TemperatureProfiles, lpgdata.TemperatureProfiles.Dresden_Germany_2000_from_Deutscher_Wetterdienst_DWD_www_dwd_de),
        "chemnitz_loc_dresden_temp",
    ),
]
# Set to None to generate all location/temperature-profile combinations.

# Key-based transport presets.
TRANSPORT_VARIANT_KEYS = [      #TODO: see above
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

#: Custom binary path for LPG. Set to None to use the official release downloaded automatically by the package.
LPG_BINARY_PATH = "/fast/home/a-tarasenko/SLP_Ade/LoadProfileGenerator/SimEngine2/bin/release/net9.0/linux-x64/publish/SimEngine2"
# "pylpg/LPG_win" for local testing

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
