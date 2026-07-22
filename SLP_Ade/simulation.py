"""Multi-run LPG simulation logic.

What this module does
- Runs multiple LPG simulations for each household template selected by
    `HOUSEHOLD_TEMPLATE_KEYS`.
- For each template it iterates over `CLIMATE_SET_KEYS` and
    `TRANSPORT_VARIANT_KEYS`.
- For each (template, climate, transport) combination it runs
  `RUNS_PER_COMBO` independent simulations with different random seeds to
  inspect stochastic variability.

All tunable parameters live in `config.py`. This module holds the shared
execution primitive `run_lpg_simulation()` plus the sequential (non-SLURM)
runner. The SLURM worker `run_task.py` also calls `run_lpg_simulation()`, so
both execution paths share the exact same primitive.

Generic collector idea
- `collect_lpg_members(...)` can collect all predefined members of a given
    type from any LPG static class via introspection (inspect).
- This is used for templates, geographic locations, temperature profiles and
    transport sets, so lists do not need to be manually copied from `lpgdata`.

Outputs
- Per-run CSV files are written to `multi_runs_output` (if SAVE_CSV=True).
- HDF5 files with hierarchical structure (if SAVE_HDF5=True):
    One file per household template: <template_name>.h5
    Structure within each file: /climate/transport/run_N/data_type
    With flexibility enabled, the data_type groups also include the baseline
    `<LoadType>_NoFlex` profiles and a `FlexibilityEvents` event-log table.
- `runs_metadata.csv` summarizes all successful runs.

Run
    python SLP_Ade/simulation.py
"""

import os
import sys
from pathlib import Path
from dataclasses import dataclass
import inspect
import time
import traceback
from typing import Any, Iterable, Optional

import pandas as pd

# Make the repo root importable so `from SLP_Ade.config import ...` works both
# when this module is imported as part of the package and when it is run
# directly as a script.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from pylpg import lpg_execution, lpgdata
from pylpg.lpgpythonbindings import EnergyIntensityType, JsonReference

from SLP_Ade.config import (
    CLIMATE_SET_KEYS,
    END_DATE,
    HOUSEHOLD_TEMPLATE_KEYS,
    HOUSETYPE,
    LPG_BINARY_PATH,
    MERGED_OUTPUT_DIR,
    SAVE_CSV,
    SAVE_HDF5,
    START_DATE,
    TRANSPORT_VARIANT_KEYS,
    ClimateSetKey,
    TransportVariantKey,
    YEAR,
    get_runs_for_combo,
)


def prompt_clean_output_dir() -> None:
    """Ask user if they want to delete existing output files.

    Prompts the user interactively to delete CSV and HDF5 files in MERGED_OUTPUT_DIR.
    Lists existing files and waits for yes/no confirmation.

    :return None: No return value.
    """
    csv_files = list(MERGED_OUTPUT_DIR.glob("*.csv"))
    hdf5_files = list(MERGED_OUTPUT_DIR.glob("*.h5"))

    if not csv_files and not hdf5_files:
        print(f"Output directory '{MERGED_OUTPUT_DIR}' is empty. Ready to start.")
        return

    print(f"\nFound existing output files in '{MERGED_OUTPUT_DIR}':")
    if csv_files:
        print(f"  - {len(csv_files)} CSV files")
        for f in sorted(csv_files)[:3]:
            print(f"    - {f.name}")
        if len(csv_files) > 3:
            print(f"    ... and {len(csv_files) - 3} more")
    if hdf5_files:
        print(f"  - {len(hdf5_files)} HDF5 files")
        for f in sorted(hdf5_files):
            print(f"    - {f.name}")

    while True:
        response = input("\nDelete all existing multirun output files for this run? (yes/no): ").strip().lower()

        if response in ("yes", "y"):
            for f in csv_files:
                f.unlink()
            for f in hdf5_files:
                f.unlink()
            print(f"Deleted {len(csv_files)} CSV files and {len(hdf5_files)} HDF5 files.\n")
            break
        elif response in ("no", "n"):
            print("Keeping existing files. New results will be added.\n")
            break
        else:
            print("Invalid response. Please enter 'yes/y' or 'no/n'.")


def safe_name(s: str) -> str:
    """Convert string to filesystem-safe name by replacing/removing special characters.

    :param str s: The string to convert.
    :return str: Filesystem-safe version of the string.
    """
    translation = str.maketrans({" ": "_", "/": "_", ",": "", "(": "", ")": ""})
    return s.translate(translation)


