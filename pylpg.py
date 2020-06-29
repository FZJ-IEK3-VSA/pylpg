from lpgdata import *
from lpgpythonbindings import *
from typing import Any
import random
import subprocess
import glob
import os
import pandas as pd  # type: ignore
from pathlib import Path
from typing import List
from sys import platform
import pathlib


def excute_lpg_tsib(year: int, number_of_households: int,
                    number_of_people_per_household: int, startdate: str = None,
                    enddate: str = None,
                    transportation: bool = False) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor()
    if number_of_households < 1:
        print("too few households")
        raise Exception("Need at least one household")

    #basic default spec
    request = lpe.make_default_lpg_settings(year)

    # create random households
    for idx in range(number_of_households):
        hhd: HouseholdData = HouseholdData()
        hhd.HouseholdDataSpecification = HouseholdDataSpecificationType.ByPersons
        hhd.HouseholdDataPersonSpec = HouseholdDataPersonSpecification()
        hhd.HouseholdDataPersonSpec.Persons = []
        hhd.ChargingStationSet = ChargingStationSets.Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity
        hhd.TravelRouteSet = TravelRouteSets.Travel_Route_Set_for_30km_Commuting_Distance
        hhd.TransportationDeviceSet = TransportationDeviceSets.Bus_and_two_30_km_h_Cars
        hhd.HouseholdDataPersonSpec.Persons = makeReasonableFamily(number_of_people_per_household)
        request.House.Households.append(hhd)

    # set more parameters
    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    if transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)

    #write to json
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)

    #execute
    lpe.execute_lpg_binaries()

    # read the results and return as dataframe
    return lpe.read_all_json_results_in_directory()

def makeReasonableFamily(personCount: int):
    previousage = 0
    persons = []
    g = 0
    for person_idx in range(personCount):

        if(person_idx == 0): # first is an adult
            age = random.randint(18,100)
            previousage = age
            g = random.randint(0, 1)
        elif person_idx==1: # 2nd adult should be roughly similar age
            diffage = random.randint(0,10)
            age = previousage -5 + diffage
            if g == 0:
                g = 1
            else:
                g = 0
        else: # other people are children
            age = random.randint(0,20)
            if g == 0:
                g = 1
            else:
                g = 0
        if g == 0:
            gender = Gender.Male
        else:
            gender = Gender.Female
        pd = PersonData(age,gender)
        persons.append(pd)
    return persons

def excute_lpg_single_household(year: int, householdref: JsonReference,
                    housetype: str, startdate: str = None,
                    enddate: str = None,
                    simulate_transportation: bool = False,
                    chargingset: JsonReference = None,
                    transportation_device_set: JsonReference= None,
                    travel_route_set: JsonReference = None
                    ) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor()

    # basic request
    request = lpe.make_default_lpg_settings(year)

    request.House.HouseTypeCode = housetype
    hhn =  HouseholdData(None,None,householdref,"hhid","hhname",
                         chargingset,transportation_device_set,travel_route_set,None,HouseholdDataSpecificationType.ByHouseholdName)
    request.House.Households.append(hhn)

    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    if simulate_transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)
    lpe.execute_lpg_binaries()

    return lpe.read_all_json_results_in_directory()


def excute_lpg_single_household(year: int, householdref: JsonReference,
                    housetype: str, startdate: str = None,
                    enddate: str = None,
                    simulate_transportation: bool = False,
                    chargingset: JsonReference = None,
                    transportation_device_set: JsonReference= None,
                    travel_route_set: JsonReference = None
                    ) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor()

    # basic request
    request = lpe.make_default_lpg_settings(year)

    request.House.HouseTypeCode = housetype
    hhn =  HouseholdData(None,None,householdref,"hhid","hhname",
                         chargingset,transportation_device_set,travel_route_set,None,HouseholdDataSpecificationType.ByHouseholdName)
    request.House.Households.append(hhn)

    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    if simulate_transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)
    lpe.execute_lpg_binaries()

    return lpe.read_all_json_results_in_directory()


