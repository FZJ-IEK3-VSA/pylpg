from lpgadapter import *


# noinspection PyPep8,PyUnusedLocal
class LoadTypes:
    Air_Conditioning_Load = "Air Conditioning Load"
    Apparent = "Apparent"
    Car_Charging_Electricity = "Car Charging Electricity"
    Coal = "Coal"
    Cold_Water = "Cold Water"
    Direct_Solar_Radiation = "Direct Solar Radiation"
    Electricity = "Electricity"
    Elevator_Distance = "Elevator Distance"
    Gas = "Gas"
    Gasoline = "Gasoline"
    Heat_Buffer_Energy_Balance = "Heat Buffer Energy Balance"
    Hot_water = "Hot water"
    Hydrogen = "Hydrogen"
    Inner_Device_Heat_Gains = "Inner Device Heat Gains"
    Reactive = "Reactive"
    Space_Heating = "Space Heating"
    Temperature = "Temperature"
    Total_Solar_Radiation_Direct_Indirect = "Total Solar Radiation (Direct + Indirect)"
    Warm_Water = "Warm Water"
    Workplace_Electricity = "Workplace Electricity"


# noinspection PyPep8,PyUnusedLocal
class HouseTypes:
    HT01_House_with_a_10kWh_Battery_and_a_fuel_cell_battery_charger_5_MWh_yearly_space_heating_gas_heating = "HT01 House with a 10kWh Battery and a fuel cell battery charger, 5 MWh yearly space heating, gas heating"
    HT02_House_with_a_5_kWh_Battery_and_a_50_m2_Photovolatic_Array_5MWh_space_heating_gas_heating = "HT02 House with a 5 kWh Battery and a 50 m2 Photovolatic Array, 5MWh space heating, gas heating"
    HT03_House_with_a_solar_thermal_System_and_300_L_storage_tank_gas_heating = "HT03 House with a solar thermal System and 300 L storage tank, gas heating"
    HT04_Photovoltaic_System_5_kW_no_space_heating_gas_warm_water_heater = "HT04 Photovoltaic System 5 kW, no space heating, gas warm water heater"
    HT05_House_with_a_5_kWh_Battery_and_a_50_m2_Photovolatic_Array_5MWh_space_heating_electric_heating = "HT05 House with a 5 kWh Battery and a 50 m2 Photovolatic Array, 5MWh space heating, electric heating"
    HT06_Normal_house_with_15_000_kWh_Heating_Continuous_Flow_Gas_Heating = "HT06 Normal house with 15.000 kWh Heating, Continuous Flow Gas Heating"
    HT07_Normal_house_with_15_000_kWh_Heating_and_5_000_kWh_Cooling_Electric_Air_Conditioning_Continuous_Flow_Gas_Heating = "HT07 Normal house with 15.000 kWh Heating and 5.000 kWh Cooling, Electric Air Conditioning, Continuous Flow Gas Heating"
    HT08_Normal_house_with_15_000_kWh_Heating_and_5_000_kWh_Cooling_Continuous_Flow_Electric_Heat_Pump = "HT08 Normal house with 15.000 kWh Heating and 5.000 kWh Cooling, Continuous Flow Electric Heat Pump"
    HT09_Normal_house_with_20_000_kWh_Heating_Continuous_Gas_Heating = "HT09 Normal house with 20.000 kWh Heating, Continuous Gas Heating"
    HT10_Normal_house_with_20_000_kWh_Heating_5_000_kWh_Cooling_Electric_Air_Conditioning_Continuous_Flow_Gas_Heating = "HT10 Normal house with 20.000 kWh Heating, 5.000 kWh Cooling, Electric Air Conditioning, Continuous Flow Gas Heating"
    HT11_Normal_house_with_20_000_kWh_Heating_no_cooling_Continuous_Flow_Heat_pump = "HT11 Normal house with 20.000 kWh Heating, no cooling, Continuous Flow Heat pump"
    HT12_Normal_house_with_30_000_kWh_Continuous_Flow_Gas_Heating = "HT12 Normal house with 30.000 kWh Continuous Flow Gas Heating"
    HT13_Normal_house_with_30_000_kWh_Continous_Flow_Gas_Heating_and_10_000_kWh_Electric_Cooling = "HT13 Normal house with 30.000 kWh Continous Flow Gas Heating and 10.000 kWh Electric Cooling"
    HT14_Normal_house_with_5_000_kWh_Air_Conditioning_no_Heating_Electric_Warm_Water = "HT14 Normal house with 5.000 kWh Air Conditioning, no Heating, Electric Warm Water"
    HT15_Normal_house_with_5_000_kWh_Space_heating_Continuous_Flow_Gas_Heater = "HT15 Normal house with 5.000 kWh Space heating, Continuous Flow Gas Heater"
    HT16_Normal_house_with_20_000_kWh_Heating_Continuous_Flow_Heat_Pump = "HT16 Normal house with 20.000 kWh Heating, Continuous Flow Heat Pump"
    HT18_Normal_House_with_15_000_kWh_Gas_Heating_and_a_hot_water_storage_tank = "HT18 Normal House with 15.000 kWh Gas Heating and a hot water storage tank"
    HT19_Normal_House_with_15_000_kWh_Heat_Demand_Heat_Pump_with_COP3_and_Hot_Water_Storage_Tank = "HT19 Normal House with 15.000 kWh Heat Demand, Heat Pump with COP3 and Hot Water Storage Tank"
    HT20_Single_Family_House_no_heating_cooling = "HT20 Single Family House (no heating/cooling)"
    HT22_Big_Multifamily_House_no_heating_cooling = "HT22 Big Multifamily House (no heating/cooling)"
    HT23_No_Infrastructure_at_all = "HT23 No Infrastructure at all"


