import glob
import io
import os
import pathlib
import random
import shutil
import stat
import subprocess
import sys
import time
import traceback
import zipfile
from pathlib import Path
from typing import Any, List, Union, Optional

import pandas as pd  # type: ignore
import requests

from pylpg.lpgdata import *
from pylpg.lpgpythonbindings import *


def execute_lpg_tsib(
    year: int,
    number_of_households: int,
    number_of_people_per_household: int,
    startdate: str = None,
    enddate: str = None,
    transportation: bool = False,
    energy_intensity: EnergyIntensityType = EnergyIntensityType.Random,
) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor(1, False)
    if number_of_households < 1:
        print("too few households")
        raise Exception("Need at least one household")

    # basic default spec
    request = lpe.make_default_lpg_settings(year)

    # create random households
    for idx in range(number_of_households):
        hhd: HouseholdData = HouseholdData()
        hhd.HouseholdDataSpecification = HouseholdDataSpecificationType.ByPersons
        hhd.HouseholdDataPersonSpec = HouseholdDataPersonSpecification()
        hhd.HouseholdDataPersonSpec.Persons = []
        hhd.ChargingStationSet = (
            ChargingStationSets.Charging_At_Home_with_03_7_kW_output_results_to_Car_Electricity
        )
        hhd.TravelRouteSet = (
            TravelRouteSets.Travel_Route_Set_for_30km_Commuting_Distance
        )
        hhd.TransportationDeviceSet = TransportationDeviceSets.Bus_and_two_30_km_h_Cars
        hhd.HouseholdDataPersonSpec.Persons = make_reasonable_family(
            number_of_people_per_household
        )
        assert request.House is not None, "HouseData was None"
        request.House.Households.append(hhd)

    # set more parameters
    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    request.CalcSpec.EnergyIntensityType = energy_intensity
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    if transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)

    # write to json
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)

    # execute
    lpe.execute_lpg_binaries()

    # read the results and return as dataframe
    return lpe.read_all_json_results_in_directory()


def make_reasonable_family(person_count: int):
    previousage = 0
    persons = []
    g = 0
    for person_idx in range(person_count):

        if person_idx == 0:  # first is an adult
            age = random.randint(18, 100)
            previousage = age
            g = random.randint(0, 1)
        elif person_idx == 1:  # 2nd adult should be roughly similar age
            diffage = random.randint(0, 10)
            age = previousage - 5 + diffage
            if g == 0:
                g = 1
            else:
                g = 0
        else:  # other people are children
            age = random.randint(0, 20)
            if g == 0:
                g = 1
            else:
                g = 0
        if g == 0:
            gender = Gender.Male
        else:
            gender = Gender.Female
        pd = PersonData(age, gender)
        persons.append(pd)
    return persons


def execute_lpg_single_household(
    year: int,
    householdref: JsonReference,
    housetype: str,
    startdate: str = None,
    enddate: str = None,
    geographic_location: JsonReference = None,
    simulate_transportation: bool = False,
    chargingset: JsonReference = None,
    transportation_device_set: JsonReference = None,
    travel_route_set: JsonReference = None,
    random_seed: int = None,
    energy_intensity: EnergyIntensityType = EnergyIntensityType.Random,
    resolution: str = "00:01:00",
    calc_options: List[CalcOption] = None,
) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor(1, False)

    # basic request
    request = lpe.make_default_lpg_settings(year)
    if random_seed is not None and request.CalcSpec is not None:
        request.CalcSpec.RandomSeed = random_seed
    assert request.House is not None, "HouseData was None"
    request.House.HouseTypeCode = housetype
    hhnamespec = HouseholdNameSpecification(householdref)
    hhn = HouseholdData(
        None,
        None,
        hhnamespec,
        "hhid",
        "hhname",
        chargingset,
        transportation_device_set,
        travel_route_set,
        None,
        HouseholdDataSpecificationType.ByHouseholdName,
    )
    request.House.Households.append(hhn)

    if request.CalcSpec is None:
        raise Exception("Failed to initialize the calculation spec")
    if startdate is not None:
        request.CalcSpec.set_StartDate(startdate)
    if enddate is not None:
        request.CalcSpec.set_EndDate(enddate)
    request.CalcSpec.EnergyIntensityType = energy_intensity
    calcspecfilename = Path(lpe.calculation_directory, "calcspec.json")
    request.CalcSpec.GeographicLocation = geographic_location
    if simulate_transportation:
        request.CalcSpec.EnableTransportation = True
        request.CalcSpec.CalcOptions.append(CalcOption.TansportationDeviceJsons)
    request.CalcSpec.ExternalTimeResolution = resolution
    if calc_options:
        request.CalcSpec.CalcOptions = calc_options
    with open(calcspecfilename, "w") as calcspecfile:
        jsonrequest = request.to_json(indent=4)  # type: ignore
        calcspecfile.write(jsonrequest)
    lpe.execute_lpg_binaries()

    return lpe.read_all_json_results_in_directory()


