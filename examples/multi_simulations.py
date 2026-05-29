"""
Multi-run LPG example template

What this script does
- Runs multiple LPG simulations for each household template selected by
  `HOUSEHOLD_TEMPLATE_KEYS`.
- For each template it iterates over `WEATHER_SET_KEYS` and
  `TRANSPORT_VARIANT_KEYS`.
- For each (template, weather, transport) combination it runs
  `RUNS_PER_COMBO` independent simulations with different random seeds to
  inspect stochastic variability.

Generic collector idea
- `collect_lpg_members(...)` can collect all predefined members of a given
  type from any LPG static class via introspection (inspect).
- This is used for templates, weather locations and transport sets, so lists
  do not need to be manually copied from `lpgdata`.

Configuration
- `HOUSEHOLD_TEMPLATE_KEYS`: template names from `lpgdata.HouseholdTemplates`.
  Set to `None` to run all available templates.
- `WEATHER_SET_KEYS`: location names from `lpgdata.GeographicLocations`.
  Set to `None` to use all available locations.
- `TRANSPORT_VARIANT_KEYS`: tuples of
  `(simulate_transportation, charging_set_key, transport_device_set_key, travel_route_set_key, tag)`.
  Keys are resolved against the corresponding `lpgdata.*Sets` classes.
- `RUNS_PER_COMBO`: number of different seeds per parameter combination.

Outputs
- Per-run CSV files are written to `multi_runs_output`.
- `runs_metadata.csv` summarizes all successful runs.

Run
    python examples/multi_simulations.py
"""

from pathlib import Path
import inspect
import time
import traceback
from typing import Any, Dict, Iterable, Optional

import pandas as pd

from pylpg import lpg_execution, lpgdata
from pylpg.lpgpythonbindings import EnergyIntensityType, JsonReference


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


def collect_lpg_members(container: Any, expected_type: type) -> Dict[str, Any]:
    """Collect public class members of `container` that match `expected_type`."""
    return {
        name: value
        for name, value in inspect.getmembers(container)
        if not name.startswith("_") and isinstance(value, expected_type)
    }


def select_by_keys(
    available: Dict[str, Any],
    keys: Optional[Iterable[str]],
    label: str,
) -> list[Any]:
    """Select values from `available` by key list, or all values if keys is None."""
    if keys is None:
        return list(available.values())

    selected: list[Any] = []
    for key in keys:
        if key not in available:
            raise KeyError(f"Unknown {label} key: {key}")
        selected.append(available[key])
    return selected


def resolve_optional_key(
    available: Dict[str, JsonReference],
    key: Optional[str],
    label: str,
) -> Optional[JsonReference]:
    if key is None:
        return None
    if key not in available:
        raise KeyError(f"Unknown {label} key: {key}")
    return available[key]


# ---- CONFIG ----
YEAR = 2022

# Set to None to use all templates in lpgdata.HouseholdTemplates.
HOUSEHOLD_TEMPLATE_KEYS = [
    "CHR01_Couple_both_at_Work",
    "CHR03_Family_1_child_both_at_work",
]

# Set to None to use all locations in lpgdata.GeographicLocations.
WEATHER_SET_KEYS = [
    "Germany_Berlin",
    "Finland_Helsinki",
]

# (simulate_transportation, charging_set_key, transport_device_set_key, travel_route_set_key, tag)
TRANSPORT_VARIANT_KEYS = [
    (False, None, None, None, "no_transport"),
    (
        True,
        "Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity",
        "Bus_and_two_30_km_h_Cars",
        "Travel_Route_Set_for_30km_Commuting_Distance",
        "home_charge_bus_cars_30km",
    ),
]

RUNS_PER_COMBO = 8
HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling
LPG_BINARY_PATH = None
# ---- END CONFIG ----


def _print_lpg_binary_source() -> None:
    if LPG_BINARY_PATH is None:
        print("LPG binary source: official release downloaded automatically.")
    else:
        print(f"LPG binary source: custom binary path {LPG_BINARY_PATH}")


def _supports_lpg_binary_path(function: Any) -> bool:
    return "lpg_binary_path" in inspect.signature(function).parameters