# noinspection PyPep8,PyUnusedLocal
class Households:
    CHR01_Couple_both_at_Work: JsonReference = JsonReference("CHR01 Couple both at Work",  StrGuid("516a33ab-79e1-4221-853b-967fc11cc85a"))
    CHR02_Couple_30_64_age_with_work: JsonReference = JsonReference("CHR02 Couple, 30 - 64 age, with work",  StrGuid("1a7c45dc-272a-4836-bca9-076bd200486a"))
    CHR03_Family_1_child_both_at_work: JsonReference = JsonReference("CHR03 Family, 1 child, both at work",  StrGuid("e41a31b5-8eb1-4ec1-8875-49d0d4441f33"))
    CHR04_Couple_30_64_years_1_at_work_1_at_home: JsonReference = JsonReference("CHR04 Couple, 30 - 64 years, 1 at work, 1 at home",  StrGuid("5da74745-b625-4311-8f69-6ef3351207c5"))
    CHR05_Family_3_children_both_with_work: JsonReference = JsonReference("CHR05 Family, 3 children, both with work",  StrGuid("f0c151a4-ee8d-4a23-9cd1-6858d258aef8"))
    CHR06_Jak_Jobless: JsonReference = JsonReference("CHR06 Jak Jobless",  StrGuid("c1248c1a-a654-486c-8e20-2435dc0cad4d"))
    CHR07_Single_with_work: JsonReference = JsonReference("CHR07 Single with work",  StrGuid("20173a11-f1ac-44ef-952d-4c5a65ac3988"))
    CHR08_Single_woman_2_children_with_work: JsonReference = JsonReference("CHR08 Single woman, 2 children, with work",  StrGuid("e30d5760-b89d-4087-ac5a-c33b3250b000"))
    CHR09_Single_woman_30_64_years_with_work: JsonReference = JsonReference("CHR09 Single woman, 30 - 64 years, with work",  StrGuid("f6309e9c-af83-44e8-9381-12766e6dc8a4"))
    CHR10_Single_man_30_64_age_shift_worker: JsonReference = JsonReference("CHR10 Single man, 30 - 64 age, shift worker",  StrGuid("2b85a956-a211-4b39-9c66-41144394a3fe"))
    CHR11_Student_Female_Philosophy: JsonReference = JsonReference("CHR11 Student, Female, Philosophy",  StrGuid("57b0bafd-93ce-4ae1-a0ec-568eb41e3a88"))
    CHR12_Student_2_Male_Philosophy: JsonReference = JsonReference("CHR12 Student 2, Male, Philosophy",  StrGuid("d4fb5502-660e-4d1e-bc9f-ca07dc4882ef"))
    CHR13_Student_with_Work: JsonReference = JsonReference("CHR13 Student with Work",  StrGuid("f2a97869-7a3d-4efc-8565-51b3c43ba183"))
    CHR14_3_adults_Couple_30_64_years_both_at_work_Senior_at_home: JsonReference = JsonReference("CHR14 3 adults: Couple, 30- 64 years, both at work + Senior at home",  StrGuid("65bd2299-3174-4531-b4fd-fc327b6fc3f6"))
    CHR15_Multigenerational_Home_working_couple_2_children_2_seniors: JsonReference = JsonReference("CHR15 Multigenerational Home: working couple, 2 children, 2 seniors",  StrGuid("f1470a33-c934-4203-b7cb-184b6dc07633"))
    CHR16_Couple_over_65_years: JsonReference = JsonReference("CHR16 Couple over 65 years",  StrGuid("8260de8b-2fa6-4a36-bf40-5304afb2fc1a"))
    CHR17_Shiftworker_Couple: JsonReference = JsonReference("CHR17 Shiftworker Couple",  StrGuid("61668b2d-0559-4dd2-815d-9d2725222690"))
    CHR18_Family_2_children_parents_without_work: JsonReference = JsonReference("CHR18 Family, 2 children, parents without work",  StrGuid("0d17c119-8566-4eac-b610-33bd6f764878"))
    CHR19_Couple_30_64_years_both_at_work_with_homehelp: JsonReference = JsonReference("CHR19 Couple, 30 - 64 years, both at work, with homehelp",  StrGuid("919ccda6-7a07-49e3-a4b0-bbba2410c70e"))
    CHR20_one_at_work_one_work_home_3_children: JsonReference = JsonReference("CHR20 one at work, one work home, 3 children",  StrGuid("68edfea5-f8d4-4a6f-a2ae-313ee2e41624"))
    CHR21_Couple_30_64_years_shift_worker: JsonReference = JsonReference("CHR21 Couple, 30 - 64 years, shift worker",  StrGuid("fd1406f4-1f65-43ba-9504-9425f6eb01ef"))
    CHR22_Single_woman_1_child_with_work: JsonReference = JsonReference("CHR22 Single woman, 1 child, with work",  StrGuid("d97ae616-e1ba-468a-85a0-627b8cc5e1cd"))
    CHR23_Single_man_over_65_years: JsonReference = JsonReference("CHR23 Single man over 65 years",  StrGuid("92f23b58-d357-403f-ad30-f7ae63576893"))
    CHR24_Single_woman_over_65_years: JsonReference = JsonReference("CHR24 Single woman over 65 years",  StrGuid("df908a28-6d5b-4d90-8a16-d0442c1c32e1"))
    CHR25_Single_woman_under_30_years_with_work: JsonReference = JsonReference("CHR25 Single woman under 30 years with work",  StrGuid("a4e53285-125a-4eed-b37a-268f081ae444"))
    CHR26_Single_woman_under_30_years_without_work: JsonReference = JsonReference("CHR26 Single woman under 30 years without work",  StrGuid("b8bdef97-556a-447d-8d46-2deda2516057"))
    CHR27_Family_both_at_work_2_children: JsonReference = JsonReference("CHR27 Family both at work, 2 children",  StrGuid("dc267b29-cfec-476a-9399-2014058f36f6"))
    CHR28_Single_man_under_30_years_without_work: JsonReference = JsonReference("CHR28 Single man under 30 years without work",  StrGuid("b833ceb3-5a19-419f-9835-b75b52f8be7c"))
    CHR29_Single_man_under_30_years_with_work: JsonReference = JsonReference("CHR29 Single man under 30 years with work",  StrGuid("e3a959e4-562a-4b15-a820-6159e2b2dddc"))
    CHR30_Single_Retired_Man: JsonReference = JsonReference("CHR30 Single, Retired Man",  StrGuid("4fb7efde-3cef-4eb2-8ebe-e89f3ac87aed"))
    CHR31_Single_Retired_Woman: JsonReference = JsonReference("CHR31 Single, Retired Woman",  StrGuid("fee0cdc2-22f7-45c4-bf01-3aaf65866773"))
    CHR32_Couple_under_30_years_without_work: JsonReference = JsonReference("CHR32 Couple under 30 years without work",  StrGuid("0dad3b57-f255-4c9c-9096-eef45ca3199c"))
    CHR33_Couple_under_30_years_with_work: JsonReference = JsonReference("CHR33 Couple under 30 years with work",  StrGuid("5220db46-4d23-410f-af0b-ab11ad1279bc"))
    CHR34_Couple_under_30_years_one_at_work_one_at_home: JsonReference = JsonReference("CHR34 Couple under 30 years, one at work, one at home",  StrGuid("25ce714a-9f93-4f8e-ba03-37b76a0294da"))
    CHR35_Single_woman_30_64_years_with_work: JsonReference = JsonReference("CHR35 Single woman, 30 - 64 years, with work",  StrGuid("3368c3e9-60f2-49e4-b79c-b1febc74485b"))
    CHR36_Single_woman_30_64_years_without_work: JsonReference = JsonReference("CHR36 Single woman, 30 - 64 years, without work",  StrGuid("d17d88c9-666d-4d24-aac1-78bef65c53a1"))
    CHR37_Single_man_30_64_years_with_work: JsonReference = JsonReference("CHR37 Single man, 30 - 64 years, with work",  StrGuid("86a5cf7a-e9c7-4f59-8a6c-f9cfe2b7fe03"))
    CHR38_Single_man_30_64_years_without_work: JsonReference = JsonReference("CHR38 Single man, 30 - 64 years, without work",  StrGuid("2335b994-d7fa-41c1-af93-0c401d192122"))
    CHR39_Couple_30_64_years_with_work: JsonReference = JsonReference("CHR39 Couple, 30 - 64 years, with work",  StrGuid("afc3244b-2988-4f65-8c73-f4fcc1f531d2"))
    CHR40_Couple_30_64_years_without_work: JsonReference = JsonReference("CHR40 Couple, 30 - 64 years, without work",  StrGuid("7cf13644-b837-4d93-9a90-0e32a295e4a9"))
    CHR41_Family_with_3_children_both_at_work: JsonReference = JsonReference("CHR41 Family with 3 children, both at work",  StrGuid("e5355495-afd3-490f-9dd0-3839d1f7f1d0"))
    CHR42_Single_man_with_2_children_with_work: JsonReference = JsonReference("CHR42 Single man with 2 children, with work",  StrGuid("23fb7efd-abcf-4caa-8434-bb6cfc87fdaf"))
    CHR43_Single_man_with_1_child_with_work: JsonReference = JsonReference("CHR43 Single man with 1 child, with work",  StrGuid("130aedcf-e0cc-4335-a6c8-594189fffefb"))
    CHR44_Family_with_2_children_1_at_work_1_at_home: JsonReference = JsonReference("CHR44 Family with 2 children, 1 at work, 1 at home",  StrGuid("c2ea56a1-6413-4bc3-9b0a-d0d5705434e1"))
    CHR45_Family_with_1_child_1_at_work_1_at_home: JsonReference = JsonReference("CHR45 Family with 1 child, 1 at work, 1 at home",  StrGuid("bab73822-78ce-4a3a-9164-3e0942fb6508"))
    CHR46_Single_woman_1_child_without_work: JsonReference = JsonReference("CHR46 Single woman, 1 child, without work",  StrGuid("442a31e8-ccb6-457a-8436-8c4d6acabc23"))
    CHR47_Single_woman_2_children_without_work: JsonReference = JsonReference("CHR47 Single woman, 2 children, without work",  StrGuid("820d9de7-4fc7-42af-bf7f-701a35675063"))
    CHR48_Family_with_2_children_without_work: JsonReference = JsonReference("CHR48 Family with 2 children, without work",  StrGuid("567c3426-85dd-4ab5-917a-9f28f0cc9f76"))
    CHR49_Family_with_1_child_without_work: JsonReference = JsonReference("CHR49 Family with 1 child, without work",  StrGuid("3c10c5de-b246-461a-b2bb-589ad80da159"))
    CHR50_Single_woman_with_3_children_without_work: JsonReference = JsonReference("CHR50 Single woman with 3 children, without work",  StrGuid("4c5fc522-9472-4b37-b7dc-1d72a24c2df1"))
    CHR51_Couple_over_65_years_II: JsonReference = JsonReference("CHR51 Couple over 65 years II",  StrGuid("114871cb-345a-47c0-9138-6322367333d6"))
    CHR52_Student_Flatsharing: JsonReference = JsonReference("CHR52 Student Flatsharing",  StrGuid("debf4669-1be0-44a1-8010-30a7e8290559"))
    CHR53_2_Parents_1_Working_2_Children: JsonReference = JsonReference("CHR53 2 Parents, 1 Working, 2 Children",  StrGuid("fe8adddd-8409-4f01-9ccc-f85dd018eff8"))
    CHR54_Retired_Couple_no_work: JsonReference = JsonReference("CHR54 Retired Couple, no work",  StrGuid("b22ecb7c-4422-4e72-8af0-0f2c5d28441a"))
    CHR55_Couple_with_work_around_40: JsonReference = JsonReference("CHR55 Couple with work around 40",  StrGuid("b4451879-164c-4416-bd20-502fb471ccdc"))
    CHR56_Couple_with_2_children_husband_at_work: JsonReference = JsonReference("CHR56 Couple with 2 children, husband at work",  StrGuid("11195315-953b-46de-9572-ec7c10b2ce5e"))
    CHR57_Family_with_2_Children_Man_at_work: JsonReference = JsonReference("CHR57 Family with 2 Children, Man at work",  StrGuid("db51a7ef-16e9-49bc-8dec-1406a664d641"))
    CHR58_Retired_Couple_no_work_no_cooking: JsonReference = JsonReference("CHR58 Retired Couple, no work, no cooking",  StrGuid("747120ae-5203-4ed7-9bb5-b56a2075c5f5"))
    CHR59_Family_3_children_parents_without_work: JsonReference = JsonReference("CHR59 Family, 3 children, parents without work",  StrGuid("f497f10f-6628-4b34-8ce3-8daf8660e6a5"))
    CHR60_Family_1_toddler_one_at_work_one_at_home: JsonReference = JsonReference("CHR60 Family, 1 toddler, one at work, one at home",  StrGuid("e045f4b5-3086-4389-ba23-c026e40900c9"))
    CHR61_Family_1_child_both_at_work_early_living_pattern: JsonReference = JsonReference("CHR61 Family, 1 child, both at work, early living pattern",  StrGuid("e7cb1be5-caac-4087-83e8-c181911a68e2"))
    CHS01_Couple_with_2_Children_Dad_Employed: JsonReference = JsonReference("CHS01 Couple with 2 Children, Dad Employed",  StrGuid("148a1c21-2a3a-49bf-93aa-20ac0e89724e"))
    CHS04_Retired_Couple_no_work: JsonReference = JsonReference("CHS04 Retired Couple, no work",  StrGuid("1fd8d33c-97b2-4934-a681-d6b10446e462"))
    CHS12_Shiftworker_Couple: JsonReference = JsonReference("CHS12 Shiftworker Couple",  StrGuid("bc09654d-e1bf-4f66-b5f6-e97476455537"))
    OR01_Single_Person_Office: JsonReference = JsonReference("OR01 Single Person Office",  StrGuid("65e73536-0d89-407c-bb47-00f67a9a0945"))


