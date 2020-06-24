from lpgpythonbindings import *
from lpgdata import *
from typing import Any
import random
import subprocess
import glob
import os
import pandas as pd  # type: ignore
from pathlib import Path
from typing import List
from sys import platform

class LPGExecutor:


    def excute_lpg_locally(self, year: int, number_of_households: int,
                           number_of_people_per_household: int, working_directory: str, startdate: str = None, enddate: str = None,
                           loadtypes: List[str] = None, transportation: bool = False) -> pd.DataFrame:
        version= "_9.7.0_"

        if platform == "linux" or platform == "linux2":
            calculation_directory = Path(working_directory, "LPG" + version + "linux")
            simengine_filename = "simengine2"
        elif platform == "win32":
            calculation_directory = Path(working_directory, "LPG" + version + "win")
            simengine_filename = "simulationengine.exe"
        else:
            raise Exception("unknown operating system detected: " + platform)


        request = self.make_default_lpg_settings(year, number_of_households, number_of_people_per_household, str(calculation_directory))
        if request.CalcSpec is None:
            raise Exception("Failed to initialize the calculation spec")
        if startdate is not None:
            request.CalcSpec.set_StartDate(startdate)
        if enddate is not None:
            request.CalcSpec.set_EndDate(enddate)
        calcspecfilename = Path(calculation_directory, "calcspec.json")
        if transportation:
            request.CalcSpec.EnableTransportation = True
            request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)
        if(loadtypes is not None and len(loadtypes) > 0):
            request.CalcSpec.LoadtypesForPostprocessing = loadtypes
        with open(calcspecfilename, "w") as calcspecfile:
            jsonrequest = request.to_json(indent=4)  # type: ignore
            calcspecfile.write(jsonrequest)
        self.execute_lpg(calculation_directory, simengine_filename)
        resultsdir = Path(calculation_directory, "results", "Results")
        return self.read_all_json_results_in_directory(str(resultsdir))

    @staticmethod
    def execute_lpg(calculation_directory: Path, filename: str) -> Any:
        # execute LPG
        pathname = Path(calculation_directory, filename)
        os.chdir(str(calculation_directory))
        print("executing in " + str(calculation_directory))
        subprocess.run([str(pathname), "processhousejob", "-j", "calcspec.json"])

    @staticmethod
    def make_default_lpg_settings(year: int, number_of_households: int,
                                  number_of_people_per_household: int, working_directory: str = "") -> HouseCreationAndCalculationJob:

        if number_of_households < 1:
            print("too few households")
            raise Exception("Need at least one household")
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
        for idx in range(number_of_households):
            hhd: HouseholdData = HouseholdData()
            hhd.HouseholdDataSpecification = HouseholdDataSpecificationType.ByPersons
            hhd.HouseholdDataPersonSpec = HouseholdDataPersonSpecification()
            hhd.HouseholdDataPersonSpec.Persons = []
            hhd.ChargingStationSet = ChargingStationSets.Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity
            hhd.TravelRouteSet = TravelRouteSets.Travel_Route_Set_for_30km_to_Work
            hhd.TransportationDeviceSet = TransportationDeviceSets.Bus_and_two_slow_Cars
            for person_idx in range(number_of_people_per_household):
                if person_idx % 2 == 0:
                    gender = Gender.Male
                else:
                    gender = Gender.Female
                age = 100*random.random()

                persondata = PersonData(int(age), gender)
                hhd.HouseholdDataPersonSpec.Persons.append(persondata)
            hd.Households.append(hhd)
        cs: JsonCalcSpecification = JsonCalcSpecification()
        hj.CalcSpec = cs
        cs.LoadTypePriority = LoadTypePriority.All
        cs.DefaultForOutputFiles = OutputFileDefault.NoFiles
        cs.CalcOptions = [CalcOption.JsonHouseholdSumFiles, CalcOption.BodilyActivityStatistics]
        cs.EnergyIntensityType = EnergyIntensityType.Random
        cs.OutputDirectory = "results"
        hj.PathToDatabase = str(Path(working_directory, "profilegenerator.db3"))
        return hj

    @staticmethod
    def read_all_json_results_in_directory(results_directory: str) -> Optional[pd.DataFrame]:
        df: pd.DataFrame = pd.DataFrame()

        if not os.path.exists(str(results_directory)):
            return None

        # self.print("reading files in " + str(results_directory))
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