def run_all() -> None:
    _print_lpg_binary_source()

    all_templates = collect_lpg_members(lpgdata.HouseholdTemplates, str)
    all_geographic_locations = collect_lpg_members(
        lpgdata.GeographicLocations, JsonReference
    )
    all_charging_sets = collect_lpg_members(lpgdata.ChargingStationSets, JsonReference)
    all_transport_device_sets = collect_lpg_members(
        lpgdata.TransportationDeviceSets, JsonReference
    )
    all_travel_route_sets = collect_lpg_members(lpgdata.TravelRouteSets, JsonReference)

    household_templates = select_by_keys(
        all_templates, HOUSEHOLD_TEMPLATE_KEYS, "household template"
    )
    weather_sets = select_by_keys(
        all_geographic_locations, WEATHER_SET_KEYS, "weather/location"
    )

    transport_variants = [
        (
            simulate_transportation,
            resolve_optional_key(all_charging_sets, charging_key, "charging set"),
            resolve_optional_key(
                all_transport_device_sets, device_set_key, "transport device set"
            ),
            resolve_optional_key(all_travel_route_sets, route_key, "travel route set"),
            tag,
        )
        for (
            simulate_transportation,
            charging_key,
            device_set_key,
            route_key,
            tag,
        ) in TRANSPORT_VARIANT_KEYS
    ]

    meta_rows = []
    total = 0

    for tmpl in household_templates:
        tmpl_name = tmpl or "template"
        for weather in weather_sets:
            weather_name = weather.Name or "weather"
            for (
                simulate_transportation,
                chargingset,
                transportation_device_set,
                travel_route_set,
                ttag,
            ) in transport_variants:
                combo_tag = f"{safe_name(tmpl_name)}__{safe_name(weather_name)}__{ttag}"

                # Multiple seeds for identical non-seed parameters.
                for run_idx in range(RUNS_PER_COMBO):
                    seed = int(time.time() * 1000) % 2**31
                    seed += run_idx

                    try:
                        print(
                            f"Running: {combo_tag} seed={seed} "
                            f"(run {run_idx + 1}/{RUNS_PER_COMBO})"
                        )

                        household = lpgdata.HouseholdData(
                            None,
                            lpgdata.HouseholdTemplateSpecification(
                                HouseholdTemplateName=tmpl,
                            ),
                            None,
                            "hhid",
                            "hhname",
                            chargingset,
                            transportation_device_set,
                            travel_route_set,
                            None,
                            HouseholdDataSpecification=
                            lpgdata.HouseholdDataSpecificationType.ByTemplateName,
                        )

                        execute_kwargs: Dict[str, Any] = {}
                        if _supports_lpg_binary_path(
                            lpg_execution.execute_lpg_with_householddata_custom
                        ):
                            execute_kwargs["lpg_binary_path"] = LPG_BINARY_PATH

                        df = lpg_execution.execute_lpg_with_householddata_custom(
                            YEAR,
                            household,
                            HOUSETYPE,
                            geographic_location=weather,
                            enable_flexibility=False,
                            enable_transportation=simulate_transportation,
                            random_seed=seed,
                            energy_intensity=EnergyIntensityType.Random,
                            **execute_kwargs,
                        )

                        if df is None:
                            print("No results returned for this run")
                            continue

                        filename_base = f"{combo_tag}__seed{seed}__run{run_idx + 1}"
                        out_csv = OUTPUT_DIR / (safe_name(filename_base) + ".csv")

                        if "Electricity_HH1" in df:
                            df["Electricity_HH1"].to_csv(out_csv)
                        else:
                            df.to_csv(out_csv)

                        meta_rows.append(
                            {
                                "template": tmpl_name,
                                "weather": weather_name,
                                "transport_tag": ttag,
                                "seed": seed,
                                "run_index": run_idx + 1,
                                "out_file": str(out_csv),
                            }
                        )
                        total += 1
                    except Exception:
                        print("Run failed:")
                        traceback.print_exc()

    meta_df = pd.DataFrame(meta_rows)
    meta_df.to_csv(OUTPUT_DIR / "runs_metadata.csv", index=False)
    print(
        f"Finished {total} successful runs. "
        f"Metadata in {OUTPUT_DIR / 'runs_metadata.csv'}"
    )


if __name__ == "__main__":
    run_all()
