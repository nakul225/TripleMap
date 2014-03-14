#This code will keep a track of locations of each bus
from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
import time

STOPPED = 0
APPROACHING = 1
LEAVING = 2

map_colloquial_bus_number_to_route =    {
                                                    '1 S.Walnut':'1001529',
                                                    '1 Fee Lane':'1001531',
                                                    '2 S.Rogers':'1001527',
                                                    '3 Curry Pike':'1001537',
                                                    '3 College Mall':'1001536',
                                                    '4 High Street':'1001541',
                                                    '4 Bloomfield':'1001539',
                                                    '5':'1001543',
                                                    '6':'1001548',
                                                    '9':'1001561',
                                                    'A':'2000316',
                                                    'B':'2000318',
                                                    'D':'2000319',
                                                    'E':'2000320'
                                                }

def get_all_buses_status():
    """
    This function returns latitude and longitude of each bus
    format : {"bus name/number":(latitude, longitude)}
    example:    (
                    "555":(39.16641998291, -86.526893615723)
                )
    """
    dict_bus_lat_lng = {}
    doublemap_url = "http://bloomington.doublemap.com/map/v2/buses"
    response = json.loads(urllib.urlopen(doublemap_url).read())
    if len(response) == 0:
        print "Something went wrong while getting status of each bus..."
        sys.exit(0)    
    for bus in response:
        bus_number = bus['name']
        lat = bus['lat']
        lng = bus['lon']
        route = bus['route']
        bus_id = bus['id']
        lastUpdate = bus['lastUpdate']
        dict_bus_lat_lng[bus_number] = (lat,lng)
    return dict_bus_lat_lng

def test_get_all_buses_status():
    """
    Test function
    """
    return len(get_all_buses_status())

def get_coordinates_of_buses(bus_number_list):
    """
    def pulls out coordinates infromation for the bus numbers given as input
    """
    dict_all_buses_lat_lng = get_all_buses_status()
    dict_bus_lat_lng = {}
    for bus_number in bus_number_list:
        dict_bus_lat_lng[bus_number] = (dict_all_buses_lat_lng[bus_number]['lat'], dict_all_buses_lat_lng[bus_number]['lng'])
    return dict_bus_lat_lng

def get_bus_status(colloquial_bus_numbers, target_location_coordinates):
    """
    This function returns a dictionary with status of each bus on each input route
    input_route_list can have one or a list of bus numbers. This will be used to get the route numbers. 
    For example, user might want yo travel by route 6 OR route 9. Then we feed both route numbers for route6 and 9 to this function.
    Output: Each bus running on the input route along with its latitude and longitude.
    """
    #Find bus numbers from input colloquial bus numbers list
    #TODO Keep a JSON file that can be updated so that colloquial bus number can be mapped to actual bus numbers used by Doublemap
    map_colloquial_to_acutal_bus_number = {'9':['9725','243'],'9L':'344','6':['553','555','554','551']}
    
    bus_number_list = []
    for bus in colloquial_bus_numbers:
        bus_number_list.extend(map_colloquial_to_acutal_bus_number[bus])

    #Query doublemap API and get status for each route
    dict_bus_lat_lng = get_coordinates_of_buses(bus_number_list)
    return None

def is_bus_approaching_waiting_or_leaving_point(bus_coordinates_before, bus_coordinates_later, target_location_coordinates):
    """
    Find if the bus is approaching a given location or not.
    bus_coordinates_before : coordinates of bus at time T
    bus_coordinates_later : coordinates of bus at time T+t where t!=0
    """
    #find difference between distance_before and distance_later
    distance_before = find_distance_between_coordinates(bus_coordinates_before, target_location_coordinates)
    distance_later = find_distance_between_coordinates(bus_coordinates_later, target_location_coordinates)
    distance = distance_before - distance_later
    if distance == 0:
        return (distance, STOPPED)
    elif distance > 0:
        return (distance, APPROACHING)
    else:
        return (distance, LEAVING)

def find_distance_between_coordinates(bus_coordinates, target_location_coordinates):
    """
    code reference: http://stackoverflow.com/a/19412565/2762836
    """
    R = 6373.0
    lat1 = radians(bus_coordinates[0])
    lon1 = radians(bus_coordinates[1])
    lat2 = radians(target_location_coordinates[0])
    lon2 = radians(target_location_coordinates[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    return distance
    
if __name__ == "__main__":
    #test if the API is working
    if test_get_all_buses_status():
        print "Code accessing Doublemap API is working correctly"
    else:
        print "Something seems to be wrong with accessing code of Doublemap API"

    colloquial_bus_numbers = ['6','9']
    target_location_coordinates = (39.171539306641,-86.512619018555)
    while True:
        time.sleep(5) # delays for 5 seconds
        #Find which bus is approaching
        dict_bus_status = get_bus_status(colloquial_bus_numbers, target_location_coordinates)
        for bus in dict_bus_status.keys():
            if bus['status'][1] == APPROACHING:
                print "Bus ",bus," is approaching and is at distance: ",bus['status'][0]

