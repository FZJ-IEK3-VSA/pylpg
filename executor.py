import json
from concurrent.futures.thread import ThreadPoolExecutor
import os
import pylpg
import lpgdata
import lpgpythonbindings
import sys


def exec_lpg(filename):
    with open(filename) as f:
        data = json.load(f)
    i = 0
    executor = ThreadPoolExecutor(max_workers=18)
    print("Total: " + str(len(data["Assigns"])))
    futures = []
    for x in data["Assigns"]:
        hhname = x["LPG"]["HHName"]
        print(hhname)
        i += 1
        if i > 100:
            print("Reached maximum count, quitting")
            break
        resultfilename = "R" + str(i) + ".csv"
        if os.path.exists(resultfilename):
            print(resultfilename + " exists, skipping")
            continue
        persons = []
        lpgPersons = x["LPG"]["Persons"]
        for person in lpgPersons:
            pd = lpgdata.PersonLivingTag(person["LivingPatternTag"], person["PersonName"])
            print(person["PersonName"] + " - " + person["LivingPatternTag"])
            persons.append(pd)
        templatespec = lpgdata.HouseholdTemplateSpecification(persons, hhname)
        templatespec.ForbiddenTraitTags.append(lpgdata.TraitTags.Food_Brunching)
        hd = lpgdata.HouseholdData(HouseholdTemplateSpec=templatespec, UniqueHouseholdId="HH"+str(i),
                                   TravelRouteSet=lpgdata.TravelRouteSets.Travel_Route_Set_for_15km_Commuting_Distance,
                                   ChargingStationSet=lpgdata.ChargingStationSets.Charging_At_Home_with_03_7_kW,
                                   TransportationDeviceSet=lpgdata.TransportationDeviceSets.Bus_and_two_30_km_h_Cars
                                   )
        hd.Name = "HH"+str(i)
        hd.HouseholdDataSpecification = lpgpythonbindings.HouseholdDataSpecificationType.ByTemplateName
        print("submitting job #" + hd.Name)
        futures.append(executor.submit(pylpg.excute_lpg_with_householdata, year=2020, householddata=hd,
                       housetype=lpgdata.HouseTypes.HT23_No_Infrastructure_at_all,
                       startdate="01.01.2020",
                       enddate="2020-12-31",
                       simulate_transportation=False,
                       calculation_index=i))

    print("finished submitting")
    executor.shutdown(wait=True)


if __name__ == "__main__":
    fn = sys.argv[1]
    print(fn)
    exec_lpg(fn)
