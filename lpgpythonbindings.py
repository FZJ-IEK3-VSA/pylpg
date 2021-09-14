from __future__ import annotations
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json  # type: ignore
from typing import List, Optional, Any, Dict
from enum import Enum


class LoadTypePriority(str, Enum):
    Undefined = "Undefined"
    Mandatory = "Mandatory"
    RecommendedForHouseholds = "RecommendedForHouseholds"
    RecommendedForHouses = "RecommendedForHouses"
    OptionalLoadtypes = "OptionalLoadtypes"
    All = "All"


class OutputFileDefault(str, Enum):
    All = "All"
    OnlyOverallSum = "OnlyOverallSum"
    OnlySums = "OnlySums"
    OnlyDeviceProfiles = "OnlyDeviceProfiles"
    Reasonable = "Reasonable"
    ReasonableWithCharts = "ReasonableWithCharts"
    ReasonableWithChartsAndPDF = "ReasonableWithChartsAndPDF"
    NoFiles = "NoFiles"
    ForSettlementCalculations = "ForSettlementCalculations"


class EnergyIntensityType(str, Enum):
    EnergySaving = "EnergySaving"
    Random = "Random"
    EnergyIntensive = "EnergyIntensive"
    AsOriginal = "AsOriginal"
    EnergySavingPreferMeasured = "EnergySavingPreferMeasured"
    EnergyIntensivePreferMeasured = "EnergyIntensivePreferMeasured"


class CalcOption(str, Enum):
    HouseSumProfilesFromDetailedDats = "HouseSumProfilesFromDetailedDats"
    OverallDats = "OverallDats"
    OverallSum = "OverallSum"
    DetailedDatFiles = "DetailedDatFiles"
    ActionCarpetPlot = "ActionCarpetPlot"
    TimeOfUsePlot = "TimeOfUsePlot"
    VariableLogFile = "VariableLogFile"
    ActivationsPerHour = "ActivationsPerHour"
    DaylightTimesList = "DaylightTimesList"
    ActivationFrequencies = "ActivationFrequencies"
    DeviceProfilesIndividualHouseholds = "DeviceProfilesIndividualHouseholds"
    TotalsPerLoadtype = "TotalsPerLoadtype"
    HouseholdContents = "HouseholdContents"
    TemperatureFile = "TemperatureFile"
    TotalsPerDevice = "TotalsPerDevice"
    EnergyStorageFile = "EnergyStorageFile"
    DurationCurve = "DurationCurve"
    DesiresLogfile = "DesiresLogfile"
    ThoughtsLogfile = "ThoughtsLogfile"
    PolysunImportFiles = "PolysunImportFiles"
    CriticalViolations = "CriticalViolations"
    SumProfileExternalEntireHouse = "SumProfileExternalEntireHouse"
    SumProfileExternalIndividualHouseholds = "SumProfileExternalIndividualHouseholds"
    WeekdayProfiles = "WeekdayProfiles"
    AffordanceEnergyUse = "AffordanceEnergyUse"
    TimeProfileFile = "TimeProfileFile"
    LocationsFile = "LocationsFile"
    HouseholdPlan = "HouseholdPlan"
    DeviceProfileExternalEntireHouse = "DeviceProfileExternalEntireHouse"
    DeviceProfileExternalIndividualHouseholds = "DeviceProfileExternalIndividualHouseholds"
    MakeGraphics = "MakeGraphics"
    MakePDF = "MakePDF"
    LocationCarpetPlot = "LocationCarpetPlot"
    PersonStatus = "PersonStatus"
    TransportationDeviceCarpetPlot = "TransportationDeviceCarpetPlot"
    LogErrorMessages = "LogErrorMessages"
    LogAllMessages = "LogAllMessages"
    TransportationStatistics = "TransportationStatistics"
    ActionsEachTimestep = "ActionsEachTimestep"
    CalculationFlameChart = "CalculationFlameChart"
    SumProfileExternalIndividualHouseholdsAsJson = "SumProfileExternalIndividualHouseholdsAsJson"
    JsonHouseSumFiles = "JsonHouseSumFiles"
    BodilyActivityStatistics = "BodilyActivityStatistics"
    BasicOverview = "BasicOverview"
    DeviceActivations = "DeviceActivations"
    LocationsEntries = "LocationsEntries"
    ActionEntries = "ActionEntries"
    AffordanceTaggingSets = "AffordanceTaggingSets"
    DeviceProfilesHouse = "DeviceProfilesHouse"
    HouseholdSumProfilesFromDetailedDats = "HouseholdSumProfilesFromDetailedDats"
    JsonHouseholdSumFiles = "JsonHouseholdSumFiles"
    JsonDeviceProfilesIndividualHouseholds = "JsonDeviceProfilesIndividualHouseholds"
    TansportationDeviceJsons = "TansportationDeviceJsons"
    DeviceTaggingSets = "DeviceTaggingSets"
    AffordanceDefinitions = "AffordanceDefinitions"
    JsonHouseholdSumFilesNoFlex = "JsonHouseholdSumFilesNoFlex"
    HouseholdSumProfilesCsvNoFlex = "HouseholdSumProfilesCsvNoFlex"
    FlexibilityEvents = "FlexibilityEvents"


