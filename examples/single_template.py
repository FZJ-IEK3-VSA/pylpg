"""
Minimalistic example for using the pylpg package with a household template
"""
from pylpg import lpg_execution, lpgdata
import utils

# Simulate the CHR01 household template for the year 2022
household = lpgdata.HouseholdData(
    None,
    lpgdata.HouseholdTemplateSpecification(
        HouseholdTemplateName=lpgdata.HouseholdTemplates.CHR01_Couple_both_at_Work,
    ),
    None,
    "hhid",
    "hhname",
    None,
    None,
    None,
    None,
    HouseholdDataSpecification=lpgdata.HouseholdDataSpecificationType.ByTemplateName,
)

data = lpg_execution.execute_lpg_with_householddata_custom(
    2022,
    household,
    lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling,
    enable_flexibility=True,
    enable_transportation=True,
    # Example: lpg_binary_path=r"C:\Tools\LPG\SimulationEngine.exe"
)

# Extract the generated electricity load profile
electricity_profile = data["Electricity_HH1"]
print(electricity_profile)

# Resample to 15 minute resolution
profile = electricity_profile.resample("15min").sum()

# Show a carpet plot
utils.carpet_plot(profile)