# noinspection PyPep8,PyUnusedLocal
class GeographicLocations:
    Finland_Helsinki: JsonReference = JsonReference("(Finland) Helsinki",  StrGuid("ddb2bae5-d41a-494d-b5df-80eee767fc20"))
    France_Carpentras: JsonReference = JsonReference("(France) Carpentras",  StrGuid("9d92f84e-4f71-4476-a307-3480cc2c1530"))
    France_Limoges: JsonReference = JsonReference("(France) Limoges",  StrGuid("2a16d9bd-87b5-4ddb-8810-6c9a6120455e"))
    France_Palaiseau: JsonReference = JsonReference("(France) Palaiseau",  StrGuid("45b3899c-2c0d-43d1-b83d-5c3f8ae878b8"))
    Germany_Berlin: JsonReference = JsonReference("(Germany) Berlin",  StrGuid("484ea885-45de-4967-8d52-9d765f886692"))
    Germany_ChemLowLight: JsonReference = JsonReference("(Germany) ChemLowLight",  StrGuid("596a7f65-c154-4554-b6b4-84c43c161af8"))
    Germany_Chemnitz: JsonReference = JsonReference("(Germany) Chemnitz",  StrGuid("eddeb22c-fbd4-44c1-bf2d-fbde3342f1bd"))
    Germany_ChemNoBridge: JsonReference = JsonReference("(Germany) ChemNoBridge",  StrGuid("f6964917-ae96-4ff4-8b06-eaadea2b1dca"))
    Germany_Freiburg: JsonReference = JsonReference("(Germany) Freiburg",  StrGuid("515806af-d667-4994-b93d-8366c970e1c8"))
    Germany_Hamburg: JsonReference = JsonReference("(Germany) Hamburg",  StrGuid("4535a43c-b165-4ca8-9aa5-8ccaf42bac36"))
    Germany_Kassel: JsonReference = JsonReference("(Germany) Kassel",  StrGuid("5f665a7f-4edd-4166-8427-bbf3d537cf59"))
    Germany_Muenchen: JsonReference = JsonReference("(Germany) München",  StrGuid("93dd3ee0-254f-4cca-99f0-428324bb7a9f"))
    Germany_Potsdam: JsonReference = JsonReference("(Germany) Potsdam",  StrGuid("6a7d9aed-0a96-49ea-a981-291cf07e3d20"))
    Germany_Stuttgart: JsonReference = JsonReference("(Germany) Stuttgart",  StrGuid("86ebf966-ca23-43a4-8035-4b075307920b"))
    Greece_Finokalia: JsonReference = JsonReference("(Greece) Finokalia",  StrGuid("3f0a181e-32c9-4864-9bbd-dc7c5b499130"))
    Greece_Patras: JsonReference = JsonReference("(Greece) Patras",  StrGuid("438d5d87-d188-40c2-9fb2-32e293176c55"))
    Greece_Thessaloniki: JsonReference = JsonReference("(Greece) Thessaloniki",  StrGuid("8381810d-221b-4dc3-86d4-d43ee256568d"))
    Italy_Mailand: JsonReference = JsonReference("(Italy) Mailand",  StrGuid("913cb1d5-d5cb-4284-9aad-30695a8d4f15"))
    Italy_Palermo: JsonReference = JsonReference("(Italy) Palermo",  StrGuid("161b2990-2f3f-4a70-9aed-f189699d8797"))
    Italy_Rom: JsonReference = JsonReference("(Italy) Rom",  StrGuid("355e2af2-fe6a-4977-b59b-ce0b04da3ff2"))


