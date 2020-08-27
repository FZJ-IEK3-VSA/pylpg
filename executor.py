import json
from concurrent.futures.thread import ThreadPoolExecutor

import pylpg
import lpgdata
import lpgpythonbindings


def exec_lpg():
    with open('assignments.json') as f:
        data = json.load(f)
    i = 0
    executor = ThreadPoolExecutor(max_workers=20)
    futures = []
    for x in data["Assigns"]:
        hhname = x["LPG"]["HHName"]
        print(hhname)
        i += 1
        persons = []
        for person in x["LPG"]["Persons"]:
            pd = lpgdata.PersonData(person["Age"], person["Gender"])
            pd.LivingPatternTag = person["LivingPatternTag"]
            persons.append(pd)
        templatespec = lpgdata.HouseholdTemplateSpecification(persons, hhname)
        hd = lpgdata.HouseholdData(HouseholdTemplateSpec=templatespec, UniqueHouseholdId="HH"+str(i),
                                   TravelRouteSet=lpgdata.TravelRouteSets.Travel_Route_Set_for_15km_Commuting_Distance,
                                   ChargingStationSet=lpgdata.ChargingStationSets.Charging_At_Home_with_03_7_kW,
                                   TransportationDeviceSet=lpgdata.TransportationDeviceSets.Bus_and_two_30_km_h_Cars
                                   )
        hd.Name = "HH"+str(i)
        hd.HouseholdDataSpecification = lpgpythonbindings.HouseholdDataSpecificationType.ByTemplateName
        print("submitting")
        futures.append(executor.submit(pylpg.excute_lpg_with_householdata, year=2020, householddata=hd,
                       housetype=lpgdata.HouseTypes.HT23_No_Infrastructure_at_all,
                       startdate="01.01.2020",
                       enddate="2020-12-31",
                       simulate_transportation=False,
                       calculation_index=i))
        #if i > 10:
         #   break
    print("finished submitting")
    executor.shutdown(wait=True)


if __name__ == "__main__":
    exec_lpg()
