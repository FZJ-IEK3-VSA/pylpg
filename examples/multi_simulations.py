"""
Multi-run LPG example template

What this script does
- Runs multiple LPG simulations for each household template selected by
    `HOUSEHOLD_TEMPLATE_KEYS`.
- For each template it iterates over `CLIMATE_SET_KEYS` and
    `TRANSPORT_VARIANT_KEYS`.
- For each (template, climate, transport) combination it runs
  `RUNS_PER_COMBO` independent simulations with different random seeds to
  inspect stochastic variability.

Generic collector idea
- `collect_lpg_members(...)` can collect all predefined members of a given
    type from any LPG static class via introspection (inspect).
- This is used for templates, geographic locations, temperature profiles and
    transport sets, so lists do not need to be manually copied from `lpgdata`.

Configuration
- `HOUSEHOLD_TEMPLATE_KEYS`: template names from `lpgdata.HouseholdTemplates`.
  Set to `None` to run all available templates.
- `CLIMATE_SET_KEYS`: tuples of
    `(geographic_location_key, temperature_profile_key, tag)`.
    This keeps LPG's geographic location and weather profile separate, while
    still letting you define meaningful paired presets. Set to `None` to run
    all possible geographic-location/temperature-profile combinations.
- `TRANSPORT_VARIANT_KEYS`: `TransportVariantKey` entries with key names for
    LPG transport sets. Keys are resolved against the corresponding
    `lpgdata.*Sets` classes.
- `RUNS_PER_COMBO`: number of different seeds per parameter combination.

Outputs
- Per-run CSV files are written to `multi_runs_output`.
- `runs_metadata.csv` summarizes all successful runs.

Run
    python examples/multi_simulations.py
"""

from pathlib import Path
from dataclasses import dataclass
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


def make_climate_variants(
    all_geographic_locations: Dict[str, JsonReference],
    all_temperature_profiles: Dict[str, JsonReference],
    climate_keys: Optional[list[tuple[str, Optional[str], str]]],
) -> list[tuple[JsonReference, Optional[JsonReference], str]]:
    if climate_keys is None:
        return [
            (
                location,
                temperature_profile,
                f"{location_key}__{temperature_key}",
            )
            for location_key, location in all_geographic_locations.items()
            for temperature_key, temperature_profile in all_temperature_profiles.items()
        ]

    variants = []
    for location_key, temperature_key, tag in climate_keys:
        location = resolve_optional_key(
            all_geographic_locations, location_key, "geographic location"
        )
        if location is None:
            raise KeyError("Climate variants require a geographic location key")
        temperature_profile = resolve_optional_key(
            all_temperature_profiles, temperature_key, "temperature profile"
        )
        variants.append((location, temperature_profile, tag))
    return variants


@dataclass(frozen=True)
class TransportVariantKey:
    simulate_transportation: bool
    charging_set_key: Optional[str]
    transport_device_set_key: Optional[str]
    travel_route_set_key: Optional[str]
    tag: str


@dataclass(frozen=True)
class TransportVariant:
    simulate_transportation: bool
    charging_set: Optional[JsonReference]
    transport_device_set: Optional[JsonReference]
    travel_route_set: Optional[JsonReference]
    tag: str


def make_transport_variants(
    all_charging_sets: Dict[str, JsonReference],
    all_transport_device_sets: Dict[str, JsonReference],
    all_travel_route_sets: Dict[str, JsonReference],
    variant_keys: list[TransportVariantKey],
) -> list[TransportVariant]:
    return [
        TransportVariant(
            simulate_transportation=variant_key.simulate_transportation,
            charging_set=resolve_optional_key(
                all_charging_sets, variant_key.charging_set_key, "charging set"
            ),
            transport_device_set=resolve_optional_key(
                all_transport_device_sets,
                variant_key.transport_device_set_key,
                "transport device set",
            ),
            travel_route_set=resolve_optional_key(
                all_travel_route_sets,
                variant_key.travel_route_set_key,
                "travel route set",
            ),
            tag=variant_key.tag,
        )
        for variant_key in variant_keys
    ]


# ---- CONFIG ----
YEAR = 2022

# Set to None to use all templates in lpgdata.HouseholdTemplates.
HOUSEHOLD_TEMPLATE_KEYS = [
    "CHR01_Couple_both_at_Work",
    "CHR03_Family_1_child_both_at_work",
]

# Climate presets keep geographic location and temperature profile separate.
# (geographic_location_key, temperature_profile_key, tag)
CLIMATE_SET_KEYS = [
    (
        "Germany_Berlin",
        "Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de",
        "berlin_loc_berlin_temp",
    ),
    (
        "Germany_Hamburg",
        "Hamburg_Germany_2007_from_Deutscher_Wetterdienst_DWD_www_dwd_de",
        "hamburg_loc_hamburg_temp",
    ),
    (
        "Germany_Chemnitz",
        "Dresden_Germany_2000_from_Deutscher_Wetterdienst_DWD_www_dwd_de",
        "chemnitz_loc_dresden_temp",
    ),
]
# Set to None to generate all location/temperature-profile combinations.

