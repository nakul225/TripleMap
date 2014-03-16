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

ALERT_DISTANCE = 0.3

#Map for colloquial bus number to route number
def create_colloquial_to_route():
    if type(colloquial_bus_numbers) is not list:
        print 'Invalid parameter for colloquial bus list!'
        return None
    else:
        dict_coll_to_route = dict.fromkeys(colloquial_bus_numbers, 0)

        dblmap_routes_uri = "http://northwestern.doublemap.com/map/v2/routes"
        routes = json.loads(urllib.urlopen(dblmap_routes_uri).read())
        #print (routes[0]['short_name'])

        for route in routes:
            dict_coll_to_route[route['short_name']] = route['id']
        return dict_coll_to_route

# Mapping between route number to actual number
def create_route_to_actual():
    all_buses = get_all_buses_status()
    dict_route_to_actual = {}
    for bus in all_buses:
            dict_route_to_actual.setdefault(bus['route'], []).append(bus['id'])
    return dict_route_to_actual


def colloquial_to_actual(colloquial_bus_numbers):
    """
    The route numbers and actual bus numbers change daily from Transport service provider. 
    This function creates a map of colloquial numbers to route number and then gets the actual bus numbers on these routes
    Returns a dict of colloquial_bus_numbers to actual_bus_numbers {'EL': [29724, 29727]}
    """
    dict_colloquial_to_actual = {}
    bus_number_list = []
    route_list = []

    map_colloquial_to_route = create_colloquial_to_route()
    map_route_to_actual = create_route_to_actual()

    for colloquial_bus in colloquial_bus_numbers:
        dict_colloquial_to_actual[colloquial_bus] = map_route_to_actual[map_colloquial_to_route[colloquial_bus]]

    return dict_colloquial_to_actual

def actual_to_colloquial(actual_bus_numbers):
    colloquial_bus_numbers = []


# ************This should probably go************
# Map to convert colloquial bus number to actual bus number
def loadMapFromFile(fileName):
    with open(fileName, "r") as jsFile:
        map_colloquial_to_acutal_bus_number = json.loads(jsFile.read())
        


def get_all_buses_status(isLatLng = None):
    """
    This function returns latitude and longitude of each bus
    format : {"bus name/number":(latitude, longitude)}
    example:    (
                    "555":(39.16641998291, -86.526893615723)
                )
    """
    dict_bus_lat_lng = {}
    #doublemap_buses_url = "http://bloomington.doublemap.com/map/v2/buses"
    doublemap_buses_url = 'http://northwestern.doublemap.com/map/v2/buses'
    
    response = json.loads(urllib.urlopen(doublemap_buses_url).read())
    if len(response) == 0:
        print "Something went wrong while getting status of each bus..."
        sys.exit(0)

    if not isLatLng:
        return response

    for bus in response:
        bus_number = bus['id']
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
    isLatLng = True
    dict_all_buses_lat_lng = get_all_buses_status(isLatLng)

    dict_bus_lat_lng = {}
    for bus_number in bus_number_list:
        dict_bus_lat_lng[bus_number] = (dict_all_buses_lat_lng[bus_number][0], dict_all_buses_lat_lng[bus_number][1])
    return dict_bus_lat_lng

def get_bus_distance(bus_number_list, target_location_coordinates):
    """
    This function returns a dictionary with status of each bus on each input route
    input_route_list can have one or a list of bus numbers. This will be used to get the route numbers. 
    For example, user might want yo travel by route 6 OR route 9. Then we feed both actual bus numbers for route6 and 9 to this function.
    Output: Each bus running on the input route along with its latitude and longitude.
    """
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
    """
    This function checks if the distance between bus and target location is less than ALERT_DISTANCE,
    and alerts the user accordingly.
    """
    dict_bus_distance = get_bus_distance(approaching_buses, target_location_coordinates)
    
    for bus, distance in dict_bus_distance.iteritems():
        if distance < ALERT_DISTANCE:
            # ALERT user
            print "Alert for bus ", bus
            # remove the bus from list for which user has been alerted.
            approaching_buses.remove(bus)
        else:
            print "Bus", bus," is approaching and is at distance: ", distance
    return approaching_buses

def get_all_bus_position(bus_number_list, target_location_coordinates):
    dict_bus_lat_lng_instance1 = get_coordinates_of_buses(bus_number_list)
    time.sleep(2)
    dict_bus_lat_lng_instance2 = get_coordinates_of_buses(bus_number_list)

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
    '''
    colloquial_bus_numbers = ['6','9']
    target_location_coordinates = (39.171539306641,-86.512619018555)
    '''
    colloquial_bus_numbers = ['EL','CL']
    #colloquial_bus_numbers = ['29727', '29732', '29729']
    #EVANSTON n/w university
    target_location_coordinates = (42.0549051148951, -87.6870495230669)
    
    
    dict_colloquial_to_actual = colloquial_to_actual(colloquial_bus_numbers)
    '''
    dict_colloquial_to_actual.values() is a list of lists (ex: [[29724, 29727], [29729]])
    Following operation flattens this list.
    '''
    bus_number_list = sum(dict_colloquial_to_actual.values(), [])

    while True:
        
        time.sleep(4)
        bus_number_list = poll_on_distance(bus_number_list, target_location_coordinates)
        print "Distance: \n"
        if len(bus_number_list) == 0:
            sys.exit(0)

    sys.exit(0)

    '''
    #TODO: Code to optimize polling
    if(status[0] > 10):
        #poll after 8 minutes
    if(status[0] > 5)
        poll after 3 minutes
    '''

