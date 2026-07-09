# SLP_Ade residential load-profile dataset

*Deutsche Version: [DATASET.de.md](DATASET.de.md)*

Synthetic residential energy **load profiles** generated with the
[LoadProfileGenerator](https://www.loadprofilegenerator.de/) (LPG) behaviour
simulator via the [pyLPG](https://github.com/FZJ-IEK3-VSA/pylpg) wrapper
(`SLP_Ade` sweep). Intended use: **training data** for load-profile / demand
models.

Each profile is a minute-resolution time series for one simulated household
over a full calendar year, under a chosen climate and transport configuration.
The simulation is stochastic, so several independent *runs* (different random
seeds) are provided per configuration to capture behavioural variability.

---

## 1. Files

| File | Household template | Size |
|------|--------------------|------|
| `CHR01_Couple_both_at_Work.h5` | Couple, both working | 1.57 GB |
| `CHR05_Family_3_children_both_with_work.h5` | Family, 3 children, both parents working | 1.60 GB |
| `CHR07_Single_with_work.h5` | Single, working | 1.52 GB |
| `CHR08_Single_woman_2_children_with_work.h5` | Single mother, 2 children, working | 1.58 GB |
| `CHR13_Student_with_Work.h5` | Student with a job | 1.49 GB |
| `CHR15_Multigenerational_Home_working_couple_2_children_2_seniors.h5` | Multigenerational: working couple, 2 children, 2 seniors | 1.66 GB |
| `CHR16_Couple_over_65_years.h5` | Retired couple (65+) | 1.56 GB |
| `CHR18_Family_2_children_parents_without_work.h5` | Family, 2 children, parents not working | 1.60 GB |
| `CHR23_Single_man_over_65_years.h5` | Retired single man (65+) | 1.50 GB |
| `CHR27_Family_both_at_work_2_children.h5` | Family, 2 children, both parents working | 1.60 GB |
| `runs_metadata.csv` | Index of all 120 runs (see §6) | ~33 KB |

**Total ≈ 15.7 GB.** One HDF5 file per household template (10 templates).

Format: HDF5 written by `pandas.HDFStore`, `format="fixed"`, compressed with
`blosc` (level 9). Reading requires **PyTables** (`pip install tables`).

---

## 2. What varies (dataset dimensions)

Every file contains the full cross-product of:

- **Climate** (3) — geographic location + historical DWD temperature year:
  - `berlin_loc_berlin_temp` — Berlin location, Berlin 1996 temperature
  - `hamburg_loc_hamburg_temp` — Hamburg location, Hamburg 2007 temperature
  - `chemnitz_loc_dresden_temp` — Chemnitz location, Dresden 2000 temperature
- **Transport** (2):
  - `no_transport` — no mobility simulated — **1 run**
  - `home_charge_bus_cars_30km` — home charging (3.7 kW), a bus + two 30 km/h
    cars + three bicycles, 30 km commuting distance — **3 runs**
- **Runs** — independent repetitions with different random seeds (see §7).

Per template: 3 climates × (1 + 3) runs = **12 runs**. Across 10 templates =
**120 runs total**.

---

## 3. Internal structure (HDF5 keys)

Keys follow a 4-level hierarchy:

```
/<climate_tag>/<transport_tag>/run_<N>/<data_type>
```

Example:

```
/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity
/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity_NoFlex
/hamburg_loc_hamburg_temp/no_transport/run_1/_metadata
```

`run_<N>` is **1-based** (`run_1` … `run_3`).

---

## 4. Time index and columns

- **Index:** a minute-resolution `DatetimeIndex`, `2020-01-01 00:00` →
  `2020-12-31 23:59`, `freq="min"` → **527 040 rows** (2020 is a leap year:
  366 × 1440). Every profile group in the dataset shares this index.
- **Columns** of a profile group are named `<LoadType>_<HHKey>`, where `HHKey`
  is:
  - `House` — whole-house aggregate (household + house-level devices)
  - `HH1` — the single household in the house
- **Values** are the instantaneous quantity at each minute (see units in §5) —
  *not* energy sums.

The weather driving each run is the **historical** DWD temperature year listed
in §2 (not 2020 weather); 2020 is only the calendar the behaviour is mapped
onto.

> **House type:** all runs use `HT20 Single Family House (no heating / cooling)`.
> **These profiles therefore contain no space-heating or space-cooling load.**
> Hot/cold/warm water and appliance electricity are included; building thermal
> demand is not.

---

## 5. Data types inside each `run_<N>` group

### Energy / load profiles (minute resolution)
Each appears **twice**: the flexible profile `<LoadType>` and its baseline twin
`<LoadType>_NoFlex` (see §8).

| Data type | Quantity | Unit (per minute) |
|-----------|----------|-------------------|
| `Electricity` | Electrical power | Watt |
| `Apparent` | Apparent power | VA |
| `Reactive` | Reactive power | var |
| `Inner_Device_Heat_Gains` | Internal heat gains from devices | Watt (thermal) |
| `Cold_Water` | Cold-water draw | L/min |
| `Hot_water` | Hot-water draw | L/min |
| `Warm_Water` | Warm-water draw | L/min |
| `Gasoline` | Fuel use | L/min |
| `None` | Devices with no assigned load type | — |

### Occupancy / activity
Number of people at each bodily-activity level, per minute:
`Person_Count_for__-_High`, `Person_Count_for__-_Low`,
`Person_Count_for__-_Outside`, `Person_Count_for__-_Unknown`.

### Transport channels — **only in `home_charge_bus_cars_30km` runs**
Per transport device (`Bicycle_1/2/3`, `Car_1_22kW…`, `Car_2_22kW…`):
`Car_Location_-_<device>`, `Car_State_-_<device>`,
`Driving_Distance_-_<device>`, `State_of_charge_-_<device>`.
Plus `Electricity_for_Car_Charging` (+ `_NoFlex`) and `Elevator_Distance`
(+ `_NoFlex`).

### Flexibility event log
`FlexibilityEvents` — one **row per load-shifting event** (not a time series).
Columns describe the flexible device, its loads and the shift window
(`Device.*`, `EarliestStart.*`, `LatestStart.*`, `TotalDuration`, …). Nested
fields (`Profiles`, `Device.Loads`) are stored as **JSON-encoded strings**;
`json.loads` them to expand.

### Per-run metadata
`_metadata` — a **1-row** DataFrame: `task_id`, `template_key`, `climate_tag`,
`transport_tag`, `run_idx`, `seed`, `geographic_location`,
`temperature_profile`. Present for **every** run.

---

## 6. `runs_metadata.csv`

A 120-row flat index of all runs (one row per run), with columns:
`task_id, template_key, climate_tag, transport_tag, run_idx, seed,
geographic_location, temperature_profile, hdf5_file, hdf5_path`.
Use it to look up which file + key path holds a given configuration without
opening every HDF5 file. **Note:** for robustness, confirm entries against the
actual HDF5 content (§9) when combining with other datasets.

---

## 7. Seeds and reproducibility

Each run's random seed is stored in its `_metadata` group and in
`runs_metadata.csv`. Seeds are derived deterministically from the configuration
(MD5 of `combo_tag + run_idx`), so the manifest — and thus the intended dataset —
is reproducible from the `SLP_Ade` code at the pinned pyLPG revision.

---

## 8. Flexibility: `<LoadType>` vs `<LoadType>_NoFlex`

Flexibility modelling was **enabled** for all runs. For every load type the LPG
emits two aligned profiles:

- `<LoadType>` — the **flexible** profile, with shiftable devices (e.g.
  dishwasher, car charging) moved within their allowed windows.
- `<LoadType>_NoFlex` — the **baseline**, the same household with **no**
  load-shifting applied.

The element-wise difference `<LoadType> − <LoadType>_NoFlex` is the modelled
demand-response / load-shifting effect. The `FlexibilityEvents` log records the
individual shifts.

---

## 9. Data completeness

**All 120 run-groups contain full profile data** (verified by walking every
file: 120 runs, 0 empty). Every `/<climate>/<transport>/run_<N>/` group holds
the load profiles, occupancy, flexibility log and — for transport runs — the
transport channels described in §5.

As a defensive check (e.g. when combining this with other sweeps), confirm a
profile group actually exists under a run path rather than trusting
`runs_metadata.csv` alone:

```python
def run_has_data(store, run_path):
    return f"{run_path}/Electricity" in store  # any expected load type
```

---

## 10. Loading examples (Python)

Requires `pandas` and `tables` (PyTables).

```python
import pandas as pd

path = "CHR07_Single_with_work.h5"

# --- list everything -------------------------------------------------------
with pd.HDFStore(path, mode="r") as store:
    for key in store.keys():
        print(key)

# --- load one profile ------------------------------------------------------
with pd.HDFStore(path, mode="r") as store:
    el = store["/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity"]
# el.index -> minute DatetimeIndex; el.columns -> ['Electricity_House', 'Electricity_HH1']
print(el.shape, list(el.columns))

# --- iterate all runs that actually have data ------------------------------
import itertools
with pd.HDFStore(path, mode="r") as store:
    run_paths = sorted({ "/".join(k.split("/")[:4]) for k in store.keys()
                         if len(k.split("/")) >= 5 })
    for rp in run_paths:
        if f"{rp}/Electricity" not in store:
            continue                     # skip the empty run-groups (§9)
        meta = store[f"{rp}/_metadata"].iloc[0]
        elec = store[f"{rp}/Electricity"]["Electricity_HH1"]
        print(rp, "seed=", meta["seed"], "mean W=", round(elec.mean(), 1))

# --- the flat run index ----------------------------------------------------
runs = pd.read_csv("runs_metadata.csv")
```

---

## 11. Provenance

- **Generator:** LoadProfileGenerator (LPG), driven by pyLPG (`SLP_Ade` sweep).
- **Simulation window:** full year 2020, 1-minute resolution.
- **Flexibility:** enabled (see §8). **Idle-mode:** enabled (a fallback "Idle"
  activity that prevents the behaviour engine from aborting when a household —
  typically one with young children — momentarily has no available activity).
- **House type:** HT20 Single Family House, no heating/cooling (§4).
- **Templates, climates, transport, seeds:** as described above and recorded in
  each `_metadata` group / `runs_metadata.csv`.