# Key-based transport presets.
TRANSPORT_VARIANT_KEYS = [
    TransportVariantKey(False, None, None, None, "no_transport"),
    TransportVariantKey(
        True,
        "Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity",
        "Bus_and_two_30_km_h_Cars",
        "Travel_Route_Set_for_30km_Commuting_Distance",
        "home_charge_bus_cars_30km",
    ),
]

HOUSETYPE = lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling
LPG_BINARY_PATH = None

# Define runs per combination. You can specify:
# - A dict mapping combo_tag patterns to run counts
# - Or use a function to determine runs based on parameters
RUNS_PER_COMBO_MAP = {
    "no_transport": 1,           # Baseline: 1 run only
    "home_charge_bus_cars_30km": 3,  # Transport variants: 3 runs
}

def get_runs_for_combo(combo_tag: str) -> int:
    """Determine number of seeds for this parameter combination."""
    for pattern, runs in RUNS_PER_COMBO_MAP.items():
        if pattern in combo_tag:
            return runs
    return 2  # Default fallback: 2 runs for unmapped combinations

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
    all_temperature_profiles = collect_lpg_members(
        lpgdata.TemperatureProfiles, JsonReference
    )
    all_charging_sets = collect_lpg_members(lpgdata.ChargingStationSets, JsonReference)
    all_transport_device_sets = collect_lpg_members(
        lpgdata.TransportationDeviceSets, JsonReference
    )
    all_travel_route_sets = collect_lpg_members(lpgdata.TravelRouteSets, JsonReference)

    household_templates = select_by_keys(
        all_templates, HOUSEHOLD_TEMPLATE_KEYS, "household template"
    )
    climate_sets = make_climate_variants(
        all_geographic_locations,
        all_temperature_profiles,
        CLIMATE_SET_KEYS,
    )

    transport_variants = make_transport_variants(
        all_charging_sets,
        all_transport_device_sets,
        all_travel_route_sets,
        TRANSPORT_VARIANT_KEYS,
    )

    meta_rows = []
    total = 0

    for tmpl in household_templates:
        tmpl_name = tmpl or "template"
        for geographic_location, temperature_profile, climate_tag in climate_sets:
            climate_name = climate_tag
            for transport_variant in transport_variants:
                combo_tag = (
                    f"{safe_name(tmpl_name)}__{safe_name(climate_name)}__"
                    f"{transport_variant.tag}"
                )

                # Determine number of seeds for this combination
                num_runs = get_runs_for_combo(combo_tag)
                
                # Multiple seeds for identical non-seed parameters.
                for run_idx in range(num_runs):
                    seed = int(time.time() * 1000) % 2**31
                    seed += run_idx

                    try:
                        print(
                            f"Running: {combo_tag} seed={seed} "
                            f"(run {run_idx + 1}/{num_runs})"
                        )

                        household = lpgdata.HouseholdData(
                            None,
                            lpgdata.HouseholdTemplateSpecification(
                                HouseholdTemplateName=tmpl,
                            ),
                            None,
                            "hhid",
                            "hhname",
                            transport_variant.charging_set,
                            transport_variant.transport_device_set,
                            transport_variant.travel_route_set,
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
                            geographic_location=geographic_location,
                            temperature_profile=temperature_profile,
                            enable_flexibility=False,
                            enable_transportation=transport_variant.simulate_transportation,
                            random_seed=seed,
                            energy_intensity=EnergyIntensityType.Random,
                            **execute_kwargs,
                        )

                        if df is None:
                            print("No results returned for this run")
                            continue

                        filename_base = f"{combo_tag}__seed{seed}__run{run_idx + 1}"
                        
                        # Save each data type to separate CSV files
                        data_types = {}
                        for col in df.columns:
                            # Extract data type from column name (e.g., "Electricity_HH1" -> "Electricity")
                            data_type = col.rsplit("_", 1)[0]
                            if data_type not in data_types:
                                data_types[data_type] = pd.DataFrame(index=df.index)
                            data_types[data_type][col] = df[col]
                        
                        # Save each data type to its own CSV file
                        for data_type, type_df in data_types.items():
                            out_csv = OUTPUT_DIR / (safe_name(f"{filename_base}__{data_type}") + ".csv")
                            type_df.to_csv(out_csv)
                        
                        print(f"  Saved {len(data_types)} data types: {', '.join(sorted(data_types.keys()))}")

                        meta_rows.append(
                            {
                                "template": tmpl_name,
                                "climate": climate_name,
                                "geographic_location": geographic_location.Name,
                                "temperature_profile": (
                                    temperature_profile.Name
                                    if temperature_profile is not None
                                    else None
                                ),
                                "transport_tag": transport_variant.tag,
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
