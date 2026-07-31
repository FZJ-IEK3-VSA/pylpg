"""
Minimalistic example for using the pylpg package with a household template
"""
from pylpg import lpg_execution, lpgdata
import utils

LPG_BINARY_PATH = None

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

utils.print_lpg_binary_source(LPG_BINARY_PATH)

execute_kwargs = {
    "enable_flexibility": True,
    "enable_transportation": True,
}
if utils.supports_lpg_binary_path(lpg_execution.execute_lpg_with_householddata_enabled_flex_and_transport_custom):
    execute_kwargs["lpg_binary_path"] = LPG_BINARY_PATH

data = lpg_execution.execute_lpg_with_householddata_enabled_flex_and_transport_custom(
    2022,
    household,
    lpgdata.HouseTypes.HT20_Single_Family_House_no_heating_cooling,
    **execute_kwargs,
)

# Extract the generated electricity load profile
electricity_profile = data["Electricity_HH1"]
print(electricity_profile)

# Resample to 15 minute resolution
profile = electricity_profile.resample("15min").sum()

# Show a carpet plot
utils.carpet_plot(profile)