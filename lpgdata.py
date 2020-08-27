from lpgpythonbindings import *


# noinspection PyPep8,PyUnusedLocal
class LoadTypes:
    Air_Conditioning_Load = "Air Conditioning Load"
    Apparent = "Apparent"
    Coal = "Coal"
    Cold_Water = "Cold Water"
    Direct_Solar_Radiation = "Direct Solar Radiation"
    Electricity = "Electricity"
    Electricity_for_Car_Charging = "Electricity for Car Charging"
    Electricity_for_Heating = "Electricity for Heating"
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
    HT21_Normal_House_with_15_000_kWh_Heat_Demand_Heat_Pump_with_COP3_and_Hot_Water_Storage_Tank_Heat_Pump_Electricity = "HT21 Normal House with 15.000 kWh Heat Demand, Heat Pump with COP3 and Hot Water Storage Tank, Heat Pump Electricity"
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
    x_CHR07_Single_with_work_01: JsonReference = JsonReference("x CHR07 Single with work 01",  StrGuid("62cfd5f3-9677-4e8c-a5d4-d219b9b1985a"))
    x_CHR11_Student_Female_Philosophy_01: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 01",  StrGuid("d841ae0b-372c-4492-b7a6-d1874c5e1b82"))
    x_CHR11_Student_Female_Philosophy_02: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 02",  StrGuid("f2403f15-ca5b-46a4-8a48-4aab8d0b36ed"))
    x_CHR11_Student_Female_Philosophy_03: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 03",  StrGuid("ad86be34-4162-4e3f-a2ae-5d4c56d20f04"))
    x_CHR11_Student_Female_Philosophy_04: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 04",  StrGuid("7e92e006-3937-4e46-a95c-f7a8f58c65ea"))
    x_CHR11_Student_Female_Philosophy_05: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 05",  StrGuid("7e8cf164-5585-4600-bc7e-c880177819db"))
    x_CHR11_Student_Female_Philosophy_06: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 06",  StrGuid("c0281009-f932-4e1e-b56c-3fcaad0c795e"))
    x_CHR11_Student_Female_Philosophy_07: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 07",  StrGuid("6393a6d6-10e3-45d6-8274-859ccb95d748"))
    x_CHR11_Student_Female_Philosophy_08: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 08",  StrGuid("c6e279cd-3ad9-422a-939f-eac2d4d5ccfc"))
    x_CHR11_Student_Female_Philosophy_09: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 09",  StrGuid("358d95b4-6291-4f76-ba02-c902d5cd8eb0"))
    x_CHR11_Student_Female_Philosophy_10: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 10",  StrGuid("8f84efde-618c-4072-809c-1d7896af73d3"))
    x_CHR11_Student_Female_Philosophy_11: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 11",  StrGuid("eeb38711-9a8e-4baf-b27b-aad270da09de"))
    x_CHR11_Student_Female_Philosophy_12: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 12",  StrGuid("37d56322-5ea1-4043-8def-0dc509fc541a"))
    x_CHR11_Student_Female_Philosophy_13: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 13",  StrGuid("16abf022-69d7-424c-8f88-5f8419ab59de"))
    x_CHR11_Student_Female_Philosophy_14: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 14",  StrGuid("8c4d2762-a57a-48cd-a0e5-ef27de36b873"))
    x_CHR11_Student_Female_Philosophy_15: JsonReference = JsonReference("x CHR11 Student, Female, Philosophy 15",  StrGuid("0ce8f2cb-41d9-482c-a709-e0a2550fc3cb"))
    x_CHR12_Student_2_Male_Philosophy_01: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 01",  StrGuid("8180231b-4244-45c8-9938-d18529970185"))
    x_CHR12_Student_2_Male_Philosophy_02: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 02",  StrGuid("833beb60-61f5-41f5-a8d5-64d5fd8d708a"))
    x_CHR12_Student_2_Male_Philosophy_03: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 03",  StrGuid("699b4e80-48f7-4a03-ab40-b0d253770c99"))
    x_CHR12_Student_2_Male_Philosophy_04: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 04",  StrGuid("252b198e-d67c-42d6-8c29-c0de569657ff"))
    x_CHR12_Student_2_Male_Philosophy_05: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 05",  StrGuid("06f79dd0-a290-43e0-a8ee-83c84fb8dc51"))
    x_CHR12_Student_2_Male_Philosophy_06: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 06",  StrGuid("551af88f-6af1-4ee4-8117-e5e38f65ce2c"))
    x_CHR12_Student_2_Male_Philosophy_07: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 07",  StrGuid("424b500c-4779-43bc-8a01-f9adb9830c04"))
    x_CHR12_Student_2_Male_Philosophy_08: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 08",  StrGuid("e9105a2e-ace6-4b37-96eb-f2315fa0f6ec"))
    x_CHR12_Student_2_Male_Philosophy_09: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 09",  StrGuid("b596c46c-8da3-4754-a5b8-a96017a487e4"))
    x_CHR12_Student_2_Male_Philosophy_10: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 10",  StrGuid("84c7bfbb-0158-434c-925a-e424feb4625a"))
    x_CHR12_Student_2_Male_Philosophy_11: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 11",  StrGuid("7a85638b-3597-4b19-b2b5-d8887de5897a"))
    x_CHR12_Student_2_Male_Philosophy_12: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 12",  StrGuid("b6f1b5f2-bceb-4469-b9d4-c4c83429117e"))
    x_CHR12_Student_2_Male_Philosophy_13: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 13",  StrGuid("3dd66505-b865-4264-aafd-2f51a9acc0fa"))
    x_CHR12_Student_2_Male_Philosophy_14: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 14",  StrGuid("d6cf4406-0df2-4a8a-842a-def30ce38d1d"))
    x_CHR12_Student_2_Male_Philosophy_15: JsonReference = JsonReference("x CHR12 Student 2, Male, Philosophy 15",  StrGuid("c00c5a15-cbe3-4289-9232-297ad43778e2"))
    x_CHR13_Student_with_Work_01: JsonReference = JsonReference("x CHR13 Student with Work 01",  StrGuid("8f913cc4-09df-4e72-81a0-d98cef5bcc9a"))
    x_CHR13_Student_with_Work_02: JsonReference = JsonReference("x CHR13 Student with Work 02",  StrGuid("22878874-55e1-4b1c-b00d-6a6aef67334e"))
    x_CHR13_Student_with_Work_03: JsonReference = JsonReference("x CHR13 Student with Work 03",  StrGuid("9edfdeb3-643d-4400-a092-217cbacac6e0"))
    x_CHR13_Student_with_Work_04: JsonReference = JsonReference("x CHR13 Student with Work 04",  StrGuid("7b3f88fe-d411-4619-b9cd-9c9ae25c21a4"))
    x_CHR13_Student_with_Work_05: JsonReference = JsonReference("x CHR13 Student with Work 05",  StrGuid("64715922-23ca-4a1f-a68b-063d79afd256"))
    x_CHR13_Student_with_Work_06: JsonReference = JsonReference("x CHR13 Student with Work 06",  StrGuid("d30be82c-4f6e-4ebd-a9e0-66d23bf9080d"))
    x_CHR13_Student_with_Work_07: JsonReference = JsonReference("x CHR13 Student with Work 07",  StrGuid("d02cac4f-c4f3-4ead-a349-677115c8f67d"))
    x_CHR13_Student_with_Work_08: JsonReference = JsonReference("x CHR13 Student with Work 08",  StrGuid("60e59acc-a6ae-4d80-8e51-53a670d2744a"))
    x_CHR13_Student_with_Work_09: JsonReference = JsonReference("x CHR13 Student with Work 09",  StrGuid("4be6bd9e-b43f-4215-a14c-e6d1b52c19ab"))
    x_CHR13_Student_with_Work_10: JsonReference = JsonReference("x CHR13 Student with Work 10",  StrGuid("cd8e8021-0e60-4e05-bbf8-00e46f0585d4"))
    x_CHR13_Student_with_Work_11: JsonReference = JsonReference("x CHR13 Student with Work 11",  StrGuid("3c3fe728-1b36-41a8-bc19-13d654b73729"))
    x_CHR13_Student_with_Work_12: JsonReference = JsonReference("x CHR13 Student with Work 12",  StrGuid("14896e99-52f1-428f-8e9e-e641abc59e39"))
    x_CHR13_Student_with_Work_13: JsonReference = JsonReference("x CHR13 Student with Work 13",  StrGuid("06543121-0054-4653-a596-f326e3aa8c20"))
    x_CHR13_Student_with_Work_14: JsonReference = JsonReference("x CHR13 Student with Work 14",  StrGuid("c395a8c4-fe43-423d-b55b-1c6731077269"))
    x_CHR13_Student_with_Work_15: JsonReference = JsonReference("x CHR13 Student with Work 15",  StrGuid("c1216d17-f82a-4c67-88e6-b2b23b53449c"))
    x_CHR13_Student_with_Work_16: JsonReference = JsonReference("x CHR13 Student with Work 16",  StrGuid("4549ed2e-c212-42bd-a0e1-66f6012ed27f"))
    x_CHR13_Student_with_Work_17: JsonReference = JsonReference("x CHR13 Student with Work 17",  StrGuid("e22d6686-840a-42b9-a0d8-5aa97d32efcf"))
    x_CHR13_Student_with_Work_18: JsonReference = JsonReference("x CHR13 Student with Work 18",  StrGuid("7daafe8e-1858-405e-ba73-c2625a774591"))
    x_CHR13_Student_with_Work_19: JsonReference = JsonReference("x CHR13 Student with Work 19",  StrGuid("2897aa16-8e84-486b-a9ec-eca38e3df0d8"))
    x_CHR13_Student_with_Work_20: JsonReference = JsonReference("x CHR13 Student with Work 20",  StrGuid("0d398573-f1ed-4f0e-8a04-3d1457155ea7"))
    x_CHR49_Family_with_1_child_without_work_01: JsonReference = JsonReference("x CHR49 Family with 1 child, without work 01",  StrGuid("af824f88-cc70-4800-8d6d-531ff4803126"))
    x_CHR57_Family_with_2_Children_Man_at_work_01: JsonReference = JsonReference("x CHR57 Family with 2 Children, Man at work 01",  StrGuid("318ec4c1-32b4-4906-a40e-104027f964cf"))
    x_OR01_Single_Person_Office_01: JsonReference = JsonReference("x OR01 Single Person Office 01",  StrGuid("c546f480-fc64-4924-80b1-46ad569dade9"))


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
    Bus_and_one_30_km_h_Car: JsonReference = JsonReference("Bus and one 30 km/h Car",  StrGuid("6ac74bd0-bacd-4b39-b84a-dc7ae16702c9"))
    Bus_and_one_60_km_h_Car: JsonReference = JsonReference("Bus and one 60 km/h Car",  StrGuid("b7b80c60-3292-4d35-9ec2-81ecf1199ce9"))
    Bus_and_two_30_km_h_Cars: JsonReference = JsonReference("Bus and two 30 km/h Cars",  StrGuid("f90fece2-901a-4419-8a6b-a0ed4ed6ceff"))
    Bus_and_two_60_km_h_Cars: JsonReference = JsonReference("Bus and two 60 km/h Cars",  StrGuid("4bbcd8b8-ddd9-4592-8f4e-f1cf5579eb37"))


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
    Travel_Route_Set_for_05km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 05km Commuting Distance",  StrGuid("a60747ab-3427-43f8-9a61-3233f332075a"))
    Travel_Route_Set_for_10km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 10km Commuting Distance",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))
    Travel_Route_Set_for_15km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 15km Commuting Distance",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))
    Travel_Route_Set_for_20km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 20km Commuting Distance",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))
    Travel_Route_Set_for_25km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 25km Commuting Distance",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))
    Travel_Route_Set_for_30km_Commuting_Distance: JsonReference = JsonReference("Travel Route Set for 30km Commuting Distance",  StrGuid("0b217fce-ad99-4ef1-8540-c07081856d3c"))


