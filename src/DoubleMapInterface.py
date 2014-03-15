#This code will keep a track of locations of each bus
from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
from pprint import pprint
import time

STOPPED = 0
APPROACHING = 1
LEAVING = 2

#The map for regular bus num and bus number

#Find bus numbers from input colloquial bus numbers list
#TODO Keep a JSON file that can be updated so that colloquial bus number can be mapped to actual bus numbers used by Doublemap
#map_colloquial_to_acutal_bus_number = {'9':['9725','243'],'9L':'344','6':['553','555','554','551']}
map_colloquial_to_acutal_bus_number = {'EL':['29727', '29732'], 'CL':['29729'] }

bus_number_list = []


#Map to convert colloquial bus number to actual bus number
def loadMapFromFile(fileName):
    with open(fileName, "r") as jsFile:
        obj = json.loads(fileName.read())
        pprint(obj)


def get_all_buses_status():
    """
    This function returns latitude and longitude of each bus
    format : {"bus name/number":(latitude, longitude)}
    example:    (
                    "555":(39.16641998291, -86.526893615723)
                )
    """
    dict_bus_lat_lng = {}
    doublemap_url = 'http://northwestern.doublemap.com/map/v2/buses'
    #"http://bloomington.doublemap.com/map/v2/buses"
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
        dict_bus_lat_lng[bus_number] = (dict_all_buses_lat_lng[bus_number][0], dict_all_buses_lat_lng[bus_number][1])
    return dict_bus_lat_lng

def get_bus_distance(colloquial_bus_numbers, target_location_coordinates):
    """
    This function returns a dictionary with status of each bus on each input route
    input_route_list can have one or a list of bus numbers. This will be used to get the route numbers. 
    For example, user might want yo travel by route 6 OR route 9. Then we feed both route numbers for route6 and 9 to this function.
    Output: Each bus running on the input route along with its latitude and longitude.
    """
    
    for bus in colloquial_bus_numbers:
        bus_number_list.extend(map_colloquial_to_acutal_bus_number[bus])

    #Query doublemap API and get status for each route
    dict_bus_lat_lng = get_coordinates_of_buses(bus_number_list)
    # use this dict to store distances
    dict_bus_distance = {}
    for bus, latLng in dict_bus_lat_lng.iteritems():
        dict_bus_distance[bus] = find_distance_between_coordinates(latLng, target_location_coordinates)
    return dict_bus_distance

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
    This function returns exact distance (and not the map/road driving distance)
    between bus_coordinates and target coordinates
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

def poll_on_distance(approaching_buses, target_location_coordinates):
    dict_bus_distance = get_bus_distance(approaching_buses, target_location_coordinates)
    for bus, distance in dict_bus_distance:
        if distance < 1:
            #ALERT user
            print "Bus ",bus," is approaching and is at distance: ", distance
            print "Move your ass now!"
            sys.exit(0)
        else:
            print "Bus", bus," is approaching and is at distance: ", distance

def get_all_bus_position(colloquial_bus_numbers, target_location_coordinates):
    dict_bus_lat_lng_instance1 = get_coordinates_of_buses(colloquial_bus_numbers)
    time.sleep(2)
    dict_bus_lat_lng_instance2 = get_coordinates_of_buses(colloquial_bus_numbers)

    # get all the approaching buses
    approaching_buses = []
    dict_bus_position = {}
    for bus, latLng in dict_bus_lat_lng_instance1.iteritems():

        dict_bus_position[bus] = is_bus_approaching_waiting_or_leaving_point(dict_bus_lat_lng_instance1[bus], \
            dict_bus_lat_lng_instance2[bus], target_location_coordinates)

        status = is_bus_approaching_waiting_or_leaving_point(dict_bus_lat_lng_instance1[bus], \
            dict_bus_lat_lng_instance2[bus], target_location_coordinates)
        if status[1] == APPROACHING:
            approaching_buses.append(bus)
    return dict_bus_position
    
if __name__ == "__main__":
    #test if the API is working
    if test_get_all_buses_status():
        print "Code accessing Doublemap API is working correctly"
    else:
        print "Something seems to be wrong with accessing code of Doublemap API"

    colloquial_bus_numbers = ['EL','CL']
    colloquial_bus_numbers = ['29727', '29732', '29729']
    #target_location_coordinates = (39.171539306641,-86.512619018555)
    target_location_coordinates = (42.0549051148951, -87.6870495230669)

    while True:
        print "Position: \n"
        dict_bus_position = get_all_bus_position(colloquial_bus_numbers, target_location_coordinates)

        pprint(dict_bus_position)
        print "\n----------------------------------------------------------------------"

        approaching_buses = ['EL', 'CL']

        time.sleep(4)
        dict_bus_distance = get_bus_distance(approaching_buses, target_location_coordinates)
        print "Distance: \n"
        pprint(dict_bus_distance)
        print '\n\n'

    sys.exit(0)

    #map_actual_to_colloquial_bus_number = {('553','555','554','551'): '6', ('9725','243'): '9'}

    '''
    #TODO: Code to optimize polling
    if(status[0] > 10):
        #poll after 8 minutes
    if(status[0] > 5)
        poll after 3 minutes
    '''

    #work on approaching buses to poll the distance
    while True:
        time.sleep(2)
        poll_on_distance(approaching_buses, target_location_coordinates)

    '''
    while True:
        time.sleep(5) # delays for 5 seconds
        #Find which bus is approaching
        dict_bus_status = get_bus_distance(colloquial_bus_numbers, target_location_coordinates)
        for bus in dict_bus_status.keys():
            if bus['status'][1] == APPROACHING:
                print "Bus ",bus," is approaching and is at distance: ",bus['status'][0]

    '''