# noinspection PyPep8,PyUnusedLocal
class TemperatureProfiles:
    Berlin_Germany_1996_from_Deutscher_Wetterdienst_DWD_www_dwd_de: JsonReference = JsonReference("Berlin, Germany 1996 from Deutscher Wetterdienst DWD (www.dwd.de)",  StrGuid("ec337ba6-60a1-404b-9db0-9be52c9e5702"))
    Dresden_Germany_2000_from_Deutscher_Wetterdienst_DWD_www_dwd_de: JsonReference = JsonReference("Dresden, Germany 2000 from Deutscher Wetterdienst DWD (www.dwd.de)",  StrGuid("532c98ac-e4ae-406e-b96c-67c8cecd5fa2"))
    Hamburg_Germany_1940_from_Deutscher_Wetterdienst_DWD_www_dwd_de: JsonReference = JsonReference("Hamburg, Germany 1940 from Deutscher Wetterdienst DWD (www.dwd.de)",  StrGuid("9d9447f8-5070-4256-a826-a1e187286c85"))
    Hamburg_Germany_2007_from_Deutscher_Wetterdienst_DWD_www_dwd_de: JsonReference = JsonReference("Hamburg, Germany 2007 from Deutscher Wetterdienst DWD (www.dwd.de)",  StrGuid("5cee108e-4126-41c2-9601-e867d597a96b"))


