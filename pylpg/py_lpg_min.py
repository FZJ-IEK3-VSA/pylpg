import sys
import time
import stat
from typing import Any
import random
import subprocess
import glob
import os
import pandas as pd  # type: ignore
from pathlib import Path
from sys import platform
import pathlib
import shutil
import traceback
import pandas
from pylpg.lpgdata import *
from pylpg.lpgpythonbindings import *


def excute_lpg_with_householdata(
    year: int,
    householddata: HouseholdData,
    housetype: str,
    startdate: str = None,
    enddate: str = None,
    simulate_transportation: bool = False,
    target_heating_demand: Optional[float] = None,
    target_cooling_demand: Optional[float] = None,
    calculation_index: int = 1,
    clear_previous_calc: bool = False,
):
    try:
        print(
            "Starting calc with "
            + str(calculation_index)
            + " for "
            + householddata.Name
        )
        lpe: LPGExecutor = LPGExecutor(calculation_index, clear_previous_calc)

        # basic request
        request = lpe.make_default_lpg_settings(year)
        request.House.HouseTypeCode = housetype
        if target_heating_demand is not None:
            request.House.TargetHeatDemand = target_heating_demand
        if target_cooling_demand is not None:
            request.House.TargetCoolingDemand = target_cooling_demand
        request.House.Households.append(householddata)
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

        df = lpe.read_all_json_results_in_directory()

        return df
    except OSError as why:
        print("Exception: " + str(why))
        traceback.print_stack()
        raise
    except:  # catch *all* exceptions
        e = sys.exc_info()[0]
        print("Exception: " + str(e))
        traceback.print_stack()
        raise