def split_dataframe_by_type(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split DataFrame columns by data type prefix (e.g., 'Electricity_HH1' -> 'Electricity').

    :param pd.DataFrame df: The DataFrame to split.
    :return dict[str, pd.DataFrame]: Dictionary mapping data type to DataFrame.
    """
    data_types = {}
    for col in df.columns:
        data_type = col.rsplit("_", 1)[0]
        if data_type not in data_types:
            data_types[data_type] = pd.DataFrame(index=df.index)
        data_types[data_type][col] = df[col]
    return data_types


def attach_flexibility_events(
    data_types: dict[str, pd.DataFrame], df: pd.DataFrame
) -> dict[str, pd.DataFrame]:
    """Add the flexibility event log (if present) as its own data-type group.

    When flexibility is enabled and shifting events occurred, the LPG execution
    layer attaches the flattened event log to ``df.attrs['flexibility_events']``.
    It is an event log, not a minute-resolution profile, so it is stored as a
    standalone ``FlexibilityEvents`` group alongside the per-load-type profiles
    rather than merged into them. No-op when no events are attached.

    :param dict[str, pd.DataFrame] data_types: Data-type -> DataFrame mapping to extend.
    :param pd.DataFrame df: Result frame whose ``.attrs`` may hold the event log.
    :return dict[str, pd.DataFrame]: The mapping, with a ``FlexibilityEvents`` entry added when present.
    """
    events_df = df.attrs.get("flexibility_events")
    if events_df is not None:
        data_types["FlexibilityEvents"] = events_df
    return data_types


def collect_lpg_members(container: Any, expected_type: type) -> dict[str, Any]:
    """Collect public class members of `container` that match `expected_type`.

    :param Any container: The class or object to collect members from.
    :param type expected_type: The type to filter members by.
    :return dict[str, Any]: Dictionary mapping member names to values.
    """
    return {
        name: value
        for name, value in inspect.getmembers(container)
        if not name.startswith("_") and isinstance(value, expected_type)
    }


def collect_lpg_references_by_name(container: Any) -> dict[str, JsonReference]:
    """Collect ``JsonReference`` members of `container` keyed by their ``.Name``.

    The companion to :func:`collect_lpg_members`, but keyed by the LPG reference
    string (``JsonReference.Name``, e.g. ``"(Germany) Berlin"``) rather than the
    Python attribute name. The config stores these ``.Name`` strings, so both the
    task manifest and the sequential runner resolve them back to the full
    ``JsonReference`` (Name **and** Guid) through this map — the exact catalog
    object, Guid included, reaches the LPG request.

    :param Any container: The class or object to collect references from.
    :return dict[str, JsonReference]: Mapping from each reference's ``.Name`` to
        the reference object.
    """
    return {
        value.Name: value
        for _, value in inspect.getmembers(container)
        if isinstance(value, JsonReference)
    }


def select_by_keys(
    available: dict[str, Any],
    keys: Optional[Iterable[str]],
    label: str,
) -> list[Any]:
    """Select values from `available` by key list, or all values if keys is None.

    :param dict[str, Any] available: Dictionary of available values.
    :param Optional[Iterable[str]] keys: Keys to select, or None for all values.
    :param str label: Label for error messages.
    :return list[Any]: List of selected values.
    :raises KeyError: If a key is not found in available.
    """
    if keys is None:
        return list(available.values())

    selected: list[Any] = []
    for key in keys:
        if key not in available:
            raise KeyError(f"Unknown {label} key: {key}")
        selected.append(available[key])
    return selected


def resolve_optional_key(
    available: dict[str, JsonReference],
    key: Optional[str],
    label: str,
) -> Optional[JsonReference]:
    """Resolve an optional key to a JsonReference.

    :param dict[str, JsonReference] available: Dictionary of available references.
    :param Optional[str] key: The key to resolve, or None.
    :param str label: Label for error messages.
    :return Optional[JsonReference]: The resolved reference, or None if key is None.
    :raises KeyError: If the key is not found in available.
    """
    if key is None:
        return None
    if key not in available:
        raise KeyError(f"Unknown {label} key: {key}")
    return available[key]


def make_climate_variants(
    all_geographic_locations: dict[str, JsonReference],
    all_temperature_profiles: dict[str, JsonReference],
    climate_keys: Optional[list[ClimateSetKey]],
) -> list[tuple[JsonReference, Optional[JsonReference], str]]:
    """Create climate variant combinations.

    :param dict[str, JsonReference] all_geographic_locations: Available geographic locations.
    :param dict[str, JsonReference] all_temperature_profiles: Available temperature profiles.
    :param Optional[list[ClimateSetKey]] climate_keys: Climate variant keys, or None for all combinations.
    :return list[tuple[JsonReference, Optional[JsonReference], str]]: List of (location, temperature_profile, tag) tuples.
    :raises KeyError: If a required location key is missing.
    """
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
    for climate_key in climate_keys:
        location = resolve_optional_key(
            all_geographic_locations,
            climate_key.geographic_location_key,
            "geographic location",
        )
        if location is None:
            raise KeyError("Climate variants require a geographic location key")
        temperature_profile = resolve_optional_key(
            all_temperature_profiles,
            climate_key.temperature_profile_key,
            "temperature profile",
        )
        variants.append((location, temperature_profile, climate_key.tag))
    return variants


@dataclass(frozen=True)
class TransportVariant:
    """Resolved transport variant with JsonReferences.

    Attributes:
        simulate_transportation: Whether to enable transportation simulation.
        charging_set: Charging station set reference (or None).
        transport_device_set: Transportation device set reference (or None).
        travel_route_set: Travel route set reference (or None).
        tag: Human-readable tag for this variant.
    """
    simulate_transportation: bool
    charging_set: Optional[JsonReference]
    transport_device_set: Optional[JsonReference]
    travel_route_set: Optional[JsonReference]
    tag: str


def make_transport_variants(
    all_charging_sets: dict[str, JsonReference],
    all_transport_device_sets: dict[str, JsonReference],
    all_travel_route_sets: dict[str, JsonReference],
    variant_keys: list[TransportVariantKey],
) -> list[TransportVariant]:
    """Create transport variant combinations from variant keys.

    :param dict[str, JsonReference] all_charging_sets: Available charging station sets.
    :param dict[str, JsonReference] all_transport_device_sets: Available transportation device sets.
    :param dict[str, JsonReference] all_travel_route_sets: Available travel route sets.
    :param list[TransportVariantKey] variant_keys: List of transport variant key configurations.
    :return list[TransportVariant]: List of resolved transport variants.
    """
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


def _print_lpg_binary_source() -> None:
    """Print the source of the LPG binary being used.

    :return None: No return value.                                                      # TODO: explicitly raise error if missing path, change to check_lpg_binary_source() with exception
    """
    if LPG_BINARY_PATH is None:
        print("LPG binary source: official release downloaded automatically.")
    else:
        print(f"LPG binary source: custom binary path {LPG_BINARY_PATH}")


def save_as_HDF5(
    tmpl_name: str,
    geographic_location: JsonReference,
    temperature_profile: Optional[JsonReference],
    climate_tag: str,
    climate_name: str,
    transport_variant: TransportVariant,
    run_idx: int,
    seed: int,
    data_types: dict[str, pd.DataFrame],
) -> None:
    """Save simulation results to HDF5 file with hierarchical structure.

    Creates or appends to an HDF5 file named after the template. Data is organized as:
    /climate_tag/transport_tag/run_N/data_type

    :param str tmpl_name: Template name for the HDF5 filename.
    :param JsonReference geographic_location: Geographic location reference.
    :param Optional[JsonReference] temperature_profile: Temperature profile reference.
    :param str climate_tag: Climate variant tag.
    :param str climate_name: Climate variant name.
    :param TransportVariant transport_variant: Transport variant configuration.
    :param int run_idx: Run index (0-based).
    :param int seed: Random seed used for this run.
    :param dict[str, pd.DataFrame] data_types: Dictionary mapping data type names to DataFrames.
    :return None: No return value.
    """
    hdf5_filename = f"{safe_name(tmpl_name)}.h5"
    hdf5_path = MERGED_OUTPUT_DIR / hdf5_filename
    # Create hierarchical path: /climate/transport/run_N/data_type
    with pd.HDFStore(hdf5_path, mode='a', complevel=9, complib='blosc') as store:
        base_path = f"{safe_name(climate_tag)}/{transport_variant.tag}/run_{run_idx + 1}"
        for data_type, type_df in data_types.items():
            key = f"{base_path}/{safe_name(data_type)}"
            store.put(key, type_df, format='fixed')
        # Store metadata
        metadata_key = f"{base_path}/_metadata"
        meta_df = pd.DataFrame([{
            "seed": seed,
            "template": tmpl_name,
            "climate": climate_name,
            "geographic_location": geographic_location.Name,
            "temperature_profile": temperature_profile.Name if temperature_profile else None,
            "transport_tag": transport_variant.tag,
        }])
        store.put(metadata_key, meta_df, format='fixed')
    if not SAVE_CSV:
        print(f"  Saved {len(data_types)} data types to HDF5: {', '.join(sorted(data_types.keys()))}")


def create_combo_tag(tmpl_name: str, climate_name: str, transport_tag: str) -> str:
    """Create a combination tag from template, climate, and transport names.

    Combines the three components with double underscores, using safe_name()
    to ensure filesystem compatibility.

    :param str tmpl_name: Template name.
    :param str climate_name: Climate variant name.
    :param str transport_tag: Transport variant tag.
    :return str: Combined tag string.
    """
    return f"{safe_name(tmpl_name)}__{safe_name(climate_name)}__{transport_tag}"


def run_lpg_simulation(
    tmpl: str,
    transport_variant: TransportVariant,
    geographic_location: JsonReference,
    temperature_profile: Optional[JsonReference],
    seed: int,
    calculation_index: int = 1,
    clear_previous_calc: bool = False,
) -> Optional[pd.DataFrame]:
    """Build a household and execute one LPG simulation.

    This is the core execution primitive shared between interactive
    (simulation) and SLURM-array (run_task) modes.

    Idle-mode is always enabled here (``enable_idle_mode=True``). Several of the
    configured household templates -- specifically the ones with young children
    -- intermittently leave a person with no available affordance at some
    timestep, which the LPG treats as a fatal ``DataIntegrityException`` and
    aborts the whole run (this function then returns ``None`` and the task is
    lost). Idle-mode gives the stuck person a fallback "Idle" activity so those
    runs complete instead. Observed impact on the first full sweep: it recovers
    the tasks that otherwise fail, all of which are child-bearing households; the
    cost is a minor behavioural artifact (a brief "doing nothing" in place of a
    real activity). See ``enable_idle_mode`` in
    :func:`pylpg.lpg_execution.execute_lpg_with_householddata_enabled_flex_and_transport_custom`
    for the full rationale and trade-off.

    Each calculation runs in its own ``C<calculation_index>`` working directory.
    Parallel callers (e.g. the SLURM worker) MUST pass a unique
    ``calculation_index`` per concurrent run, otherwise they collide on the same
    working directory. The base location of these working directories is taken
    from the ``LPG_WORK_DIR`` environment variable when set (point it at fast
    node-local scratch such as ``$TMPDIR`` on a cluster); otherwise it defaults
    to the pylpg package directory.

    :param str tmpl: Template name string (value of a HouseholdTemplates attribute).
    :param TransportVariant transport_variant: Resolved transport configuration.
    :param JsonReference geographic_location: Geographic location reference.
    :param Optional[JsonReference] temperature_profile: Temperature profile reference.
    :param int seed: Random seed.
    :param int calculation_index: Unique index selecting the C<idx> working directory.
    :param bool clear_previous_calc: Wipe and re-copy the working directory before running.
    :return Optional[pd.DataFrame]: Simulation result DataFrame, or None on failure.
    """
    if START_DATE is None or END_DATE is None:
        raise ValueError(
            "Simulation date range is not configured: set START_DATE and "
            "END_DATE in SLP_Ade/config.py (ISO 'YYYY-MM-DD' strings). "
            f"Got START_DATE={START_DATE!r}, END_DATE={END_DATE!r}."
        )

    household = lpgdata.HouseholdData(
        None,
        lpgdata.HouseholdTemplateSpecification(HouseholdTemplateName=tmpl),
        None,
        "hhid",
        "hhname",
        transport_variant.charging_set,
        transport_variant.transport_device_set,
        transport_variant.travel_route_set,
        None,
        HouseholdDataSpecification=lpgdata.HouseholdDataSpecificationType.ByTemplateName,
        # The HouseholdData binding defaults PointOfInterestPreferences to an
        # empty dict, which serializes to `{}` (non-null). With transportation
        # enabled the LPG treats a non-null POI-preferences value as "POI-based
        # travel requested" (its check is literally `is not null`), so combined
        # with our TravelRouteSet it sees two conflicting travel-behavior inputs
        # and aborts ("Two or more properties specifying travel behavior were
        # set"). Force it to None so it serializes to null and the TravelRouteSet
        # is the only travel-behavior signal.
        PointOfInterestPreferences=None,
    )
    startdate = START_DATE
    enddate = END_DATE

    return lpg_execution.execute_lpg_with_householddata_enabled_flex_and_transport_custom(
        YEAR,
        household,
        HOUSETYPE,
        startdate,
        enddate,
        geographic_location=geographic_location,
        temperature_profile=temperature_profile,
        enable_flexibility=True,
        enable_transportation=transport_variant.simulate_transportation,
        # Prevent child-affordance dead-ends from aborting the run; see the
        # run_lpg_simulation docstring above for why this is unconditionally True.
        enable_idle_mode=True,
        random_seed=seed,
        energy_intensity=EnergyIntensityType.Random,
        calculation_index=calculation_index,
        clear_previous_calc=clear_previous_calc,
        lpg_binary_path=LPG_BINARY_PATH,
        working_directory=os.environ.get("LPG_WORK_DIR"),
    )


def execute_single_run(
    tmpl: str,
    tmpl_name: str,
    geographic_location: JsonReference,
    temperature_profile: Optional[JsonReference],
    climate_tag: str,
    climate_name: str,
    transport_variant: TransportVariant,
    combo_tag: str,
    run_idx: int,
    num_runs: int,
) -> Optional[dict[str, Any]]:
    """Execute a single LPG simulation run.

    :param str tmpl: Template identifier.
    :param str tmpl_name: Template name for output files.
    :param JsonReference geographic_location: Geographic location reference.
    :param Optional[JsonReference] temperature_profile: Temperature profile reference.
    :param str climate_tag: Climate variant tag.
    :param str climate_name: Climate variant name.
    :param TransportVariant transport_variant: Transport variant configuration.
    :param str combo_tag: Combined identifier tag.
    :param int run_idx: Run index (0-based).
    :param int num_runs: Total number of runs for this combination.
    :return Optional[dict[str, Any]]: Metadata dictionary if successful, None otherwise.
    """
    # Generate seed: current time in milliseconds, modulo 2^31 to fit in 32-bit signed int
    seed = int(time.time() * 1000) % 2**31
    seed += run_idx  # Add run index to ensure different seeds for multiple runs

    try:
        print(
            f"Running: {combo_tag} seed={seed} "
            f"(run {run_idx + 1}/{num_runs})"
        )

        df = run_lpg_simulation(
            tmpl, transport_variant, geographic_location, temperature_profile, seed
        )

        if df is None:
            print("No results returned for this run")
            return None

        filename_base = f"{combo_tag}__seed{seed}__run{run_idx + 1}"

        # Split dataframe by data type
        data_types = split_dataframe_by_type(df)
        # Store the flexibility event log (if any) as its own group.
        attach_flexibility_events(data_types, df)

        # Save to CSV if enabled
        if SAVE_CSV:
            for data_type, type_df in data_types.items():
                out_csv = MERGED_OUTPUT_DIR / (safe_name(f"{filename_base}__{data_type}") + ".csv")
                type_df.to_csv(out_csv)
            print(f"  Saved {len(data_types)} data types to CSV: {', '.join(sorted(data_types.keys()))}")

        # Save to HDF5 if enabled (one file per household template)
        if SAVE_HDF5:
            save_as_HDF5(
                tmpl_name,
                geographic_location,
                temperature_profile,
                climate_tag,
                climate_name,
                transport_variant,
                run_idx,
                seed,
                data_types,
            )

        return {
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
            "hdf5_file": f"{safe_name(tmpl_name)}.h5" if SAVE_HDF5 else None,
            "hdf5_path": f"{safe_name(climate_tag)}/{transport_variant.tag}/run_{run_idx + 1}" if SAVE_HDF5 else None,
        }
    except Exception:
        print("Run failed:")
        traceback.print_exc()
        return None


def execute_all_runs(
    household_templates: list[str],
    climate_sets: list[tuple[JsonReference, Optional[JsonReference], str]],
    transport_variants: list[TransportVariant],
) -> tuple[list[dict[str, Any]], int]:
    """Execute all simulation runs for given parameter combinations.

    Iterates through all combinations of templates, climate variants, and transport
    variants, executing multiple runs per combination based on configuration.

    :param list[str] household_templates: List of household template names.
    :param list[tuple[JsonReference, Optional[JsonReference], str]] climate_sets: List of (location, temp_profile, tag) tuples.
    :param list[TransportVariant] transport_variants: List of transport variant configurations.
    :return tuple[list[dict[str, Any]], int]: Tuple of (metadata rows, total successful runs).
    """
    meta_rows = []
    total = 0

    # Execute all parameter combinations
    for tmpl in household_templates:
        if tmpl is None:
            raise ValueError("Household template is None")
        tmpl_name = tmpl

        for geographic_location, temperature_profile, climate_tag in climate_sets:
            climate_name = climate_tag

            for transport_variant in transport_variants:
                combo_tag = create_combo_tag(tmpl_name, climate_name, transport_variant.tag)
                num_runs = get_runs_for_combo(combo_tag)

                # Execute multiple runs with different seeds for this combination
                for run_idx in range(num_runs):
                    metadata = execute_single_run(
                        tmpl,
                        tmpl_name,
                        geographic_location,
                        temperature_profile,
                        climate_tag,
                        climate_name,
                        transport_variant,
                        combo_tag,
                        run_idx,
                        num_runs,
                    )

                    if metadata is not None:
                        meta_rows.append(metadata)
                        total += 1

    return meta_rows, total


def print_summary(meta_df: pd.DataFrame, total: int) -> None:
    """Print summary of completed simulation runs.

    :param pd.DataFrame meta_df: DataFrame containing metadata for all runs.
    :param int total: Total number of successful runs.
    :return None: No return value.
    """
    output_summary = []
    if SAVE_CSV:
        output_summary.append("CSV files")
    if SAVE_HDF5:
        hdf5_files = meta_df['hdf5_file'].dropna().unique()
        output_summary.append(f"{len(hdf5_files)} HDF5 file(s) (one per household template)")

    print(
        f"\nFinished {total} successful runs.\n"
        f"Output: {' and '.join(output_summary)}\n"
        f"Metadata: {MERGED_OUTPUT_DIR / 'runs_metadata.csv'}"
    )

    if SAVE_HDF5:
        hdf5_files = meta_df['hdf5_file'].dropna().unique()
        print(f"\nHDF5 files created:")
        for hdf5_file in sorted(hdf5_files):
            print(f"  - {hdf5_file}")
        print(f"\nHDF5 structure per file: /climate/transport/run_N/data_type")


def run_all() -> None:
    """Run all configured LPG simulations and save results.

    Main execution function that:
    1. Collects all available LPG members (templates, locations, etc.)
    2. Creates parameter combinations from configuration
    3. Runs simulations for each combination with multiple seeds
    4. Saves results to CSV and/or HDF5 files
    5. Generates metadata CSV summarizing all runs

    :return None: No return value.
    """
    _print_lpg_binary_source()
    # Create the merged-output dir on demand (config no longer does this at
    # import time, so importing config never touches the filesystem).
    MERGED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_clean_output_dir()

    # Collect all available LPG members
    all_templates = collect_lpg_members(lpgdata.HouseholdTemplates, str)
    # JsonReference catalogs are keyed by .Name (matching the strings the config
    # stores), so make_climate_variants / make_transport_variants resolve the
    # config keys straight back to the full reference (Name + Guid).
    all_geographic_locations = collect_lpg_references_by_name(
        lpgdata.GeographicLocations
    )
    all_temperature_profiles = collect_lpg_references_by_name(
        lpgdata.TemperatureProfiles
    )
    all_charging_sets = collect_lpg_references_by_name(lpgdata.ChargingStationSets)
    all_transport_device_sets = collect_lpg_references_by_name(
        lpgdata.TransportationDeviceSets
    )
    all_travel_route_sets = collect_lpg_references_by_name(lpgdata.TravelRouteSets)

    # Create parameter combinations
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

    # Execute all simulation runs
    meta_rows, total = execute_all_runs(
        household_templates,
        climate_sets,
        transport_variants,
    )

    # Save metadata and print summary
    meta_df = pd.DataFrame(meta_rows)
    meta_df.to_csv(MERGED_OUTPUT_DIR / "runs_metadata.csv", index=False)
    print_summary(meta_df, total)


if __name__ == "__main__":
    run_all()
