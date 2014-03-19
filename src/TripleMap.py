# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

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

DOUBLEMAP_BUSES_API_URL = {
                    "BLOOMINGTON_TRANSIT":"http://bloomington.doublemap.com/map/v2/buses",
                    "NORTHWESTERN":"http://northwestern.doublemap.com/map/v2/buses"
                    }
DOUBLEMAP_ROUTES_API_URL = {
                    "BLOOMINGTON_TRANSIT":"http://bloomington.doublemap.com/map/v2/routes",
                    "NORTHWESTERN":"http://northwestern.doublemap.com/map/v2/routes"
                    }
MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS = {}
ALERT_DISTANCE = 0.3

# <codecell>

#Map for colloquial bus number to route number
def create_colloquial_to_route():
    if type(colloquial_bus_numbers) is not list:
        print 'Invalid parameter for colloquial bus list!'
        return None
    else:
        dict_coll_to_route = dict.fromkeys(colloquial_bus_numbers, 0)

        dblmap_routes_uri = DOUBLEMAP_ROUTES_API_URL["BLOOMINGTON_TRANSIT"]
        routes = json.loads(urllib.urlopen(dblmap_routes_uri).read())
        #print (routes[0]['short_name'])

        for route in routes:
            dict_coll_to_route[route['short_name']] = route['id']
        return dict_coll_to_route

# <codecell>

# Mapping between route number to actual number
def create_route_to_actual():
    all_buses = get_all_buses_status()
    dict_route_to_actual = {}
    for bus in all_buses:
            dict_route_to_actual.setdefault(bus['route'], []).append(bus['id'])
    return dict_route_to_actual

# <codecell>

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

# <codecell>

def actual_to_colloquial(actual_bus_numbers):
    colloquial_bus_numbers = []


# ************This should probably go************
# Map to convert colloquial bus number to actual bus number
def loadMapFromFile(fileName):
    with open(fileName, "r") as jsFile:
        map_colloquial_to_acutal_bus_number = json.loads(jsFile.read())
        

# <codecell>

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
    #'http://northwestern.doublemap.com/map/v2/buses'
    doublemap_buses_url = DOUBLEMAP_BUSES_API_URL["NORTHWESTERN"] 
    
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

# <codecell>

def test_get_all_buses_status():
    """
    Test function
    """
    return len(get_all_buses_status())

# <codecell>

def get_coordinates_of_buses(bus_number_list):
    """
    def pulls out coordinates infromation for the bus numbers given as input
    """
    isLatLng = True
    dict_all_buses_lat_lng = get_all_buses_status(isLatLng)

    dict_bus_lat_lng = {}
    for bus_number in bus_number_list:
        if bus_number in dict_all_buses_lat_lng:
            dict_bus_lat_lng[bus_number] = (dict_all_buses_lat_lng[bus_number][0], dict_all_buses_lat_lng[bus_number][1])
    return dict_bus_lat_lng

# <codecell>

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

# <codecell>

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

# <codecell>

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

# <codecell>

def poll_on_distance(approaching_buses, target_location_coordinates):
    """
    This function checks if the distance between bus and target location is less than ALERT_DISTANCE,
    and alerts the user accordingly.
    """
    dict_bus_distance = get_bus_distance(approaching_buses, target_location_coordinates)
    
    for bus, distance in dict_bus_distance.iteritems():
        colloquial_bus_number = MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS[bus]
        if distance < ALERT_DISTANCE:
            # ALERT user
            print "Alert for bus ", colloquial_bus_number
            # remove the bus from list for which user has been alerted.
            approaching_buses.remove(bus)
        else:
            print "Bus", colloquial_bus_number," is approaching and is at distance: ", distance
    return approaching_buses

# <codecell>

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

# <codecell>

def get_colloquial_bus_numbers_from_actual_bus_numbers(DOUBLEMAP_CITY):
    """
    used to update MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS
    """
    #Fetch all buses data
    doublemap_buses_url = DOUBLEMAP_BUSES_API_URL[DOUBLEMAP_CITY] 
    response_buses = json.loads(urllib.urlopen(doublemap_buses_url).read())
    #Fetch all routes data
    doublemap_routes_url = DOUBLEMAP_ROUTES_API_URL[DOUBLEMAP_CITY]
    response_routes = json.loads(urllib.urlopen(doublemap_routes_url).read())

    dict_actual_bus_number_actual_route_number = {}
    for bus in response_buses:
        bus_number = bus['id']
        route = bus['route']
        dict_actual_bus_number_actual_route_number[bus_number] = route
    
    dict_actual_route_number_to_colloquial_route_number = {}
    for route in response_routes:
        actual_route_number = route['id']
        colloquial_route_name = route['short_name']
        dict_actual_route_number_to_colloquial_route_number[actual_route_number] = colloquial_route_name
        
    #For each route ID, find buses running on it and then update the map
    for bus_number in dict_actual_bus_number_actual_route_number.keys():
        route = dict_actual_bus_number_actual_route_number[bus_number]
        if route in dict_actual_route_number_to_colloquial_route_number:
            MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS[bus_number] = dict_actual_route_number_to_colloquial_route_number[route]
    return MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS

