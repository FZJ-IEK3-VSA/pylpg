"""Tests for the SLP_Ade SLURM-array workflow.

All tests here are fast and do NOT execute LPG simulations.
They cover:
  - Pure helper functions in multi_simulations.py
  - Task-manifest generation in generate_tasks.py (build_task_list)
"""
from __future__ import annotations

import json
from collections import defaultdict

import pandas as pd
import pytest

from pylpg import lpgdata
from pylpg.lpgpythonbindings import JsonReference

from SLP_Ade.multi_simulations import (
    CLIMATE_SET_KEYS,
    TRANSPORT_VARIANT_KEYS,
    collect_lpg_members,
    create_combo_tag,
    get_runs_for_combo,
    safe_name,
    select_by_keys,
    split_dataframe_by_type,
)
from SLP_Ade.generate_tasks import _deterministic_seed, build_task_list


# ---------------------------------------------------------------------------
# safe_name
# ---------------------------------------------------------------------------

def test_safe_name_replaces_spaces() -> None:
    assert safe_name("My Template") == "My_Template"


def test_safe_name_replaces_slash() -> None:
    assert safe_name("foo/bar") == "foo_bar"


def test_safe_name_removes_parens_and_commas() -> None:
    # "(", ")", "," are stripped (not replaced); spaces become underscores
    assert safe_name("CHR01 (v2), 2020") == "CHR01_v2_2020"


# ---------------------------------------------------------------------------
# split_dataframe_by_type
# ---------------------------------------------------------------------------

def test_split_dataframe_by_type_groups_correctly() -> None:
    df = pd.DataFrame({
        "Electricity_HH1": [1.0, 2.0],
        "Electricity_HH2": [3.0, 4.0],
        "Warmwater_HH1": [5.0, 6.0],
    })
    result = split_dataframe_by_type(df)
    assert set(result.keys()) == {"Electricity", "Warmwater"}
    assert list(result["Electricity"].columns) == ["Electricity_HH1", "Electricity_HH2"]
    assert list(result["Warmwater"].columns) == ["Warmwater_HH1"]


def test_split_dataframe_by_type_splits_on_last_underscore() -> None:
    # "Foo_Bar_HH1" → type "Foo_Bar", not "Foo"
    df = pd.DataFrame({"Foo_Bar_HH1": [1.0]})
    result = split_dataframe_by_type(df)
    assert "Foo_Bar" in result


# ---------------------------------------------------------------------------
# collect_lpg_members
# ---------------------------------------------------------------------------

def test_collect_lpg_members_returns_strings_for_templates() -> None:
    members = collect_lpg_members(lpgdata.HouseholdTemplates, str)
    assert len(members) > 0
    for attr_name, template_value in members.items():
        assert isinstance(attr_name, str)
        assert isinstance(template_value, str)


def test_collect_lpg_members_keys_differ_from_values_for_templates() -> None:
    # Attribute names use underscores; string values use spaces
    members = collect_lpg_members(lpgdata.HouseholdTemplates, str)
    first_key, first_value = next(iter(members.items()))
    assert first_key != first_value  # e.g. "CHR01_Couple_..." vs "CHR01 Couple ..."


def test_collect_lpg_members_returns_jsonreferences_for_locations() -> None:
    members = collect_lpg_members(lpgdata.GeographicLocations, JsonReference)
    assert len(members) > 0
    for value in members.values():
        assert isinstance(value, JsonReference)


# ---------------------------------------------------------------------------
# select_by_keys
# ---------------------------------------------------------------------------

def test_select_by_keys_none_returns_all_values() -> None:
    d = {"a": 1, "b": 2, "c": 3}
    assert select_by_keys(d, None, "label") == [1, 2, 3]


def test_select_by_keys_filters_by_keys() -> None:
    d = {"a": 1, "b": 2, "c": 3}
    assert select_by_keys(d, ["a", "c"], "label") == [1, 3]


def test_select_by_keys_unknown_key_raises() -> None:
    d = {"a": 1}
    with pytest.raises(KeyError, match="Unknown label key: x"):
        select_by_keys(d, ["x"], "label")


# ---------------------------------------------------------------------------
# create_combo_tag
# ---------------------------------------------------------------------------

def test_create_combo_tag_format() -> None:
    tag = create_combo_tag("CHR01 Couple", "berlin_loc", "no_transport")
    assert tag == "CHR01_Couple__berlin_loc__no_transport"


