"""
A bunch of interesting data scoops from NYC education data
Author: Michael Rochlin
"""

from sodapy import Socrata
from itertools import groupby

with open('server_key') as keyfile:
    serverkey = keyfile.read().strip()

client = Socrata("data.cityofnewyork.us", serverkey)

def getSATResults2010(**kwargs):
    return client.get('zt9s-n5aj', **kwargs)

def getAPResults2010(**kwargs):
    return client.get('itfs-ms3e', **kwargs)

def getHSClassSize2010(**kwargs):
    return client.get('d3ge-anaz', **kwargs)

def zip_APs_and_SATs():
    # This function will only return schools that are in both APs and SATs. 
    aps = getAPResults2010(order="dbn")
    sats = getSATResults2010(order="dbn")
   # print aps
  #  print sats
    # zip together the scorers
    zipped = []
    api, sati = 0,0
    while api < len(aps) and sati < len(sats):
        if aps[api]["dbn"] < sats[sati]["dbn"]: 
            api += 1
        elif aps[api]["dbn"] > sats[sati]["dbn"]: 
            sati += 1
        else:
            zipped.append((aps[api], sats[sati]))
            sati += 1
            api += 1
    
    def separate(zippedSchool):
        dbn = zippedSchool[0]["dbn"]
        names = [zippedSchool[0]["schoolname"], zippedSchool[1]["school_name"]]
        data1 = {k: zippedSchool[0][k] for k in zippedSchool[0] if k not in ["dbn", "schoolname", "school_name"]}
        data2 = {k: zippedSchool[1][k] for k in zippedSchool[1] if k not in ["dbn", "schoolname", "school_name"]}
        return { "dbn": dbn, "schoolnames": names, "apdata": data1, "satdata":data2 }

    return map(separate, zipped)

def matchtoenrollment():
    classes = sorted(getHSClassSize2010(where="grade_='09-12'", order="school_code", limit=10000), key=lambda s: "0"+s["csd"]+s["school_code"])
    def setdbn(cl):
        cl["dbn"] = "0"+cl["csd"] + cl["school_code"]
    map(setdbn, classes)
    classes_uniq = []
    for dbn, g in groupby(classes, lambda cl: cl["dbn"]):
        classes_uniq.append( { "dbn" : dbn, "data" : list(g) } )
    classes = list(classes_uniq)
    aps_and_sats = zip_APs_and_SATs()
    zipped = []
    api, sati = 0,0
    while api < len(aps_and_sats) and sati < len(classes):
        code = classes[sati]["dbn"]
        if aps_and_sats[api]["dbn"] < code: 
            api += 1
        elif aps_and_sats[api]["dbn"] > code: 
            sati += 1
        else:
            print type(classes[sati]["data"])
            entry = { k : aps_and_sats[api][k] for k in aps_and_sats[api] }
            entry["enrollment"] = classes[sati]["data"] 
            entry["schoolnames"].append(classes[sati]["data"][0]["school_name"])
            zipped.append(entry)
            sati += 1
            api += 1
   
    return zipped
    


if __name__ == "__main__":
    #matchtoenrollment()
#    for school in zip_APs_and_SATs():
#        print "%s %s %s %s" % (school["dbn"], str(school["schoolnames"]), str(school["apdata"]), str(school["satdata"]))

    print set([s["dbn"][2] for s in zip_APs_and_SATs()])

    for school in matchtoenrollment():
        print "{dbn} {schoolnames}".format(**{ k : str(school[k]) for k in ["dbn","schoolnames"]})

