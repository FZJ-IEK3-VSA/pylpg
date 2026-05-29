"""
Multi-run LPG example template

What this script does
- Runs multiple LPG simulations for each household template in
    `HOUSEHOLD_TEMPLATES`.
- For each template it iterates over `WEATHER_SETS` and
    `TRANSPORT_VARIANTS`.
- For each (template, weather, transport) combination it runs
    `RUNS_PER_COMBO` independent simulations with different random seeds to
    inspect stochastic variability.

Configuration:
- `HOUSEHOLD_TEMPLATES`: list of `lpgdata.HouseholdTemplates.*` string constants.
- `WEATHER_SETS`: list of `lpgdata.GeographicLocations.*` (or
    `lpgdata.TemperatureProfiles.*`) JsonReference constants.
- `TRANSPORT_VARIANTS`: list of tuples
    `(simulate_transportation, chargingset, transportation_device_set, travel_route_set, tag)`
    where `chargingset`, `transportation_device_set` and `travel_route_set` are
    `lpgdata.*` JsonReference constants (or `None`). The `tag` is a short
    identifier used in output filenames.
- `RUNS_PER_COMBO`: how many different seeds to run per parameter combination.

Seeding and reproducibility
- The script generates a seed per run (time-based) and offsets it by the
    run index so repeated runs for the same combo get different seeds. To
    run fully reproducible experiments, set `random_seed` explicitly by
    editing the call to `execute_lpg_single_household`.

Outputs
- Per-run CSV files are written to the `multi_runs_output` folder. If
    `Electricity_HH1` exists in the result dataframe it is written; otherwise
    the full dataframe is saved.
- A `runs_metadata.csv` file lists (template, weather, transport_tag, seed,
    run_index, out_file) for all successful runs.

Run
        python examples/multi_simulations.py

"""
from pathlib import Path
import time
import traceback
import pandas as pd

from pylpg import lpg_execution, lpgdata
from pylpg.lpgpythonbindings import EnergyIntensityType, CalcOption


OUTPUT_DIR = Path("multi_runs_output")
OUTPUT_DIR.mkdir(exist_ok=True)


def safe_name(s: str) -> str:
    return (
        s.replace(" ", "_")
        .replace(",", "")
        .replace("/", "_")
        .replace("(", "")
        .replace(")", "")
    )


# ---- CONFIG ----
YEAR = 2022

# list of household templates to run (use lpgdata.HouseholdTemplates)
HOUSEHOLD_TEMPLATES = [
    lpgdata.HouseholdTemplates.CHR01_Couple_both_at_Work,
    lpgdata.HouseholdTemplates.CHR03_Family_1_child_both_at_work,
]

# weather / geographic locations to try (use lpgdata.GeographicLocations)
WEATHER_SETS = [
    lpgdata.GeographicLocations.Germany_Berlin,
    lpgdata.GeographicLocations.Finland_Helsinki,
]

# transport variants: tuples of (simulate_transportation, chargingset, transportation_device_set, travel_route_set, tag)
TRANSPORT_VARIANTS = [
    (False, None, None, None, "no_transport"),
    (
        True,
        lpgdata.ChargingStationSets.Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity,
        lpgdata.TransportationDeviceSets.Bus_and_two_30_km_h_Cars,
        lpgdata.TravelRouteSets.Travel_Route_Set_for_30km_Commuting_Distance,
        "home_charge_bus_cars_30km",
    ),
]

# number of independent seeds to run per (household, weather, transport) combo
RUNS_PER_COMBO = 8  # set between ~10-100 overall as needed

# choose housetype and resolution
HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling
RESOLUTION = "00:15:00"

# optional: path to LPG binary if you want to use a local installation
LPG_BINARY_PATH = None
# -----------------------------------------
# ---- END OF CONFIG ----