def test_create_combo_tag_safe_names_first_two_parts() -> None:
    # Only the first two parts go through safe_name; transport_tag is used as-is
    tag = create_combo_tag("A B", "C/D", "x_y")
    assert tag == "A_B__C_D__x_y"


# ---------------------------------------------------------------------------
# get_runs_for_combo
# ---------------------------------------------------------------------------

def test_get_runs_for_combo_no_transport() -> None:
    assert get_runs_for_combo("template__climate__no_transport") == 1


def test_get_runs_for_combo_home_charge() -> None:
    assert get_runs_for_combo("template__climate__home_charge_bus_cars_30km") == 3


def test_get_runs_for_combo_unknown_tag_returns_default() -> None:
    assert get_runs_for_combo("completely__unknown__variant") == 2


# ---------------------------------------------------------------------------
# _deterministic_seed
# ---------------------------------------------------------------------------

def test_deterministic_seed_is_reproducible() -> None:
    assert _deterministic_seed("combo_tag", 0) == _deterministic_seed("combo_tag", 0)


def test_deterministic_seed_differs_by_run_index() -> None:
    assert _deterministic_seed("combo_tag", 0) != _deterministic_seed("combo_tag", 1)


def test_deterministic_seed_differs_by_combo_tag() -> None:
    assert _deterministic_seed("combo_a", 0) != _deterministic_seed("combo_b", 0)


def test_deterministic_seed_fits_in_31_bits() -> None:
    seed = _deterministic_seed("any_combo", 42)
    assert 0 <= seed < 2**31


# ---------------------------------------------------------------------------
# build_task_list (integration, no LPG execution)
# ---------------------------------------------------------------------------

_REQUIRED_TASK_KEYS = {
    "task_id",
    "template_key",
    "geographic_location_key",
    "temperature_profile_key",
    "climate_tag",
    "transport_simulate",
    "transport_charging_set_key",
    "transport_device_set_key",
    "transport_travel_route_key",
    "transport_tag",
    "run_idx",
    "num_runs",
    "seed",
}


def test_build_task_list_nonempty() -> None:
    assert len(build_task_list()) > 0


def test_build_task_list_sequential_ids() -> None:
    tasks = build_task_list()
    for i, task in enumerate(tasks):
        assert task["task_id"] == i


def test_build_task_list_all_keys_present() -> None:
    tasks = build_task_list()
    for task in tasks:
        missing = _REQUIRED_TASK_KEYS - task.keys()
        assert not missing, f"Task {task['task_id']} missing keys: {missing}"


def test_build_task_list_run_indices_complete() -> None:
    """For every (template, climate, transport) combo, run_idx must cover 0..num_runs-1."""
    tasks = build_task_list()
    combo_groups: dict = defaultdict(list)
    for t in tasks:
        key = (t["template_key"], t["climate_tag"], t["transport_tag"])
        combo_groups[key].append(t)

    for key, group in combo_groups.items():
        num_runs = group[0]["num_runs"]
        assert len(group) == num_runs, f"Wrong task count for {key}"
        assert sorted(t["run_idx"] for t in group) == list(range(num_runs))


def test_build_task_list_deterministic() -> None:
    """Two consecutive calls must produce identical seeds."""
    tasks1 = build_task_list()
    tasks2 = build_task_list()
    assert [t["seed"] for t in tasks1] == [t["seed"] for t in tasks2]


def test_build_task_list_json_serialisable() -> None:
    """The task list must round-trip through JSON without loss."""
    tasks = build_task_list()
    reloaded = json.loads(json.dumps(tasks))
    assert reloaded == tasks


def test_build_task_list_climate_coverage() -> None:
    """Every configured climate tag must appear in the task list."""
    if CLIMATE_SET_KEYS is None:
        pytest.skip("CLIMATE_SET_KEYS=None means all combos; count is dynamic")
    tasks = build_task_list()
    climate_tags_in_tasks = {t["climate_tag"] for t in tasks}
    for _, _, expected_tag in CLIMATE_SET_KEYS:
        assert expected_tag in climate_tags_in_tasks


def test_build_task_list_transport_coverage() -> None:
    """Every configured transport tag must appear in the task list."""
    tasks = build_task_list()
    transport_tags_in_tasks = {t["transport_tag"] for t in tasks}
    for tvk in TRANSPORT_VARIANT_KEYS:
        assert tvk.tag in transport_tags_in_tasks