# noinspection PyPep8,PyUnusedLocal
class Houses:
    House_Template_01_House_01_HT01_with_CHR49: JsonReference = JsonReference("(5 House Template 01) House 01 HT01 with CHR49",  StrGuid("3320aede-412d-4327-ab74-f147990b27b0"))
    House_Template_01_House_02_HT08_with_OR01: JsonReference = JsonReference("(5 House Template 01) House 02 HT08 with OR01",  StrGuid("721884fd-7f99-417f-9f1e-3a2f63c7b649"))
    House_Template_01_House_03_HT12_with_CHR61: JsonReference = JsonReference("(5 House Template 01) House 03 HT12 with CHR61",  StrGuid("36ea32be-be56-4399-aa7e-29915effe3cd"))
    House_Template_01_House_04_HT16_with_CHR57: JsonReference = JsonReference("(5 House Template 01) House 04 HT16 with CHR57",  StrGuid("057b1ec6-d0f4-4700-add6-6065742beae3"))
    Singles_01_House_01_HT23_with_CHR06: JsonReference = JsonReference("(Singles 01) House 01 HT23 with CHR06",  StrGuid("d97d5e5f-e6d8-471e-a19c-be9a22b6ec28"))
    Singles_01_House_02_HT23_with_CHR30: JsonReference = JsonReference("(Singles 01) House 02 HT23 with CHR30",  StrGuid("0d513c5c-ab0f-4017-95b7-382473aadad0"))
    Singles_01_House_03_HT23_with_CHR31: JsonReference = JsonReference("(Singles 01) House 03 HT23 with CHR31",  StrGuid("1686cc35-bfd3-4046-8188-c5e48d120a18"))
    Singles_01_House_04_HT23_with_CHR07: JsonReference = JsonReference("(Singles 01) House 04 HT23 with CHR07",  StrGuid("03ac6ad2-e923-475b-ab27-a6cb230844be"))
    Singles_01_House_05_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 05 HT23 with CHR11",  StrGuid("a2f998fb-017e-4778-b0b7-1f99fd6dedd3"))
    Singles_01_House_06_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 06 HT23 with CHR11",  StrGuid("5e5a74eb-25c4-43f0-8841-5c0f0161a58b"))
    Singles_01_House_07_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 07 HT23 with CHR11",  StrGuid("a983bff8-6b96-4bfd-867f-8d704311fdae"))
    Singles_01_House_08_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 08 HT23 with CHR11",  StrGuid("46e17f3b-ccb9-40fc-ae5b-88d30c2bd7e0"))
    Singles_01_House_09_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 09 HT23 with CHR11",  StrGuid("e8c048d3-97b9-4c7d-b0ec-5d3d0bdf255a"))
    Singles_01_House_10_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 10 HT23 with CHR11",  StrGuid("21391590-7ff3-4845-9a55-637848728b2a"))
    Singles_01_House_100_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 100 HT23 with CHR13",  StrGuid("7c24f09f-75e0-41b2-a864-fbd3e45c4ef2"))
    Singles_01_House_11_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 11 HT23 with CHR11",  StrGuid("c26620a2-7d51-4c5c-91f0-82a5ee637e07"))
    Singles_01_House_12_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 12 HT23 with CHR11",  StrGuid("79bd3943-0862-4370-83d8-90e466ec3eb7"))
    Singles_01_House_13_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 13 HT23 with CHR11",  StrGuid("29827171-5145-44da-96c1-ac7b4079c336"))
    Singles_01_House_14_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 14 HT23 with CHR11",  StrGuid("7e090256-ba3a-46a1-a9f9-d350ed4de325"))
    Singles_01_House_15_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 15 HT23 with CHR11",  StrGuid("d68d5329-e774-4b20-a7e8-234e36574b14"))
    Singles_01_House_16_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 16 HT23 with CHR11",  StrGuid("1cb77de2-51e7-4fe2-937e-660b23cf7c7f"))
    Singles_01_House_17_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 17 HT23 with CHR11",  StrGuid("a5a29c73-d37c-466a-aef2-92b933c129b1"))
    Singles_01_House_18_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 18 HT23 with CHR11",  StrGuid("93021a95-562a-4f40-807f-1227f1fdb2f5"))
    Singles_01_House_19_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 19 HT23 with CHR11",  StrGuid("3d2e2db0-97ec-4588-8cfe-4a3942a5dec4"))
    Singles_01_House_20_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 20 HT23 with CHR11",  StrGuid("2a31d126-624f-420b-aaa9-331dbcc6e6ec"))
    Singles_01_House_21_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 21 HT23 with CHR11",  StrGuid("bacb752e-7442-4ba2-a435-0f86e6ba6501"))
    Singles_01_House_22_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 22 HT23 with CHR11",  StrGuid("b90ca61e-7f6d-46f0-8423-784be1b41ef6"))
    Singles_01_House_23_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 23 HT23 with CHR11",  StrGuid("47167d78-2f75-42f2-bc28-2d40e8eafe4f"))
    Singles_01_House_24_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 24 HT23 with CHR11",  StrGuid("3644cdf1-cc80-46d9-86f8-41f5c4dda9fa"))
    Singles_01_House_25_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 25 HT23 with CHR11",  StrGuid("b514e975-0001-4eff-a401-6ff54eedd118"))
    Singles_01_House_26_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 26 HT23 with CHR11",  StrGuid("f8a95088-4af2-4a0f-b101-dc842e5ac6b6"))
    Singles_01_House_27_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 27 HT23 with CHR11",  StrGuid("e98072b2-341f-4551-964f-c65cd1a92015"))
    Singles_01_House_28_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 28 HT23 with CHR11",  StrGuid("5d45451f-f4f0-4ede-946c-2ac1d955a793"))
    Singles_01_House_29_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 29 HT23 with CHR11",  StrGuid("89673510-c081-4cf3-8c84-69292c274eb0"))
    Singles_01_House_30_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 30 HT23 with CHR11",  StrGuid("f6c46812-d84b-44e0-ad13-3976ede1f684"))
    Singles_01_House_31_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 31 HT23 with CHR11",  StrGuid("2ff0e05a-7378-4df5-a51e-90ada77177e8"))
    Singles_01_House_32_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 32 HT23 with CHR11",  StrGuid("d2397681-2f94-4e0f-a593-a3ed2c594c39"))
    Singles_01_House_33_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 33 HT23 with CHR11",  StrGuid("5434f3c5-b376-43b3-a940-2a9c22b8bc49"))
    Singles_01_House_34_HT23_with_CHR11: JsonReference = JsonReference("(Singles 01) House 34 HT23 with CHR11",  StrGuid("df0e1487-b0d7-408f-9fa2-d96b4dfa1e6a"))
    Singles_01_House_35_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 35 HT23 with CHR12",  StrGuid("ef9fe6a5-9954-4511-bc6d-3dddc9cc0bc3"))
    Singles_01_House_36_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 36 HT23 with CHR12",  StrGuid("ac690d16-de15-40ec-b8c5-02bdad437e5d"))
    Singles_01_House_37_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 37 HT23 with CHR12",  StrGuid("06ec1688-99cd-4f24-90c4-8a7fa04795e8"))
    Singles_01_House_38_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 38 HT23 with CHR12",  StrGuid("dbac100d-379c-47d7-b9b9-3962f8b57c87"))
    Singles_01_House_39_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 39 HT23 with CHR12",  StrGuid("f0d34f98-f434-40cd-abce-f02925b11eff"))
    Singles_01_House_40_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 40 HT23 with CHR12",  StrGuid("99690e29-a954-4863-bac9-de13c0738421"))
    Singles_01_House_41_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 41 HT23 with CHR12",  StrGuid("c3b7f1c7-068d-4efc-91b0-a2493de1ac57"))
    Singles_01_House_42_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 42 HT23 with CHR12",  StrGuid("174e0063-50a7-43e4-8aeb-a3acc940f952"))
    Singles_01_House_43_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 43 HT23 with CHR12",  StrGuid("2b57d94e-3270-4056-871f-87512f48c13c"))
    Singles_01_House_44_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 44 HT23 with CHR12",  StrGuid("5933084b-36ee-4635-8a8e-d2381e5fcf04"))
    Singles_01_House_45_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 45 HT23 with CHR12",  StrGuid("191a8f5d-0efc-4ceb-b3f8-2f27334994e8"))
    Singles_01_House_46_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 46 HT23 with CHR12",  StrGuid("b65208d9-4ca2-4e3c-9b77-eb6c748002f3"))
    Singles_01_House_47_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 47 HT23 with CHR12",  StrGuid("fee28f91-87d7-4a8f-bd6c-3b26414587bc"))
    Singles_01_House_48_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 48 HT23 with CHR12",  StrGuid("ef38da46-aa0f-4cd8-a2f4-467f1e5779c3"))
    Singles_01_House_49_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 49 HT23 with CHR12",  StrGuid("2cc4bd92-0fc9-428f-a67f-a9db68f29ce0"))
    Singles_01_House_50_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 50 HT23 with CHR12",  StrGuid("32eb36e6-8ff0-4d3c-8a76-e7cde6cb0a3b"))
    Singles_01_House_51_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 51 HT23 with CHR12",  StrGuid("14647a8c-a2a3-446e-a901-81747aa9f36e"))
    Singles_01_House_52_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 52 HT23 with CHR12",  StrGuid("c7147e1c-e67b-4899-b3f9-b890ac3fc55a"))
    Singles_01_House_53_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 53 HT23 with CHR12",  StrGuid("5ff05ac8-9d76-4027-a957-1cffdce64d75"))
    Singles_01_House_54_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 54 HT23 with CHR12",  StrGuid("960114f1-e23b-46d5-a5ad-0fd87a2323fc"))
    Singles_01_House_55_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 55 HT23 with CHR12",  StrGuid("ee22f5c3-f4e1-4a6c-b030-9d26de9ce478"))
    Singles_01_House_56_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 56 HT23 with CHR12",  StrGuid("4f08698d-8a72-4e2a-bee0-5cf55111a236"))
    Singles_01_House_57_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 57 HT23 with CHR12",  StrGuid("566180a9-3762-4bee-a5f5-6239381623e1"))
    Singles_01_House_58_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 58 HT23 with CHR12",  StrGuid("33e4392e-3d10-4fc9-b0ec-5a5945fdffe1"))
    Singles_01_House_59_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 59 HT23 with CHR12",  StrGuid("f06e0a52-bf76-4273-9794-b836b86fbb3e"))
    Singles_01_House_60_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 60 HT23 with CHR12",  StrGuid("33ef9755-ba84-4b47-b543-c3d048c88684"))
    Singles_01_House_61_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 61 HT23 with CHR12",  StrGuid("ed5c04ae-3e8d-4a0a-83e6-51b82852ecb4"))
    Singles_01_House_62_HT23_with_CHR12: JsonReference = JsonReference("(Singles 01) House 62 HT23 with CHR12",  StrGuid("be23bf38-f736-429b-84a2-58b7e9bf1ff0"))
    Singles_01_House_63_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 63 HT23 with CHR13",  StrGuid("e21a6c45-66f3-4136-bbb8-5f784f0ac7a8"))
    Singles_01_House_64_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 64 HT23 with CHR13",  StrGuid("38a8ec26-b67e-4e08-9f5d-580765fb2e91"))
    Singles_01_House_65_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 65 HT23 with CHR13",  StrGuid("38f69539-709a-4881-8c36-f09a2f99a01f"))
    Singles_01_House_66_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 66 HT23 with CHR13",  StrGuid("f0087138-678a-43d9-99c6-f4d4c0192eaa"))
    Singles_01_House_67_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 67 HT23 with CHR13",  StrGuid("f3338167-1042-48c9-aaab-4562dd00cced"))
    Singles_01_House_68_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 68 HT23 with CHR13",  StrGuid("098cd811-b8c3-456a-83e6-4ceff59e3266"))
    Singles_01_House_69_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 69 HT23 with CHR13",  StrGuid("5abc9707-354a-46dc-86e3-f851f0953540"))
    Singles_01_House_70_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 70 HT23 with CHR13",  StrGuid("3e75b0c1-4de7-438e-87ee-827192428e6b"))
    Singles_01_House_71_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 71 HT23 with CHR13",  StrGuid("bf5ed1c6-82e2-4660-bc64-360f9e45e216"))
    Singles_01_House_72_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 72 HT23 with CHR13",  StrGuid("f698a25a-bd93-42dd-8018-aab26b11c8d1"))
    Singles_01_House_73_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 73 HT23 with CHR13",  StrGuid("d1763933-cfdc-438f-8014-a9a87895a235"))
    Singles_01_House_74_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 74 HT23 with CHR13",  StrGuid("81d19122-ee10-46c3-99cf-7f15689c80ec"))
    Singles_01_House_75_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 75 HT23 with CHR13",  StrGuid("035428a0-7ed8-4dd0-a246-74fda70b8916"))
    Singles_01_House_76_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 76 HT23 with CHR13",  StrGuid("355c77fc-0e38-41bc-b274-608a4427b1af"))
    Singles_01_House_77_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 77 HT23 with CHR13",  StrGuid("b69a1157-df4a-4630-ac30-1d5719e28a73"))
    Singles_01_House_78_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 78 HT23 with CHR13",  StrGuid("6eff916b-e234-4771-a012-1044347b8f1d"))
    Singles_01_House_79_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 79 HT23 with CHR13",  StrGuid("050835d0-b6b2-461d-a880-3377a2da9c2a"))
    Singles_01_House_80_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 80 HT23 with CHR13",  StrGuid("a188adb1-85a9-4d49-8467-103a24e2fbe5"))
    Singles_01_House_81_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 81 HT23 with CHR13",  StrGuid("b6dda3d6-e075-4cbe-83d2-2f8f07664fae"))
    Singles_01_House_82_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 82 HT23 with CHR13",  StrGuid("d9d45117-44db-495d-a4ab-442127161f8d"))
    Singles_01_House_83_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 83 HT23 with CHR13",  StrGuid("0673492d-ae92-4cb8-b85f-ef442d2b9d49"))
    Singles_01_House_84_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 84 HT23 with CHR13",  StrGuid("26b5a6df-33d2-464e-9ac9-689b4238b1d8"))
    Singles_01_House_85_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 85 HT23 with CHR13",  StrGuid("f54d89f4-23ef-4a21-be7b-c9ecd667910e"))
    Singles_01_House_86_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 86 HT23 with CHR13",  StrGuid("6c98d8b2-110c-4e6d-9ae1-f97d48259102"))
    Singles_01_House_87_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 87 HT23 with CHR13",  StrGuid("0aa0c04a-90f1-42ec-a569-e92f891160a5"))
    Singles_01_House_88_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 88 HT23 with CHR13",  StrGuid("235d6696-1d24-4ab5-bb76-6b0ab9204873"))
    Singles_01_House_89_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 89 HT23 with CHR13",  StrGuid("6874ff1d-a9d1-4114-8c5e-a571a666990c"))
    Singles_01_House_90_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 90 HT23 with CHR13",  StrGuid("28b59167-8cd1-44b2-8909-075db6f41ba6"))
    Singles_01_House_91_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 91 HT23 with CHR13",  StrGuid("b556dd06-7600-4a8f-a711-cb27a715d4f9"))
    Singles_01_House_92_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 92 HT23 with CHR13",  StrGuid("1f012456-8d9f-4b59-837e-06f9365a4668"))
    Singles_01_House_93_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 93 HT23 with CHR13",  StrGuid("a80799a7-7dee-44ba-9154-eca0fef04ba1"))
    Singles_01_House_94_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 94 HT23 with CHR13",  StrGuid("cbb2e57b-1e21-4daf-b2c4-e3e917cb77de"))
    Singles_01_House_95_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 95 HT23 with CHR13",  StrGuid("fd0e1ea0-b520-4828-bb58-bb1a552e7c1c"))
    Singles_01_House_96_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 96 HT23 with CHR13",  StrGuid("ab4b43e6-1107-4f57-b4b3-9c1ec4b40046"))
    Singles_01_House_97_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 97 HT23 with CHR13",  StrGuid("7a3a8b6e-a1a7-4b20-bd26-530ac1554c62"))
    Singles_01_House_98_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 98 HT23 with CHR13",  StrGuid("b9427981-4863-401a-a8d8-c3ac7c2bd38b"))
    Singles_01_House_99_HT23_with_CHR13: JsonReference = JsonReference("(Singles 01) House 99 HT23 with CHR13",  StrGuid("093d373b-9bce-4733-b2d1-159ad990e49e"))
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


