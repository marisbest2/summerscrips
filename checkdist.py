import googlemaps
import datetime
import sys
import json

"""
This program finds the approximate shortest transit time between 
two addresses by replacing walking with biking 
It does not account for waiting time
Michael R
"""

def mini(lst, key=lambda x: x):
    """
    Finds min and returns both the best and the index of the best
    Optional parameter @param key to use as a getter
    """
    best, besti = lst[0],0
    for i in xrange(1,len(lst)): 
        if key(lst[i]) < key(best):
            best, besti = lst[i], i
    return best,besti


def to(addr1, addr2):
    """ distance from addr1 to addr2 """
    directions_result = gmaps.directions(addr1,
                                     addr2,
                                     mode="transit",
                                     alternatives=True)

    best,besti = mini(map(calc_time, directions_result), key=lambda x: x[0])
    return best

def from_addr(addr1, addr2): return to(addr2, addr1)


def calc_time(directions_result):
    """ 
    replaces all walking legs with biking  
    returns total time in seconds along with the updated route
    """

    # there is only one leg
    legs = directions_result["legs"][0]["steps"]

    steps = map(lambda x: (x["travel_mode"], x["start_location"], x["end_location"]), legs)

    walking = filter(lambda x: x[0] == "WALKING", steps)
    transit = filter(lambda x: x[0] == "TRANSIT", steps)


    walking_to_biking = map(lambda x: gmaps.directions(
        x[1], x[2],
        mode="bicycling"), walking)

    transit_final = map(lambda x: gmaps.directions(
        x[1], x[2], mode="transit"), transit)


    walking_addrs = map(lambda x : (x[0]["legs"][0]["start_address"], x[0]["legs"][0]["end_address"]), walking_to_biking)
    transit_addrs = map(lambda x : (x[0]["legs"][0]["start_address"], x[0]["legs"][0]["end_address"]), transit_final)

    all_legs = map(lambda x:
        sum(map(lambda y: y["duration"]["value"], x[0]["legs"]))
        ,walking_to_biking+transit_final)

    final = zip(all_legs, walking+transit, walking_addrs+transit_addrs)


    def reconstruct():
        w,t = 0,len(walking)
        arr = []
        for i in xrange(len(all_legs)):
            if steps[i][0] == "TRANSIT":
                arr.append(final[t])
                t += 1
            else:
                arr.append(final[w])
                w += 1
        return arr


    total_time = sum(all_legs)     

    return total_time, reconstruct()



if __name__ == "__main__":
    with open('server_key', 'r') as keyfile:
        key = keyfile.readline()
        # trims the key if necessary
        if key[-1] == '\n': key = key[:-1]

    gmaps = googlemaps.Client(key=key)

    addr1 = sys.argv[1]
    addr2 = sys.argv[2]
    
    there = to(addr1,addr2)
    back = from_addr(addr1,addr2)
    
    (t,best),besti = mini((there,back))

    print "Total time:", datetime.timedelta(seconds=t)

    for step in best:
        print "From {0} to {1} by {2} takes {3}".format(step[2][0], step[2][1], 
            step[1][0], datetime.timedelta(seconds=step[0])).replace("WALKING", "BICYCLING")




