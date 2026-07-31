"""
Structural key types and validation helpers used to declare a sweep
configuration.

This module deliberately imports nothing else from the package, so a
user-supplied config (copied from ``examples/sweep_config_minimal.py`` over
``config.py``) can import from it without a circular import.
"""

from dataclasses import dataclass
from typing import Any, Optional, Sequence


def require_non_empty(
    value: Optional[Sequence[Any]],
    name: str,
    *,
    allow_none: bool,
    none_means: str = "",
) -> None:
    """Validate that a config key list actually selects something.

    An empty list is never valid: it selects nothing, so the sweep expands to
    zero tasks -- an editing mistake, not an intent. Rejecting it at import time
    surfaces the problem immediately instead of as an empty ``tasks.json``.

    ``None`` is a separate question and differs per knob, which is why callers
    must state ``allow_none`` explicitly. Where it is allowed it means "all of
    them"; where it is not, the consumers iterate the value directly and would
    otherwise fail with an opaque ``TypeError``.

    :param Optional[Sequence[Any]] value: The configured value to check.
    :param str name: Name of the config knob, used in the error message.
    :param bool allow_none: Whether None is valid, meaning "use all entries".
    :param str none_means: What None expands to, quoted in the error message
        when ``allow_none`` is True. Ignored otherwise.
    :return None: No return value.
    :raises ValueError: If value is empty, or None while allow_none is False.
    """
    if value is None:
        if allow_none:
            return
        raise ValueError(
            f"{name} must contain at least one entry; None is not accepted here."
        )

    if len(value) == 0:
        message = f"{name} must contain at least one entry."
        if allow_none:
            message += f" Set it to None to {none_means or 'use all of them'}."
        raise ValueError(message)


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
            used to name per-run output files.
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
            ...``) and part of the ``combo_tag`` used to name per-run output files.
    """
    geographic_location_key: str
    temperature_profile_key: Optional[str]
    tag: str
