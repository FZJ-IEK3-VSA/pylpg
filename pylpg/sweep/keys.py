"""
Structural key types used to declare a sweep configuration.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TransportVariantKey:
    """Configuration key for a transport variant.

    Attributes:
        simulate_transportation: Whether to enable transportation simulation.
        charging_set_key: The ``.Name`` of a ``lpgdata.ChargingStationSets``
            reference (or None).
        transport_device_set_key: The ``.Name`` of a
            ``lpgdata.TransportationDeviceSets`` reference (or None).
        travel_route_set_key: The ``.Name`` of a ``lpgdata.TravelRouteSets``
            reference (or None).
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
        geographic_location_key: The ``.Name`` of a
            ``lpgdata.GeographicLocations`` reference (e.g. ``"(Germany) Berlin"``).
            The runner resolves it back to the full ``JsonReference`` (Name +
            Guid) at runtime.
        temperature_profile_key: The ``.Name`` of a
            ``lpgdata.TemperatureProfiles`` reference, or None to fall back to the
            location's own default profile.
        tag: Short, filesystem-safe identifier for this variant. Load-bearing,
            exactly like ``TransportVariantKey.tag``: it is the climate level of
            the HDF5 output hierarchy (``/<climate_tag>/<transport_tag>/run_<N>/
            ...``) and part of the ``combo_tag`` used for deterministic seeding.
    """
    geographic_location_key: str
    temperature_profile_key: Optional[str]
    tag: str