# noinspection PyPep8,PyUnusedLocal
class HouseholdTags:
    Children_None = "Children - None"
    Children_One_Child = "Children - One Child"
    Children_Three_Children = "Children - Three Children"
    Children_Two_Children = "Children - Two Children"
    Earners_None = "Earners - None"
    Earners_One = "Earners - One"
    Earners_Two = "Earners - Two"
    Employment_Employed_Office_Hours = "Employment - Employed Office Hours"
    Employment_Part_Time = "Employment - Part Time"
    Employment_Retired = "Employment - Retired"
    Employment_Student = "Employment - Student"
    Employment_Three_Shifts = "Employment - Three Shifts"
    Employment_Two_Shifts = "Employment - Two Shifts"
    Employment_Unemployed = "Employment - Unemployed"
    Size_Couple = "Size - Couple"
    Size_Family = "Size - Family"
    Size_Flatsharing = "Size - Flatsharing"
    Size_Single = "Size - Single"
    Size_Single_Parent = "Size - Single Parent"


# noinspection PyPep8,PyUnusedLocal
class LivingPatternTags:
    Living_Pattern_All = "Living Pattern / All"
    Living_Pattern_Kindergarden = "Living Pattern / Kindergarden"
    Living_Pattern_Maid_Day_Maid = "Living Pattern / Maid / Day Maid"
    Living_Pattern_Office_Job = "Living Pattern / Office Job"
    Living_Pattern_Office_Job_Early_5_7am = "Living Pattern / Office Job / Early (5-7am)"
    Living_Pattern_Office_Job_Late_9_11am = "Living Pattern / Office Job / Late (9-11am)"
    Living_Pattern_Office_Job_Medium_7_9am = "Living Pattern / Office Job / Medium (7-9am)"
    Living_Pattern_Office_Worker = "Living Pattern / Office Worker"
    Living_Pattern_Part_Time_Job = "Living Pattern / Part Time Job"
    Living_Pattern_Retiree = "Living Pattern / Retiree"
    Living_Pattern_School = "Living Pattern / School"
    Living_Pattern_School_Medium_7_9am = "Living Pattern / School / Medium (7-9am)"
    Living_Pattern_Shift_work = "Living Pattern / Shift work"
    Living_Pattern_Shift_work_3_Shifts_A = "Living Pattern / Shift work / 3 Shifts A"
    Living_Pattern_Shift_work_3_Shifts_B = "Living Pattern / Shift work / 3 Shifts B"
    Living_Pattern_Stay_at_Home = "Living Pattern / Stay at Home"
    Living_Pattern_Stay_at_Home_Drifting = "Living Pattern / Stay at Home / Drifting"
    Living_Pattern_Stay_at_Home_Regular = "Living Pattern / Stay at Home / Regular"
    Living_Pattern_Two_Shift_Work = "Living Pattern / Two Shift Work"
    Living_Pattern_University = "Living Pattern / University"
    Living_Pattern_University_Student_Independent = "Living Pattern / University / Student Independent"
    Living_Pattern_University_Student_Living_at_Home = "Living Pattern / University / Student Living at Home"
    Living_Pattern_Work_From_Home = "Living Pattern / Work From Home"
    Living_Pattern_Work_From_Home_Full_Time_3_Days = "Living Pattern / Work From Home / Full Time 3 Days"
    Living_Pattern_Work_From_Home_Full_Time_5_days = "Living Pattern / Work From Home / Full Time 5 days"
    Living_Pattern_Work_From_Home_Part_Time = "Living Pattern / Work From Home / Part Time"