class HouseDefinitionType(str, Enum):
    HouseData = "HouseData"
    HouseName = "HouseName"


class Gender(str, Enum):
    Male = "Male"
    Female = "Female"


class HouseholdDataSpecificationType(str, Enum):
    ByPersons = "ByPersons"
    ByTemplateName = "ByTemplateName"
    ByHouseholdName = "ByHouseholdName"


class HouseholdKeyType(str, Enum):
    Household = "Household"
    General = "General"
    House = "House"


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class StrGuid:
    StrVal: Optional[str] = ""

    def set_StrVal(self, value: str) -> StrGuid:
        self.StrVal = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class TransportationPreference:
    DestinationSite: Optional[JsonReference] = None

    def set_DestinationSite(self, value: JsonReference) -> TransportationPreference:
        self.DestinationSite = value
        return self

    DistanceFromHome: float = 0

    def set_DistanceFromHome(self, value: float) -> TransportationPreference:
        self.DistanceFromHome = value
        return self

    Angle: float = 0

    def set_Angle(self, value: float) -> TransportationPreference:
        self.Angle = value
        return self

    TransportationDeviceCategories: List[JsonReference] = field(default_factory=list)

    def set_TransportationDeviceCategories(self, value: List[JsonReference]) -> TransportationPreference:
        self.TransportationDeviceCategories = value
        return self

    Weights: List[float] = field(default_factory=list)

    def set_Weights(self, value: List[float]) -> TransportationPreference:
        self.Weights = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class PersonData:
    Age: int = 0

    def set_Age(self, value: int) -> PersonData:
        self.Age = value
        return self

    Gender: Optional[str] = ""

    def set_Gender(self, value: str) -> PersonData:
        self.Gender = value
        return self

    LivingPatternTag: Optional[str] = ""

    def set_LivingPatternTag(self, value: str) -> PersonData:
        self.LivingPatternTag = value
        return self

    PersonName: Optional[str] = ""

    def set_PersonName(self, value: str) -> PersonData:
        self.PersonName = value
        return self

    TransportationPreferences: List[TransportationPreference] = field(default_factory=list)

    def set_TransportationPreferences(self, value: List[TransportationPreference]) -> PersonData:
        self.TransportationPreferences = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class JsonReference:
    Name: Optional[str] = ""

    def set_Name(self, value: str) -> JsonReference:
        self.Name = value
        return self

    Guid: Optional[StrGuid] = None

    def set_Guid(self, value: StrGuid) -> JsonReference:
        self.Guid = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class TransportationDistanceModifier:
    RouteKey: Optional[str] = ""

    def set_RouteKey(self, value: str) -> TransportationDistanceModifier:
        self.RouteKey = value
        return self

    StepKey: Optional[str] = ""

    def set_StepKey(self, value: str) -> TransportationDistanceModifier:
        self.StepKey = value
        return self

    NewDistanceInMeters: float = 0

    def set_NewDistanceInMeters(self, value: float) -> TransportationDistanceModifier:
        self.NewDistanceInMeters = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class JsonCalcSpecification:
    LoadtypesForPostprocessing: List[str] = field(default_factory=list)

    def set_LoadtypesForPostprocessing(self, value: List[str]) -> JsonCalcSpecification:
        self.LoadtypesForPostprocessing = value
        return self

    CalculationName: Optional[str] = ""

    def set_CalculationName(self, value: str) -> JsonCalcSpecification:
        self.CalculationName = value
        return self

    CalcOptions: List[str] = field(default_factory=list)

    def set_CalcOptions(self, value: List[str]) -> JsonCalcSpecification:
        self.CalcOptions = value
        return self

    DefaultForOutputFiles: Optional[str] = ""

    def set_DefaultForOutputFiles(self, value: str) -> JsonCalcSpecification:
        self.DefaultForOutputFiles = value
        return self

    DeleteAllButPDF: bool = False

    def set_DeleteAllButPDF(self, value: bool) -> JsonCalcSpecification:
        self.DeleteAllButPDF = value
        return self

    DeleteDAT: bool = False

    def set_DeleteDAT(self, value: bool) -> JsonCalcSpecification:
        self.DeleteDAT = value
        return self

    DeviceSelection: Optional[JsonReference] = None

    def set_DeviceSelection(self, value: JsonReference) -> JsonCalcSpecification:
        self.DeviceSelection = value
        return self

    EndDate: Optional[str] = ""

    def set_EndDate(self, value: str) -> JsonCalcSpecification:
        self.EndDate = value
        return self

    EnergyIntensityType: Optional[str] = ""

    def set_EnergyIntensityType(self, value: str) -> JsonCalcSpecification:
        self.EnergyIntensityType = value
        return self

    ExternalTimeResolution: Optional[str] = ""

    def set_ExternalTimeResolution(self, value: str) -> JsonCalcSpecification:
        self.ExternalTimeResolution = value
        return self

    InternalTimeResolution: Optional[str] = ""

    def set_InternalTimeResolution(self, value: str) -> JsonCalcSpecification:
        self.InternalTimeResolution = value
        return self

    GeographicLocation: Optional[JsonReference] = None

    def set_GeographicLocation(self, value: JsonReference) -> JsonCalcSpecification:
        self.GeographicLocation = value
        return self

    LoadTypePriority: Optional[str] = ""

    def set_LoadTypePriority(self, value: str) -> JsonCalcSpecification:
        self.LoadTypePriority = value
        return self

    OutputDirectory: Optional[str] = ""

    def set_OutputDirectory(self, value: str) -> JsonCalcSpecification:
        self.OutputDirectory = value
        return self

    RandomSeed: int = 0

    def set_RandomSeed(self, value: int) -> JsonCalcSpecification:
        self.RandomSeed = value
        return self

    ShowSettlingPeriod: bool = False

    def set_ShowSettlingPeriod(self, value: bool) -> JsonCalcSpecification:
        self.ShowSettlingPeriod = value
        return self

    EnableFlexibility: bool = False

    def set_EnableFlexibility(self, value: bool) -> JsonCalcSpecification:
        self.EnableFlexibility = value
        return self

    SkipExisting: bool = False

    def set_SkipExisting(self, value: bool) -> JsonCalcSpecification:
        self.SkipExisting = value
        return self

    StartDate: Optional[str] = ""

    def set_StartDate(self, value: str) -> JsonCalcSpecification:
        self.StartDate = value
        return self

    TemperatureProfile: Optional[JsonReference] = None

    def set_TemperatureProfile(self, value: JsonReference) -> JsonCalcSpecification:
        self.TemperatureProfile = value
        return self

    DeleteSqlite: bool = False

    def set_DeleteSqlite(self, value: bool) -> JsonCalcSpecification:
        self.DeleteSqlite = value
        return self

    IgnorePreviousActivitiesWhenNeeded: bool = False

    def set_IgnorePreviousActivitiesWhenNeeded(self, value: bool) -> JsonCalcSpecification:
        self.IgnorePreviousActivitiesWhenNeeded = value
        return self

    EnableTransportation: bool = False

    def set_EnableTransportation(self, value: bool) -> JsonCalcSpecification:
        self.EnableTransportation = value
        return self

    EnableIdlemode: bool = False

    def set_EnableIdlemode(self, value: bool) -> JsonCalcSpecification:
        self.EnableIdlemode = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseReference:
    House: Optional[JsonReference] = None

    def set_House(self, value: JsonReference) -> HouseReference:
        self.House = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdDataPersonSpecification:
    Persons: List[PersonData] = field(default_factory=list)

    def set_Persons(self, value: List[PersonData]) -> HouseholdDataPersonSpecification:
        self.Persons = value
        return self

    HouseholdTags: List[str] = field(default_factory=list)

    def set_HouseholdTags(self, value: List[str]) -> HouseholdDataPersonSpecification:
        self.HouseholdTags = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class PersonLivingTag:
    LivingPatternTag: Optional[str] = ""

    def set_LivingPatternTag(self, value: str) -> PersonLivingTag:
        self.LivingPatternTag = value
        return self

    PersonName: Optional[str] = ""

    def set_PersonName(self, value: str) -> PersonLivingTag:
        self.PersonName = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdTemplateSpecification:
    Persons: List[PersonLivingTag] = field(default_factory=list)

    def set_Persons(self, value: List[PersonLivingTag]) -> HouseholdTemplateSpecification:
        self.Persons = value
        return self

    HouseholdTemplateName: Optional[str] = ""

    def set_HouseholdTemplateName(self, value: str) -> HouseholdTemplateSpecification:
        self.HouseholdTemplateName = value
        return self

    ForbiddenTraitTags: List[str] = field(default_factory=list)

    def set_ForbiddenTraitTags(self, value: List[str]) -> HouseholdTemplateSpecification:
        self.ForbiddenTraitTags = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdNameSpecification:
    HouseholdReference: Optional[JsonReference] = None

    def set_HouseholdReference(self, value: JsonReference) -> HouseholdNameSpecification:
        self.HouseholdReference = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdData:
    HouseholdDataPersonSpec: Optional[HouseholdDataPersonSpecification] = None

    def set_HouseholdDataPersonSpec(self, value: HouseholdDataPersonSpecification) -> HouseholdData:
        self.HouseholdDataPersonSpec = value
        return self

    HouseholdTemplateSpec: Optional[HouseholdTemplateSpecification] = None

    def set_HouseholdTemplateSpec(self, value: HouseholdTemplateSpecification) -> HouseholdData:
        self.HouseholdTemplateSpec = value
        return self

    HouseholdNameSpec: Optional[HouseholdNameSpecification] = None

    def set_HouseholdNameSpec(self, value: HouseholdNameSpecification) -> HouseholdData:
        self.HouseholdNameSpec = value
        return self

    UniqueHouseholdId: Optional[str] = ""

    def set_UniqueHouseholdId(self, value: str) -> HouseholdData:
        self.UniqueHouseholdId = value
        return self

    Name: Optional[str] = ""

    def set_Name(self, value: str) -> HouseholdData:
        self.Name = value
        return self

    ChargingStationSet: Optional[JsonReference] = None

    def set_ChargingStationSet(self, value: JsonReference) -> HouseholdData:
        self.ChargingStationSet = value
        return self

    TransportationDeviceSet: Optional[JsonReference] = None

    def set_TransportationDeviceSet(self, value: JsonReference) -> HouseholdData:
        self.TransportationDeviceSet = value
        return self

    TravelRouteSet: Optional[JsonReference] = None

    def set_TravelRouteSet(self, value: JsonReference) -> HouseholdData:
        self.TravelRouteSet = value
        return self

    TransportationDistanceModifiers: Optional[List[TransportationDistanceModifier]] = field(default_factory=list)

    def set_TransportationDistanceModifiers(self, value: List[TransportationDistanceModifier]) -> HouseholdData:
        self.TransportationDistanceModifiers = value
        return self

    HouseholdDataSpecification: Optional[str] = ""

    def set_HouseholdDataSpecification(self, value: str) -> HouseholdData:
        self.HouseholdDataSpecification = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseData:
    Name: Optional[str] = ""

    def set_Name(self, value: str) -> HouseData:
        self.Name = value
        return self

    HouseGuid: Optional[StrGuid] = None

    def set_HouseGuid(self, value: StrGuid) -> HouseData:
        self.HouseGuid = value
        return self

    Households: List[HouseholdData] = field(default_factory=list)

    def set_Households(self, value: List[HouseholdData]) -> HouseData:
        self.Households = value
        return self

    HouseTypeCode: Optional[str] = ""

    def set_HouseTypeCode(self, value: str) -> HouseData:
        self.HouseTypeCode = value
        return self

    TargetCoolingDemand: float = 0

    def set_TargetCoolingDemand(self, value: float) -> HouseData:
        self.TargetCoolingDemand = value
        return self

    TargetHeatDemand: float = 0

    def set_TargetHeatDemand(self, value: float) -> HouseData:
        self.TargetHeatDemand = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseCreationAndCalculationJob:
    House: Optional[HouseData] = None

    def set_House(self, value: HouseData) -> HouseCreationAndCalculationJob:
        self.House = value
        return self

    CalcSpec: Optional[JsonCalcSpecification] = None

    def set_CalcSpec(self, value: JsonCalcSpecification) -> HouseCreationAndCalculationJob:
        self.CalcSpec = value
        return self

    HouseDefinitionType: Optional[str] = HouseDefinitionType.HouseData

    def set_HouseDefinitionType(self, value: str) -> HouseCreationAndCalculationJob:
        self.HouseDefinitionType = value
        return self

    HouseRef: Optional[HouseReference] = None

    def set_HouseRef(self, value: HouseReference) -> HouseCreationAndCalculationJob:
        self.HouseRef = value
        return self

    Scenario: Optional[str] = ""

    def set_Scenario(self, value: str) -> HouseCreationAndCalculationJob:
        self.Scenario = value
        return self

    Year: Optional[str] = ""

    def set_Year(self, value: str) -> HouseCreationAndCalculationJob:
        self.Year = value
        return self

    DistrictName: Optional[str] = ""

    def set_DistrictName(self, value: str) -> HouseCreationAndCalculationJob:
        self.DistrictName = value
        return self

    PathToDatabase: Optional[str] = ""

    def set_PathToDatabase(self, value: str) -> HouseCreationAndCalculationJob:
        self.PathToDatabase = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class SingleDeviceProfile:
    Name: Optional[str] = ""

    def set_Name(self, value: str) -> SingleDeviceProfile:
        self.Name = value
        return self

    Guid: Optional[str] = ""

    def set_Guid(self, value: str) -> SingleDeviceProfile:
        self.Guid = value
        return self

    TagsBySet: Dict[str, str] = field(default_factory=dict)

    def set_TagsBySet(self, value: Dict[str, str]) -> SingleDeviceProfile:
        self.TagsBySet = value
        return self

    DeviceType: Optional[str] = ""

    def set_DeviceType(self, value: str) -> SingleDeviceProfile:
        self.DeviceType = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class TemplatePersonEntry:
    Age: int = 0

    def set_Age(self, value: int) -> TemplatePersonEntry:
        self.Age = value
        return self

    Gender: Optional[str] = ""

    def set_Gender(self, value: str) -> TemplatePersonEntry:
        self.Gender = value
        return self

    LivingPattern: Optional[str] = ""

    def set_LivingPattern(self, value: str) -> TemplatePersonEntry:
        self.LivingPattern = value
        return self

    TemplateName: Optional[str] = ""

    def set_TemplateName(self, value: str) -> TemplatePersonEntry:
        self.TemplateName = value
        return self

    PersonName: Optional[str] = ""

    def set_PersonName(self, value: str) -> TemplatePersonEntry:
        self.PersonName = value
        return self

    Name: Optional[str] = ""

    def set_Name(self, value: str) -> TemplatePersonEntry:
        self.Name = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdKey:
    Key: Optional[str] = ""

    def set_Key(self, value: str) -> HouseholdKey:
        self.Key = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class LoadTypeInformation:
    ConversionFaktor: float = 0

    def set_ConversionFaktor(self, value: float) -> LoadTypeInformation:
        self.ConversionFaktor = value
        return self

    FileName: Optional[str] = ""

    def set_FileName(self, value: str) -> LoadTypeInformation:
        self.FileName = value
        return self

    Guid: Optional[StrGuid] = None

    def set_Guid(self, value: StrGuid) -> LoadTypeInformation:
        self.Guid = value
        return self

    Name: Optional[str] = ""

    def set_Name(self, value: str) -> LoadTypeInformation:
        self.Name = value
        return self

    ShowInCharts: bool = False

    def set_ShowInCharts(self, value: bool) -> LoadTypeInformation:
        self.ShowInCharts = value
        return self

    UnitOfPower: Optional[str] = ""

    def set_UnitOfPower(self, value: str) -> LoadTypeInformation:
        self.UnitOfPower = value
        return self

    UnitOfSum: Optional[str] = ""

    def set_UnitOfSum(self, value: str) -> LoadTypeInformation:
        self.UnitOfSum = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class HouseholdKeyEntry:
    HouseDescription: Optional[str] = ""

    def set_HouseDescription(self, value: str) -> HouseholdKeyEntry:
        self.HouseDescription = value
        return self

    HouseholdDescription: Optional[str] = ""

    def set_HouseholdDescription(self, value: str) -> HouseholdKeyEntry:
        self.HouseholdDescription = value
        return self

    HHKey: Optional[HouseholdKey] = None

    def set_HHKey(self, value: HouseholdKey) -> HouseholdKeyEntry:
        self.HHKey = value
        return self

    HouseholdName: Optional[str] = ""

    def set_HouseholdName(self, value: str) -> HouseholdKeyEntry:
        self.HouseholdName = value
        return self

    HouseName: Optional[str] = ""

    def set_HouseName(self, value: str) -> HouseholdKeyEntry:
        self.HouseName = value
        return self

    KeyType: Optional[str] = ""

    def set_KeyType(self, value: HouseholdKeyType) -> HouseholdKeyEntry:
        self.KeyType = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class JsonSumProfile:
    Name: Optional[str] = ""

    def set_Name(self, value: str) -> JsonSumProfile:
        self.Name = value
        return self

    TimeResolution: str = "00:01:00"

    def set_TimeResolution(self, value: str) -> JsonSumProfile:
        self.TimeResolution = value
        return self

    Values: List[float] = field(default_factory=list)

    def set_Values(self, value: List[float]) -> JsonSumProfile:
        self.Values = value
        return self

    StartTime: Optional[str] = ""

    def set_StartTime(self, value: str) -> JsonSumProfile:
        self.StartTime = value
        return self

    LoadTypeName: Optional[str] = ""

    def set_LoadTypeName(self, value: str) -> JsonSumProfile:
        self.LoadTypeName = value
        return self

    LoadTypeDefinition: Optional[LoadTypeInformation] = None

    def set_LoadTypeDefinition(self, value: LoadTypeInformation) -> JsonSumProfile:
        self.LoadTypeDefinition = value
        return self

    Unit: Optional[str] = ""

    def set_Unit(self, value: str) -> JsonSumProfile:
        self.Unit = value
        return self

    HouseKey: Optional[HouseholdKeyEntry] = None

    def set_HouseKey(self, value: HouseholdKeyEntry) -> JsonSumProfile:
        self.HouseKey = value
        return self


# noinspection PyPep8Naming, PyUnusedLocal
@dataclass_json
@dataclass
class JsonDeviceProfiles:
    DeviceProfiles: List[SingleDeviceProfile] = field(default_factory=list)

    def set_DeviceProfiles(self, value: List[SingleDeviceProfile]) -> JsonDeviceProfiles:
        self.DeviceProfiles = value
        return self

    TimeResolution: str = "00:01:00"

    def set_TimeResolution(self, value: str) -> JsonDeviceProfiles:
        self.TimeResolution = value
        return self

    StartTime: Optional[str] = ""

    def set_StartTime(self, value: str) -> JsonDeviceProfiles:
        self.StartTime = value
        return self

    LoadTypeName: Optional[str] = ""

    def set_LoadTypeName(self, value: str) -> JsonDeviceProfiles:
        self.LoadTypeName = value
        return self

    LoadTypeDefinition: Optional[LoadTypeInformation] = None

    def set_LoadTypeDefinition(self, value: LoadTypeInformation) -> JsonDeviceProfiles:
        self.LoadTypeDefinition = value
        return self

    Unit: Optional[str] = ""

    def set_Unit(self, value: str) -> JsonDeviceProfiles:
        self.Unit = value
        return self