class LPGExecutor:
    def __init__(self, calcidx: int, clear_previous_calc: bool):
        version = "_"
        self.working_directory = pathlib.Path(__file__).parent.absolute()
        if platform == "linux" or platform == "linux2":
            self.calculation_src_directory = Path(
                self.working_directory, "LPG" + version + "linux"
            )
            self.simengine_src_filename = "simengine2"
            fullname = Path(self.calculation_src_directory, self.simengine_src_filename)
            print("starting to execute " + str(fullname))
            os.chmod(str(fullname), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            print("Permissions:" + str(oct(os.stat(str(fullname))[stat.ST_MODE])[-3:]))
        elif platform == "win32":
            self.calculation_src_directory = Path(
                self.working_directory, "LPG" + version + "win"
            )
            self.simengine_src_filename = "simulationengine.exe"
        else:
            raise Exception("unknown operating system detected: " + platform)

        self.calculation_directory = Path(self.working_directory, "C" + str(calcidx))
        print("Working in directory: " + str(self.calculation_directory))
        if clear_previous_calc and os.path.exists(self.calculation_directory):
            self.error_tolerating_directory_clean(self.calculation_directory)
            print("Removing " + str(self.calculation_directory))
            shutil.rmtree(self.calculation_directory)
            time.sleep(1)
        if not os.path.exists(self.calculation_directory):
            print(
                "copying from  "
                + str(self.calculation_src_directory)
                + " to "
                + str(self.calculation_directory)
            )
            shutil.copytree(self.calculation_src_directory, self.calculation_directory)
            print("copied to: " + str(self.calculation_directory))

    def error_tolerating_directory_clean(self, path: str):
        mypath = str(path)
        if len(str(mypath)) < 10:
            raise Exception(
                "Path too short. This is suspicious. Trying to delete more than you meant to?"
            )
        print("cleaning " + mypath)
        files = glob.glob(mypath + "/*", recursive=True)
        for file in files:
            if os.path.isfile(file):
                print("Removing " + file)
                os.remove(file)

    def execute_lpg_binaries(self) -> Any:
        # execute LPG
        pathname = Path(self.calculation_directory, self.simengine_src_filename)
        print("executing in " + str(self.calculation_directory))
        subprocess.run(
            [str(pathname), "processhousejob", "-j", "calcspec.json"],
            cwd=str(self.calculation_directory),
        )

    def make_default_lpg_settings(self, year: int) -> HouseCreationAndCalculationJob:
        print("Creating")
        hj = HouseCreationAndCalculationJob()
        hj.set_Scenario("S1").set_Year(str(year)).set_DistrictName("district")
        hd = HouseData()
        hj.House = hd
        hd.Name = "House"
        hd.HouseGuid = StrGuid("houseguid")
        hd.HouseTypeCode = (
            HouseTypes.HT01_House_with_a_10kWh_Battery_and_a_fuel_cell_battery_charger_5_MWh_yearly_space_heating_gas_heating
        )
        hd.TargetCoolingDemand = 10000
        hd.TargetHeatDemand = 0
        hd.Households = []

        cs: JsonCalcSpecification = JsonCalcSpecification()
        hj.CalcSpec = cs
        cs.IgnorePreviousActivitiesWhenNeeded = True
        cs.LoadTypePriority = LoadTypePriority.All
        cs.DefaultForOutputFiles = OutputFileDefault.NoFiles
        cs.CalcOptions = [
            CalcOption.JsonHouseholdSumFiles,
            CalcOption.BodilyActivityStatistics,
        ]
        cs.EnergyIntensityType = EnergyIntensityType.Random
        cs.OutputDirectory = "results"
        hj.PathToDatabase = str(
            Path(self.calculation_directory, "profilegenerator.db3")
        )
        return hj

    def read_all_json_results_in_directory(self) -> Optional[pd.DataFrame]:
        df: pd.DataFrame = pd.DataFrame()
        results_directory = Path(self.calculation_directory, "results", "Results")
        if not os.path.exists(str(results_directory)):
            return None
        potential_sum_files = glob.glob(str(results_directory) + "/Sum.*.json")

        bodilyActivity_files = glob.glob(
            str(results_directory) + "/BodilyActivityLevel.*.json"
        )
        potential_sum_files.extend(bodilyActivity_files)

        carlocs = glob.glob(str(results_directory) + "/CarLocation.*.json")
        potential_sum_files.extend(carlocs)

        carstate = glob.glob(str(results_directory) + "/Carstate.*.json")
        potential_sum_files.extend(carstate)

        driving = glob.glob(str(results_directory) + "/DrivingDistance.*.json")
        potential_sum_files.extend(driving)

        soc = glob.glob(str(results_directory) + "/Soc.*.json")
        potential_sum_files.extend(soc)
        isFirst = True
        for file in potential_sum_files:
            #                self.print("Reading json file " + str(file))
            print("Reading file " + str(file))
            with open(str(file)) as json_file:
                filecontent: str = json_file.read()  # type: ignore
                sumProfile: JsonSumProfile = JsonSumProfile.from_json(filecontent)  # type: ignore
            if sumProfile.LoadTypeName is None:
                raise Exception("Empty load type name on " + str(file))
            if (
                sumProfile is None
                or sumProfile.HouseKey is None
                or sumProfile.HouseKey.HHKey is None
            ):
                raise Exception("empty housekey")
            key: str = (
                sumProfile.LoadTypeName + "_" + str(sumProfile.HouseKey.HHKey.Key)
            )
            df[key] = sumProfile.Values
            if isFirst:
                isFirst = False
                ts = sumProfile.StartTime
                timestamps = pd.date_range(ts, periods=len(sumProfile.Values), freq="T")
                df["Timestamp"] = timestamps
        return df


def test_householdata_function() -> None:
    random.seed(2)
    p1 = PersonData(24, "male")
    p2 = PersonData(24, "female")
    personspec = HouseholdDataPersonSpecification([p1, p2])
    hhdata1 = HouseholdData(
        UniqueHouseholdId="uniq",
        Name="name",
        HouseholdDataPersonSpec=personspec,
        HouseholdDataSpecification=HouseholdDataSpecificationType.ByPersons,
        TransportationDeviceSet=TransportationDeviceSets.Bus_and_two_30_km_h_Cars,
        ChargingStationSet=ChargingStationSets.Charging_At_Home_with_11_kW,
        TravelRouteSet=TravelRouteSets.Travel_Route_Set_for_15km_Commuting_Distance,
    )
    df: pandas.DataFrame = excute_lpg_with_householdata(
        year=2020,
        householddata=hhdata1,
        housetype=HouseTypes.HT23_No_Infrastructure_at_all,
        startdate="01.01.2020",
        enddate="01.03.2020",
        simulate_transportation=True,
    )
    df.to_csv(r"lpgexport.csv", index=True, sep=";")
    print("successfully exportet dataframe to lpgexport.csv")


if __name__ == "__main__":
    test_householdata_function()