# <codecell>

def get_actual_bus_numbers(colloquial_bus_numbers, DOUBLEMAP_CITY):
    """
    This function takes in colloquial names for buses (routes) for example, route '6' or route '9' and returns lists
    of buses running on those routes. 
    For example, buses [234,545,5657,2324] might be running on '6' route.
    Since both route numbers and bus numbers change everyday, we use route names by calling 'ROUTES' API to find route numbers.
    Then we use 'BUSES' API to fetch all bus numbers running on those routes and return them.
    """
    #Task 1: Find actual route numbers on which the colloquial bus numbers are running
    dict_actual_route_numbers = find_routes_for_colloquial_bus_numbers(colloquial_bus_numbers, DOUBLEMAP_CITY)
    set_actual_route_numbers = set(dict_actual_route_numbers.values())
    print "set_actual_route_numbers: ",set_actual_route_numbers
    #Task 2: Find actual bus numbers running on the actual route numbers found in above step
    list_actual_bus_numbers = find_actual_bus_numbers_for_actual_routes(set_actual_route_numbers, DOUBLEMAP_CITY)
    
    return list_actual_bus_numbers
    

# <codecell>

def find_actual_bus_numbers_for_actual_routes(set_actual_route_numbers, DOUBLEMAP_CITY):
    """
    This function returns the actual bus numbers by using actual route numbers
    """
    list_actual_bus_numbers = []
    doublemap_buses_url = DOUBLEMAP_BUSES_API_URL[DOUBLEMAP_CITY] 
    
    response = json.loads(urllib.urlopen(doublemap_buses_url).read())
    if len(response) == 0:
        print "Something went wrong while getting status of each bus..."
        sys.exit(0)
    
    for bus in response:
        bus_number = bus['id']
        lat = bus['lat']
        lng = bus['lon']
        route = bus['route']
        bus_id = bus['id']
        lastUpdate = bus['lastUpdate']
        print route
        #If route number matches the one in dict_colloquial_bus_numbers, add that bus number to the list
        if route in set_actual_route_numbers:
            #Add this bus to the list
            list_actual_bus_numbers.append(bus_number)
    return list_actual_bus_numbers

# <codecell>

def find_routes_for_colloquial_bus_numbers(colloquial_bus_numbers, DOUBLEMAP_CITY):
    """
    Returns a dictionary with key as colloquial bus number and value as actual route numbers associated with it.
    Example:
        INPUT: 
            colloquial_bus_numbers = ['6','9','3','5']
            DOUBLEMAP_CITY = "BLOOMINGTON_TRANSIT"
        OUPUT:
            dict_colloquial_bus_numbers = {u'9': 1001555, u'3': 1001536, u'5': 1001543, u'6': 1001546}
    """
    doublemap_routes_url = DOUBLEMAP_ROUTES_API_URL[DOUBLEMAP_CITY]
    response = json.loads(urllib.urlopen(doublemap_routes_url).read())
    
    set_colloquial_bus_numbers = set(colloquial_bus_numbers)
    dict_colloquial_bus_numbers = {} #This would store mapping of colloquial bus number to their actual route numbers
    for route in response:
        colloquial_route_name = route['short_name']
        #If the user is looking for buses on this particular route, fetch the actual route number 
        if colloquial_route_name in set_colloquial_bus_numbers:
            dict_colloquial_bus_numbers[colloquial_route_name] = route['id']
                               
    return dict_colloquial_bus_numbers

# <codecell>

if __name__ == "__main__":
    #test if the API is working
    if test_get_all_buses_status():
        print "Code accessing Doublemap API is working correctly"
    else:
        print "Something seems to be wrong with accessing code of Doublemap API"
    DOUBLEMAP_CITY = "NORTHWESTERN"
    #colloquial_bus_numbers = ['6','9','3','5']
    #target_location_coordinates = (39.171539306641,-86.512619018555)

    colloquial_bus_numbers = ['EL','CL']
    #colloquial_bus_numbers = ['29727', '29732', '29729']
    #EVANSTON n/w university
    target_location_coordinates = (42.0549051148951, -87.6870495230669)
    
    
    get_colloquial_bus_numbers_from_actual_bus_numbers(DOUBLEMAP_CITY)
    bus_number_list = get_actual_bus_numbers(colloquial_bus_numbers,DOUBLEMAP_CITY)
    '''
    dict_colloquial_to_actual.values() is a list of lists (ex: [[29724, 29727], [29729]])
    Following operation flattens this list.
    '''
    print bus_number_list
    while True:
        time.sleep(2)
        bus_number_list = poll_on_distance(bus_number_list, target_location_coordinates)
        print "Distance: \n"
        if len(bus_number_list) == 0:
            print "No Bus Running"
            sys.exit(0)

    sys.exit(0)

# <codecell>

%tb

# <codecell>


# <codecell>