def execute_lpg_with_householdata(
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
    random_seed: int = None,
    energy_intensity: EnergyIntensityType = EnergyIntensityType.Random,
):
    try:
        print(
            "Starting calc with "
            + str(calculation_index)
            + " for "
            + (householddata.Name or "nameless household")
        )
        lpe: LPGExecutor = LPGExecutor(calculation_index, clear_previous_calc)

        # basic request
        request = lpe.make_default_lpg_settings(year)
        assert request.House is not None, "Housedata was None"
        request.House.HouseTypeCode = housetype
        if random_seed is not None and request.CalcSpec is not None:
            request.CalcSpec.RandomSeed = random_seed
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
        request.CalcSpec.EnergyIntensityType = energy_intensity
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


def execute_lpg_with_many_householdata(
    year: int,
    householddata: List[HouseholdData],
    housetype: str,
    startdate: str = None,
    enddate: str = None,
    simulate_transportation: bool = False,
    target_heating_demand: Optional[float] = None,
    target_cooling_demand: Optional[float] = None,
    calculation_index: int = 1,
    clear_previous_calc: bool = False,
    random_seed: int = None,
    energy_intensity: EnergyIntensityType = EnergyIntensityType.Random,
):
    try:
        print(
            "Starting calc with "
            + str(calculation_index)
            + " for "
            + str(len(householddata))
            + " households"
        )
        lpe: LPGExecutor = LPGExecutor(calculation_index, clear_previous_calc)

        # basic request
        request = lpe.make_default_lpg_settings(year)
        assert request.House is not None, "Housedata was None"
        request.House.HouseTypeCode = housetype
        if random_seed is not None and request.CalcSpec is not None:
            request.CalcSpec.RandomSeed = random_seed
        if target_heating_demand is not None:
            request.House.TargetHeatDemand = target_heating_demand
        if target_cooling_demand is not None:
            request.House.TargetCoolingDemand = target_cooling_demand
        request.House.Households = request.House.Households + householddata
        if request.CalcSpec is None:
            raise Exception("Failed to initialize the calculation spec")
        if startdate is not None:
            request.CalcSpec.set_StartDate(startdate)
        if enddate is not None:
            request.CalcSpec.set_EndDate(enddate)
        request.CalcSpec.EnergyIntensityType = energy_intensity
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


def execute_lpg_with_householdata_with_csv_save(
    year: int,
    householddata: HouseholdData,
    housetype: str,
    startdate: str = None,
    enddate: str = None,
    simulate_transportation: bool = False,
    target_heating_demand: Optional[float] = None,
    target_cooling_demand: Optional[float] = None,
    calculation_index: int = 1,
):
    try:
        df = execute_lpg_with_householdata(
            year,
            householddata,
            housetype,
            startdate,
            enddate,
            simulate_transportation,
            target_heating_demand,
            target_cooling_demand,
            calculation_index,
            True,
        )
        df_electricity = df["Electricity_HH1"]
        df_electricity.to_csv("R" + str(calculation_index) + ".csv")
        calcdir = "C" + str(calculation_index)
        if os.path.exists(calcdir):
            print("cleaning up " + calcdir)
            shutil.rmtree(calcdir)
            time.sleep(1)
    except OSError as why:
        print("Exception: " + str(why))
        traceback.print_stack()
        raise
    except:  # catch *all* exceptions
        e = sys.exc_info()[0]
        print("Exception: " + str(e))
        traceback.print_stack()
        raise