# noinspection PyPep8,PyUnusedLocal
class TransportationDeviceSets:
    Bus_and_one_slow_Car: JsonReference = JsonReference("Bus and one slow Car",  StrGuid("6ac74bd0-bacd-4b39-b84a-dc7ae16702c9"))
    Bus_and_two_slow_Cars: JsonReference = JsonReference("Bus and two slow Cars",  StrGuid("f90fece2-901a-4419-8a6b-a0ed4ed6ceff"))


# noinspection PyPep8,PyUnusedLocal
class ChargingStationSets:
    Charging_At_Home_with_00_5_kW: JsonReference = JsonReference("Charging At Home with 00.5 kW",  StrGuid("0a42e424-2f0d-40db-b257-82a5fc010567"))
    Charging_At_Home_with_03_7_kW: JsonReference = JsonReference("Charging At Home with 03.7 kW",  StrGuid("38e3a15d-d6f5-4f51-a16a-da287d14608f"))
    Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity: JsonReference = JsonReference("Charging At Home with 03.7 kW, output results to Car Electricity",  StrGuid("223f0577-9249-4293-a849-ea12e2033377"))
    Charging_At_Home_with_11_kW: JsonReference = JsonReference("Charging At Home with 11 kW",  StrGuid("78dae308-24c4-45cc-8bdf-b001d61f45c2"))
    Charging_At_Home_with_22_kW: JsonReference = JsonReference("Charging At Home with 22 kW",  StrGuid("c96bf5dd-d3ad-4212-acde-badc43d5ffe3"))
    Charging_At_Work_with_00_5_kW: JsonReference = JsonReference("Charging At Work with 00.5 kW",  StrGuid("570e3cea-8b67-404d-9426-ef782773edb0"))
    Charging_At_Work_with_03_7_kW: JsonReference = JsonReference("Charging At Work with 03.7 kW",  StrGuid("32b071ad-c49c-47e8-9c5e-1d05f7f46fcd"))
    Charging_At_Work_with_11_kW: JsonReference = JsonReference("Charging At Work with 11 kW",  StrGuid("a6b62baf-d164-407e-858b-75a4ad8f36ca"))
    Charging_At_Work_with_22_kW: JsonReference = JsonReference("Charging At Work with 22 kW",  StrGuid("e24180ef-852e-4361-8fc8-0eb01bba096b"))