def execute_grid_calc(year: int, household_size_list: List[int],
                    housetype: str, startdate: str = None,
                    enddate: str = None,
                    simulate_transportation: bool = False,
                    chargingset: JsonReference = None,
                    transportation_device_set: JsonReference= None,
                    travel_route_set: JsonReference = None
                    ) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor()

    # basic request
    request = lpe.make_default_lpg_settings(year)
    request.CalcSpec.CalcOptions.clear()
    request.CalcSpec.CalcOptions.append(CalcOption.JsonHouseSumFiles)
    if(len(household_size_list)< 1):
        raise Exception("need at least one household.")

    request.House.HouseTypeCode = housetype
    count = 1
    for hs in household_size_list:
        hhdps: HouseholdDataPersonSpecification = HouseholdDataPersonSpecification(makeReasonableFamily(hs))
        hhn =  HouseholdData(hhdps,None,None,"hhid","hhname" + str(count),
                         chargingset,transportation_device_set,travel_route_set,None,HouseholdDataSpecificationType.ByPersons)
        request.House.Households.append(hhn)
        count = count + 1

    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    if simulate_transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)
    lpe.execute_lpg_binaries()

    return lpe.read_all_json_results_in_directory()


class LPGExecutor:
    def __init__(self):
        version = "_9.9.0_"
        self.working_directory = pathlib.Path(__file__).parent.absolute()
        if platform == "linux" or platform == "linux2":
            self.calculation_directory = Path(self.working_directory, "LPG" + version + "linux")
            self.simengine_filename = "simengine2"
        elif platform == "win32":
            self.calculation_directory = Path(self.working_directory, "LPG" + version + "win")
            self.simengine_filename = "simulationengine.exe"
        else:
            raise Exception("unknown operating system detected: " + platform)

    def execute_lpg_binaries(self) -> Any:
        # execute LPG
        pathname = Path(self.calculation_directory, self.simengine_filename)
        os.chdir(str(self.calculation_directory))
        print("executing in " + str(self.calculation_directory))
        subprocess.run([str(pathname), "processhousejob", "-j", "calcspec.json"])


    def make_default_lpg_settings(self, year: int) -> HouseCreationAndCalculationJob:


        print("Creating")

        hj = HouseCreationAndCalculationJob()
        hj.set_Scenario("S1").set_Year(str(year)).set_DistrictName("district")
        hd = HouseData()
        hj.House = hd
        hd.Name = "House"
        hd.HouseGuid = StrGuid("houseguid")
        hd.HouseTypeCode = HouseTypes.HT01_House_with_a_10kWh_Battery_and_a_fuel_cell_battery_charger_5_MWh_yearly_space_heating_gas_heating
        hd.TargetCoolingDemand = 10000
        hd.TargetHeatDemand = 0
        hd.Households = []

        cs: JsonCalcSpecification = JsonCalcSpecification()
        hj.CalcSpec = cs
        cs.IgnorePreviousActivitiesWhenNeeded = True
        cs.LoadTypePriority = LoadTypePriority.All
        cs.DefaultForOutputFiles = OutputFileDefault.NoFiles
        cs.CalcOptions = [CalcOption.JsonHouseholdSumFiles, CalcOption.BodilyActivityStatistics]
        cs.EnergyIntensityType = EnergyIntensityType.Random
        cs.OutputDirectory = "results"
        hj.PathToDatabase = str(Path(self.calculation_directory, "profilegenerator.db3"))
        return hj

    def read_all_json_results_in_directory(self) -> Optional[pd.DataFrame]:
        df: pd.DataFrame = pd.DataFrame()
        results_directory = Path(self.calculation_directory, "results", "Results")
        if not os.path.exists(str(results_directory)):
            return None
        potential_files = glob.glob(str(results_directory) + "/*.json")
        isFirst = True
        for file in potential_files:
            #                self.print("Reading json file " + str(file))
            print("Reading file " + str(file))
            with open(file) as json_file:
                filecontent: str = json_file.read()  # type: ignore
                sumProfile: JsonSumProfile = JsonSumProfile.from_json(filecontent)  # type: ignore
            if sumProfile.LoadTypeName is None:
                raise Exception("Empty load type name on " + file)
            if sumProfile is None or sumProfile.HouseKey is None or sumProfile.HouseKey.HHKey is None:
                raise Exception("empty housekey")
            key: str = sumProfile.LoadTypeName + "_" + str(sumProfile.HouseKey.HHKey.Key)
            df[key] = sumProfile.Values
            if isFirst:
                isFirst = False
                ts = sumProfile.StartTime
                timestamps = pd.date_range(ts, periods=len(sumProfile.Values), freq='T')
                df["Timestamp"] = timestamps
        return df