def execute_grid_calc(
    year: int,
    household_size_list: List[int],
    housetype: str,
    startdate: str = None,
    enddate: str = None,
    simulate_transportation: bool = False,
    chargingset: JsonReference = None,
    transportation_device_set: JsonReference = None,
    travel_route_set: JsonReference = None,
) -> pd.DataFrame:
    lpe: LPGExecutor = LPGExecutor(1, True)

    # basic request
    request = lpe.make_default_lpg_settings(year)
    assert request.CalcSpec is not None, "Calcspec was None"
    request.CalcSpec.CalcOptions.clear()
    request.CalcSpec.CalcOptions.append(CalcOption.JsonHouseSumFiles)
    if len(household_size_list) < 1:
        raise Exception("need at least one household.")

    assert request.House is not None, "Housedata was None"
    request.House.HouseTypeCode = housetype
    count = 1
    for hs in household_size_list:
        hhdps: HouseholdDataPersonSpecification = HouseholdDataPersonSpecification(
            make_reasonable_family(hs)
        )
        hhn = HouseholdData(
            hhdps,
            None,
            None,
            "hhid",
            "hhname" + str(count),
            chargingset,
            transportation_device_set,
            travel_route_set,
            None,
            HouseholdDataSpecificationType.ByPersons,
        )
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
    @staticmethod
    def retrieve_lpg_binaries(path: Path):
        """
        Downloads the LoadProfileGenerator binaries

        :param path: The path where the LPG binaries will be installed
        :type path: Path
        """
        # determine correct link and destination folder depending on the platform
        if sys.platform == "linux" or sys.platform == "linux2":
            url = "https://www.loadprofilegenerator.de/setup/LPG10.10.0_linux.zip"
            folder_name = "LPG_linux"
        elif sys.platform == "win32":
            url = "https://www.loadprofilegenerator.de/setup/LPG10.10.0_core.zip"
            folder_name = "LPG_win"
        else:
            raise Exception("Operating system not supported: " + sys.platform)

        print("Downloading LPG binaries from " + url)

        try:
            # download the LPG binaries from LoadProfileGenerator.de
            response = requests.get(url)
            # store the zipped result in a temporary buffer and extract it
            zipped_result = zipfile.ZipFile(io.BytesIO(response.content))
            destination_folder = os.path.join(path, folder_name)
            zipped_result.extractall(destination_folder)
        except Exception as e:
            raise Exception(f"Could not install the LoadProfileGenerator binaries: {e}")

        if sys.platform == "linux":
            # on linux, make the file executable
            fullname = os.path.join(destination_folder, "simengine2")
            os.chmod(str(fullname), stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            print(
                "Permissions set for simengine2:"
                + str(oct(os.stat(str(fullname))[stat.ST_MODE])[-3:])
            )

    def lpg_simengine_filepath(self) -> str:
        """returns the path of the LPG simulation engine executable file"""
        return os.path.join(self.calculation_src_directory, self.simengine_src_filename)

    def are_lpg_binaries_available(self) -> bool:
        """checks if the LPG executable is available"""
        return os.path.isfile(self.lpg_simengine_filepath())

    def __init__(self, calcidx: int, clear_previous_calc: bool):
        self.working_directory = pathlib.Path(__file__).parent.absolute()
        # get LPG binary directory and executable name depending on platform
        if sys.platform == "linux" or sys.platform == "linux2":
            self.calculation_src_directory = Path(self.working_directory, "LPG_linux")
            self.simengine_src_filename = "simengine2"
        elif sys.platform == "win32":
            self.calculation_src_directory = Path(self.working_directory, "LPG_win")
            self.simengine_src_filename = "simengine2.exe"
        else:
            raise Exception("unknown operating system detected: " + sys.platform)

        # check if the executable exists
        if not self.are_lpg_binaries_available():
            # download the binaries for this system
            LPGExecutor.retrieve_lpg_binaries(self.working_directory)
            if not self.are_lpg_binaries_available():
                raise Exception("Could not install the LPG binaries.")

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

    def error_tolerating_directory_clean(self, path: Union[Path, str]):
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
        pathname = self.lpg_simengine_filepath()
        print("executing in " + str(self.calculation_directory))
        subprocess.run(
            [pathname, "processhousejob", "-j", "calcspec.json"],
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

    @staticmethod
    def parse_json_profile(filepath: str) -> JsonSumProfile | JsonEnumProfile:
        """parses a single json profile file"""
        print("Reading json file " + str(filepath))
        with open(str(filepath)) as json_file:
            filecontent: str = json_file.read()  # type: ignore
            try:
                # try to load as a sum profile
                profile: JsonSumProfile = JsonSumProfile.from_json(filecontent)  # type: ignore
            except Exception:
                try:
                    # try to load as enum profile instead
                    profile = JsonEnumProfile.from_json(filecontent)
                except Exception as e:
                    print(f"Could not parse Json file {filepath} - skipping it")
        return profile

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
            profile = self.parse_json_profile(file)
            if profile.LoadTypeName is None:
                raise Exception("Empty load type name on " + str(file))
            if (
                profile is None
                or profile.HouseKey is None
                or profile.HouseKey.HHKey is None
            ):
                raise Exception("empty housekey")
            key: str = profile.LoadTypeName + "_" + str(profile.HouseKey.HHKey.Key)
            df[key] = profile.Values
            if isFirst:
                isFirst = False
                ts = profile.StartTime
                timestamps = pd.date_range(ts, periods=len(profile.Values), freq="min")
                df.index = timestamps
        return df
