# SLP_Ade – Datensatz mit Lastprofilen für Wohngebäude

*English version: [DATASET.md](DATASET.md)*

Synthetische **Lastprofile** für den Energieverbrauch von Wohngebäuden, erzeugt
mit dem Verhaltenssimulator
[LoadProfileGenerator](https://www.loadprofilegenerator.de/) (LPG) über den
[pyLPG](https://github.com/FZJ-IEK3-VSA/pylpg)-Wrapper (`SLP_Ade`-Sweep).
Vorgesehener Zweck: **Trainingsdaten** für Lastprofil- / Bedarfsmodelle.

Jedes Profil ist eine minutenaufgelöste Zeitreihe für einen simulierten Haushalt
über ein vollständiges Kalenderjahr, unter einer gewählten Klima- und
Verkehrskonfiguration. Die Simulation ist stochastisch, daher werden pro
Konfiguration mehrere unabhängige Durchläufe (*runs*, mit unterschiedlichen
Zufallsstartwerten) bereitgestellt, um die Verhaltensvariabilität abzubilden.

---

## 1. Dateien

| Datei | Haushaltsvorlage | Größe |
|-------|------------------|-------|
| `CHR01_Couple_both_at_Work.h5` | Paar, beide berufstätig | 1,57 GB |
| `CHR05_Family_3_children_both_with_work.h5` | Familie, 3 Kinder, beide Eltern berufstätig | 1,60 GB |
| `CHR07_Single_with_work.h5` | Alleinstehend, berufstätig | 1,52 GB |
| `CHR08_Single_woman_2_children_with_work.h5` | Alleinerziehende Mutter, 2 Kinder, berufstätig | 1,58 GB |
| `CHR13_Student_with_Work.h5` | Studierende(r) mit Nebenjob | 1,49 GB |
| `CHR15_Multigenerational_Home_working_couple_2_children_2_seniors.h5` | Mehrgenerationenhaushalt: berufstätiges Paar, 2 Kinder, 2 Senioren | 1,66 GB |
| `CHR16_Couple_over_65_years.h5` | Rentnerpaar (65+) | 1,56 GB |
| `CHR18_Family_2_children_parents_without_work.h5` | Familie, 2 Kinder, Eltern nicht berufstätig | 1,60 GB |
| `CHR23_Single_man_over_65_years.h5` | Alleinstehender Rentner (65+) | 1,50 GB |
| `CHR27_Family_both_at_work_2_children.h5` | Familie, 2 Kinder, beide Eltern berufstätig | 1,60 GB |
| `runs_metadata.csv` | Index aller 120 Durchläufe (siehe §6) | ~33 KB |

**Gesamt ≈ 15,7 GB.** Eine HDF5-Datei pro Haushaltsvorlage (10 Vorlagen).

Format: HDF5, geschrieben von `pandas.HDFStore`, `format="fixed"`, komprimiert
mit `blosc` (Level 9). Zum Lesen wird **PyTables** benötigt
(`pip install tables`).

---

## 2. Was variiert (Dimensionen des Datensatzes)

Jede Datei enthält das vollständige Kreuzprodukt aus:

- **Klima** (3) — geografischer Standort + historisches DWD-Temperaturjahr:
  - `berlin_loc_berlin_temp` — Standort Berlin, Temperatur Berlin 1996
  - `hamburg_loc_hamburg_temp` — Standort Hamburg, Temperatur Hamburg 2007
  - `chemnitz_loc_dresden_temp` — Standort Chemnitz, Temperatur Dresden 2000
- **Verkehr** (2):
  - `no_transport` — keine Mobilität simuliert — **1 Durchlauf**
  - `home_charge_bus_cars_30km` — Laden zu Hause (3,7 kW), ein Bus + zwei Autos
    (30 km/h) + drei Fahrräder, 30 km Pendeldistanz — **3 Durchläufe**
- **Durchläufe** — unabhängige Wiederholungen mit unterschiedlichen
  Zufallsstartwerten (siehe §7).

Pro Vorlage: 3 Klimata × (1 + 3) Durchläufe = **12 Durchläufe**. Über 10
Vorlagen hinweg = **insgesamt 120 Durchläufe**.

---

## 3. Interne Struktur (HDF5-Schlüssel)

Die Schlüssel folgen einer 4-stufigen Hierarchie:

```
/<climate_tag>/<transport_tag>/run_<N>/<data_type>
```

Beispiel:

```
/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity
/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity_NoFlex
/hamburg_loc_hamburg_temp/no_transport/run_1/_metadata
```

`run_<N>` ist **1-basiert** (`run_1` … `run_3`).

---

## 4. Zeitindex und Spalten

- **Index:** ein minutenaufgelöster `DatetimeIndex`, `2020-01-01 00:00` →
  `2020-12-31 23:59`, `freq="min"` → **527 040 Zeilen** (2020 ist ein
  Schaltjahr: 366 × 1440). Jede Profilgruppe im Datensatz teilt sich diesen
  Index.
- **Spalten** einer Profilgruppe heißen `<LoadType>_<HHKey>`, wobei `HHKey` ist:
  - `House` — Aggregat des gesamten Hauses (Haushalt + Geräte auf Hausebene)
  - `HH1` — der einzelne Haushalt im Haus
- **Werte** sind die Momentangröße zu jeder Minute (Einheiten siehe §5) —
  *keine* Energiesummen.

Das Wetter jedes Durchlaufs ist das in §2 genannte **historische**
DWD-Temperaturjahr (nicht das Wetter von 2020); 2020 ist nur der Kalender, auf
den das Verhalten abgebildet wird.

> **Haustyp:** Alle Durchläufe verwenden
> `HT20 Single Family House (no heating / cooling)`.
> **Diese Profile enthalten daher keine Raumheiz- oder Raumkühllast.**
> Heiß-, Kalt- und Warmwasser sowie Gerätestrom sind enthalten; der thermische
> Gebäudebedarf nicht.

---

## 5. Datentypen innerhalb jeder `run_<N>`-Gruppe

### Energie- / Lastprofile (Minutenauflösung)
Jedes erscheint **zweimal**: das flexible Profil `<LoadType>` und sein
Basis-Gegenstück `<LoadType>_NoFlex` (siehe §8).

| Datentyp | Größe | Einheit (pro Minute) |
|----------|-------|----------------------|
| `Electricity` | Elektrische Wirkleistung | Watt |
| `Apparent` | Scheinleistung | VA |
| `Reactive` | Blindleistung | var |
| `Inner_Device_Heat_Gains` | Interne Wärmegewinne durch Geräte | Watt (thermisch) |
| `Cold_Water` | Kaltwasserentnahme | L/min |
| `Hot_water` | Heißwasserentnahme | L/min |
| `Warm_Water` | Warmwasserentnahme | L/min |
| `Gasoline` | Kraftstoffverbrauch | L/min |
| `None` | Geräte ohne zugeordneten Lasttyp | — |

### Anwesenheit / Aktivität
Anzahl der Personen je körperlichem Aktivitätsniveau, pro Minute:
`Person_Count_for__-_High`, `Person_Count_for__-_Low`,
`Person_Count_for__-_Outside`, `Person_Count_for__-_Unknown`.

### Verkehrskanäle — **nur in `home_charge_bus_cars_30km`-Durchläufen**
Pro Verkehrsmittel (`Bicycle_1/2/3`, `Car_1_22kW…`, `Car_2_22kW…`):
`Car_Location_-_<device>`, `Car_State_-_<device>`,
`Driving_Distance_-_<device>`, `State_of_charge_-_<device>`.
Zusätzlich `Electricity_for_Car_Charging` (+ `_NoFlex`) und `Elevator_Distance`
(+ `_NoFlex`).

### Flexibilitäts-Ereignisprotokoll
`FlexibilityEvents` — eine **Zeile pro Lastverschiebungs-Ereignis** (keine
Zeitreihe). Die Spalten beschreiben das flexible Gerät, seine Lasten und das
Verschiebungsfenster (`Device.*`, `EarliestStart.*`, `LatestStart.*`,
`TotalDuration`, …). Verschachtelte Felder (`Profiles`, `Device.Loads`) sind als
**JSON-codierte Zeichenketten** gespeichert; mit `json.loads` lassen sie sich
expandieren.

### Metadaten pro Durchlauf
`_metadata` — ein DataFrame mit **einer Zeile**: `task_id`, `template_key`,
`climate_tag`, `transport_tag`, `run_idx`, `seed`, `geographic_location`,
`temperature_profile`. Für **jeden** Durchlauf vorhanden.

---

## 6. `runs_metadata.csv`

Ein flacher Index aller Durchläufe mit 120 Zeilen (eine Zeile pro Durchlauf),
mit den Spalten: `task_id, template_key, climate_tag, transport_tag, run_idx,
seed, geographic_location, temperature_profile, hdf5_file, hdf5_path`.
Damit lässt sich nachschlagen, welche Datei + welcher Schlüsselpfad eine
bestimmte Konfiguration enthält, ohne jede HDF5-Datei zu öffnen. **Hinweis:**
Zur Sicherheit die Einträge gegen den tatsächlichen HDF5-Inhalt prüfen (§9),
wenn mit anderen Datensätzen kombiniert wird.

---

## 7. Zufallsstartwerte und Reproduzierbarkeit

Der Zufallsstartwert (Seed) jedes Durchlaufs ist in seiner `_metadata`-Gruppe
und in `runs_metadata.csv` gespeichert. Die Seeds werden deterministisch aus der
Konfiguration abgeleitet (MD5 von `combo_tag + run_idx`), sodass das Manifest —
und damit der beabsichtigte Datensatz — aus dem `SLP_Ade`-Code bei der
festgelegten pyLPG-Revision reproduzierbar ist.

---

## 8. Flexibilität: `<LoadType>` vs. `<LoadType>_NoFlex`

Die Flexibilitätsmodellierung war für alle Durchläufe **aktiviert**. Für jeden
Lasttyp gibt der LPG zwei zeitlich ausgerichtete Profile aus:

- `<LoadType>` — das **flexible** Profil, bei dem verschiebbare Geräte (z. B.
  Geschirrspüler, Autoladung) innerhalb ihrer erlaubten Fenster verschoben
  werden.
- `<LoadType>_NoFlex` — die **Basislinie**, derselbe Haushalt **ohne**
  angewandte Lastverschiebung.

Die elementweise Differenz `<LoadType> − <LoadType>_NoFlex` ist der modellierte
Demand-Response- / Lastverschiebungseffekt. Das `FlexibilityEvents`-Protokoll
erfasst die einzelnen Verschiebungen.

---

## 9. Vollständigkeit der Daten

**Alle 120 Durchlauf-Gruppen enthalten vollständige Profildaten** (überprüft
durch Durchlaufen jeder Datei: 120 Durchläufe, 0 leer). Jede
`/<climate>/<transport>/run_<N>/`-Gruppe enthält die Lastprofile, die
Anwesenheit, das Flexibilitätsprotokoll und — bei Verkehrsdurchläufen — die in
§5 beschriebenen Verkehrskanäle.

Als Absicherung (z. B. beim Kombinieren mit anderen Sweeps) prüfen, ob unter
einem Durchlaufpfad tatsächlich eine Profilgruppe existiert, statt sich allein
auf `runs_metadata.csv` zu verlassen:

```python
def run_has_data(store, run_path):
    return f"{run_path}/Electricity" in store  # ein beliebiger erwarteter Lasttyp
```

---

## 10. Ladebeispiele (Python)

Benötigt `pandas` und `tables` (PyTables).

```python
import pandas as pd

path = "CHR07_Single_with_work.h5"

# --- alles auflisten -------------------------------------------------------
with pd.HDFStore(path, mode="r") as store:
    for key in store.keys():
        print(key)

# --- ein Profil laden ------------------------------------------------------
with pd.HDFStore(path, mode="r") as store:
    el = store["/hamburg_loc_hamburg_temp/home_charge_bus_cars_30km/run_2/Electricity"]
# el.index -> Minuten-DatetimeIndex; el.columns -> ['Electricity_House', 'Electricity_HH1']
print(el.shape, list(el.columns))

# --- alle Durchläufe mit tatsächlichen Daten durchlaufen -------------------
with pd.HDFStore(path, mode="r") as store:
    run_paths = sorted({ "/".join(k.split("/")[:4]) for k in store.keys()
                         if len(k.split("/")) >= 5 })
    for rp in run_paths:
        if f"{rp}/Electricity" not in store:
            continue                     # leere Durchlauf-Gruppen überspringen (§9)
        meta = store[f"{rp}/_metadata"].iloc[0]
        elec = store[f"{rp}/Electricity"]["Electricity_HH1"]
        print(rp, "seed=", meta["seed"], "mean W=", round(elec.mean(), 1))

# --- der flache Durchlauf-Index --------------------------------------------
runs = pd.read_csv("runs_metadata.csv")
```

---

## 11. Herkunft (Provenienz)

- **Generator:** LoadProfileGenerator (LPG), gesteuert über pyLPG
  (`SLP_Ade`-Sweep).
- **Simulationszeitraum:** gesamtes Jahr 2020, 1-Minuten-Auflösung.
- **Flexibilität:** aktiviert (siehe §8). **Idle-Modus:** aktiviert (eine
  Ersatzaktivität „Idle“, die verhindert, dass die Verhaltens-Engine abbricht,
  wenn ein Haushalt — typischerweise einer mit kleinen Kindern — vorübergehend
  keine verfügbare Aktivität hat).
- **Haustyp:** HT20 Single Family House, ohne Heizung/Kühlung (§4).
- **Vorlagen, Klimata, Verkehr, Seeds:** wie oben beschrieben und in jeder
  `_metadata`-Gruppe / in `runs_metadata.csv` festgehalten.