# noinspection PyPep8,PyUnusedLocal
class TravelRouteSets:
    Travel_Route_Set_for_30km_to_Work: JsonReference = JsonReference("Travel Route Set for 30km to Work",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))
    Travel_Route_Set_for_5km_Difference: JsonReference = JsonReference("Travel Route Set for 5km Difference",  StrGuid("a60747ab-3427-43f8-9a61-3233f332075a"))


# noinspection PyPep8,PyUnusedLocal
class Houses:
    CHH01_02_and_03_in_HT02: JsonReference = JsonReference("CHH01, 02 and 03... in HT02",  StrGuid("75077e03-3e4a-4c48-aa0f-2438a9f819f4"))
    CHR03_in_HT02: JsonReference = JsonReference("CHR03 in HT02",  StrGuid("2720a742-5b29-4846-9b31-464e8ea03df7"))
    CHR03_in_HT04: JsonReference = JsonReference("CHR03 in HT04",  StrGuid("a9ceec7f-e47c-4b8d-bc2b-bc29b3285f18"))
    CHR07_in_HT04_with_Car_05_km_to_work_3_7_kW_Charging_at_home: JsonReference = JsonReference("CHR07 in HT04 with Car, 05 km to work, 3.7 kW Charging at home",  StrGuid("aa849a94-dbaf-45f4-8660-954850768aeb"))
    CHR07_in_HT04_with_Car_05_km_to_work_3_7_kW_Charging_at_work: JsonReference = JsonReference("CHR07 in HT04 with Car, 05 km to work, 3.7 kW Charging at work",  StrGuid("340792aa-f55c-48e9-92b1-73463bcf5afc"))
    CHR07_in_HT04_with_Car_30_km_to_work_22kW_Charging_at_home: JsonReference = JsonReference("CHR07 in HT04 with Car, 30 km to work, 22kW Charging at home",  StrGuid("3ebeb519-f62e-4db7-84fd-744af7f24bca"))
    CHR07_in_HT04_with_Car_30_km_to_work_22kW_Charging_at_work: JsonReference = JsonReference("CHR07 in HT04 with Car, 30 km to work, 22kW Charging at work",  StrGuid("4e465dd6-677f-4600-a17f-efc1bc1a1f98"))
    CHR07_in_HT04_with_Car_30_km_to_work_3_7kW_Charging_at_home: JsonReference = JsonReference("CHR07 in HT04 with Car, 30 km to work, 3.7kW Charging at home",  StrGuid("cb521436-0a85-4f69-aef5-c1ca1b8781c1"))
    CHR07_in_HT04_with_Car_30_km_to_work_3_7kW_Charging_at_work: JsonReference = JsonReference("CHR07 in HT04 with Car, 30 km to work, 3.7kW Charging at work",  StrGuid("03ae1815-a810-4c91-89aa-7bcd10f9068f"))
    CHS01_Familiy_2_Children_in_HT06_normal_detached_house: JsonReference = JsonReference("CHS01 (Familiy, 2 Children) in HT06 (normal detached house)",  StrGuid("c8e6af1a-6aba-4c7e-932e-5a40cdbd693b"))
    H01_in_HT02: JsonReference = JsonReference("H01 in HT02",  StrGuid("de274d56-0280-4631-b05d-f6641caf1a24"))
    H01_in_HT03: JsonReference = JsonReference("H01 in HT03",  StrGuid("90e20bf2-ddc4-4b9d-b442-aa5b10475e4d"))
    H01_in_HT04: JsonReference = JsonReference("H01 in HT04",  StrGuid("262466a9-5168-4493-bc68-101ede2f83d3"))
    H01_in_HT05: JsonReference = JsonReference("H01 in HT05",  StrGuid("3fab0bc6-8a25-4764-8eab-42670137eaa5"))
    H01_in_HT06: JsonReference = JsonReference("H01 in HT06",  StrGuid("571b24ee-09c3-4cc2-a6a5-7e09337e776a"))
    H01_in_HT07: JsonReference = JsonReference("H01 in HT07",  StrGuid("efdfee1e-4ff7-438d-975b-e6465cfe5434"))
    H01_in_HT08: JsonReference = JsonReference("H01 in HT08",  StrGuid("ba39951f-41fe-40ef-a274-15cdf8ca78a7"))
    H01_in_HT09: JsonReference = JsonReference("H01 in HT09",  StrGuid("5dd1a988-f63f-4c7b-a9d5-878c864b944c"))
    H01_in_HT10: JsonReference = JsonReference("H01 in HT10",  StrGuid("0184a80c-04df-4418-ba47-56f71743a944"))
    H01_in_HT11: JsonReference = JsonReference("H01 in HT11",  StrGuid("6ec74659-5d98-47f1-a6ae-55e3978912f9"))
    H01_in_HT12: JsonReference = JsonReference("H01 in HT12",  StrGuid("c3b25334-e265-4dc8-816a-0a25617cac06"))
    H01_in_HT13: JsonReference = JsonReference("H01 in HT13",  StrGuid("ce282069-8b2d-4e38-9bc6-4d0749880b40"))
    H01_in_HT14: JsonReference = JsonReference("H01 in HT14",  StrGuid("de57236a-2cb6-46ab-9631-c130e0897033"))
    H01_in_HT15: JsonReference = JsonReference("H01 in HT15",  StrGuid("93a0463c-1819-4286-9bed-d6acff91dd5d"))
    H01_in_HT16: JsonReference = JsonReference("H01 in HT16",  StrGuid("4e3d306e-6622-414a-9fa1-8be88343053c"))
    H01_in_HT18: JsonReference = JsonReference("H01 in HT18",  StrGuid("68d7f93a-b15e-4f71-bb61-a3650772dabc"))
    H01_in_HT19: JsonReference = JsonReference("H01 in HT19",  StrGuid("f86dacc1-29bc-4d0e-ae9c-807d24b04cef"))
    SHO01_CHS01_in_HT06: JsonReference = JsonReference("SHO01 CHS01 in HT06",  StrGuid("13173e9b-3025-48f8-abe2-df647afef99a"))
    SHO01I_CHS01_in_HT06: JsonReference = JsonReference("SHO01I CHS01 in HT06",  StrGuid("cc39df66-a6c8-48f5-afb7-6cf1935307e8"))
    SHO04_CHS04_in_HT06: JsonReference = JsonReference("SHO04 CHS04 in HT06",  StrGuid("b7affde3-79e1-4822-9ec8-59c4b5a21fec"))
    SHO04I_CHS04_in_HT06: JsonReference = JsonReference("SHO04I CHS04 in HT06",  StrGuid("02f23a76-5a6b-488a-8f6f-79d0f7172174"))
    SHO12_CHS12_in_HT06: JsonReference = JsonReference("SHO12 CHS12 in HT06",  StrGuid("b65cbd06-10c8-4176-b101-59f5e5f19d43"))
    SHO12I_CHS12_in_HT06: JsonReference = JsonReference("SHO12I CHS12 in HT06",  StrGuid("0d097bc8-4497-4ea5-b234-69f90c81af33"))

