# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

#This code will keep a track of locations of each bus
from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
from pprint import pprint
import time
import logging
from datetime import datetime
from Bus import *
from Route import *
from BusOperations import *

DOUBLEMAP_BUSES_API_URL = {
                    "BLOOMINGTON_TRANSIT":"http://bloomington.doublemap.com/map/v2/buses",
                    "NORTHWESTERN":"http://northwestern.doublemap.com/map/v2/buses"
                    }
DOUBLEMAP_ROUTES_API_URL = {
                    "BLOOMINGTON_TRANSIT":"http://bloomington.doublemap.com/map/v2/routes",
                    "NORTHWESTERN":"http://northwestern.doublemap.com/map/v2/routes"
                    }

class BusOperations:
    STOPPED = 0
    APPROACHING = 1
    LEAVING = 2
    ALERT_DISTANCE = 0.3
    MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS = {}
    MAP_COLLOQUIAL_TO_ROUTE = {}
    
    #Map for colloquial route number to actual route number
    def create_colloquial_to_route(self):
        dict_coll_to_route = {}

        dblmap_routes_uri = DOUBLEMAP_ROUTES_API_URL[self.DOUBLEMAP_CITY]
        routes = json.loads(urllib.urlopen(dblmap_routes_uri).read())
        logging.info("\nIn create_colloquial_to_route: routes:"+str(routes))
        for route in routes:
            dict_coll_to_route[route['short_name']] = route['id']
        return dict_coll_to_route

    # Mapping between route number to actual number
    def create_route_to_actual(self):
        all_buses = self.get_all_buses_status()
        dict_route_to_actual = {}
        logging.info("\nIn create_route_to_actual: all_buses:"+str(all_buses))
        for bus in all_buses:
                dict_route_to_actual.setdefault(bus['route'], []).append(bus['id'])
        logging.info("In create_route_to_actual: dict_route_to_actual:"+str(dict_route_to_actual))
        return dict_route_to_actual

    def colloquial_to_actual(self,colloquial_bus_numbers):
        """
        The route numbers and actual bus numbers change daily from Transport service provider. 
        This function creates a map of colloquial numbers to route number and then gets the actual bus numbers on these routes
        Returns a dict of colloquial_bus_numbers to actual_bus_numbers {'EL': [29724, 29727]}
        """
        dict_colloquial_to_actual = {}
        bus_number_list = []
        route_list = []
        
        #map_colloquial_to_route = self.create_colloquial_to_route(colloquial_bus_numbers) #Created a global variable since this function needs to be called only once as data doesn't change every hour
        map_route_to_actual = self.create_route_to_actual()
        logging.info("In colloquial_to_actual: map_route_to_actual:"+str(map_route_to_actual))
        logging.info("In colloquial_to_actual: colloquial_bus_numbers:"+str(colloquial_bus_numbers))
        for colloquial_bus in colloquial_bus_numbers:
            dict_colloquial_to_actual[colloquial_bus] = map_route_to_actual[self.MAP_COLLOQUIAL_TO_ROUTE[colloquial_bus]]
        logging.info("In colloquial_to_actual: dict_colloquial_to_actual:"+str(dict_colloquial_to_actual))
        return dict_colloquial_to_actual

    def get_all_buses_status(self, isLatLng = None):
        """
        This function returns latitude and longitude of each bus
        format : {"bus name/number":(latitude, longitude)}
        example:    (
                        "555":(39.16641998291, -86.526893615723)
                    )
        """
        dict_bus_lat_lng = {}
        doublemap_buses_url = DOUBLEMAP_BUSES_API_URL[self.DOUBLEMAP_CITY] 
        response = json.loads(urllib.urlopen(doublemap_buses_url).read())
        logging.info("\nIn get_all_buses_status: response:"+str(response))
        if len(response) == 0:
            logging.warn("In get_all_buses_status: Something went wrong while getting status of each bus, exiting")
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
        logging.info("In get_all_buses_status: dict_bus_lat_lng:"+str(dict_bus_lat_lng))
        return dict_bus_lat_lng

    def test_get_all_buses_status(self):
        """
        Test function
        """
        return len(self.get_all_buses_status())

    def get_coordinates_of_buses(self, bus_number_list):
        """
        def pulls out coordinates infromation for the bus numbers given as input
        """
        isLatLng = True
        dict_all_buses_lat_lng = self.get_all_buses_status(isLatLng)
        dict_bus_lat_lng = {}
        actual_bus_number_list = self.colloquial_to_actual(bus_number_list).values()
        logging.info("\nIn get_coordinates_of_buses: actual_bus_number_list:"+str(actual_bus_number_list))
        #print "dict_all_buses_lat_lng: ",dict_all_buses_lat_lng
        #print "actual_bus_number_list: ",actual_bus_number_list
        for actual_bus_numbers_per_colloquial_bus_number in actual_bus_number_list:
            for bus_number in  actual_bus_numbers_per_colloquial_bus_number:
                #print "bus_number: ",bus_number
                if bus_number in dict_all_buses_lat_lng:
                    dict_bus_lat_lng[bus_number] = (dict_all_buses_lat_lng[bus_number][0], dict_all_buses_lat_lng[bus_number][1])
        logging.info("In get_coordinates_of_buses: dict_bus_lat_lng:"+str(dict_bus_lat_lng))
        return dict_bus_lat_lng

    def get_bus_distance(self, bus_number_list, target_location_coordinates):
        """
        This function returns a dictionary with status of each bus on each input route
        input_route_list can have one or a list of bus numbers. This will be used to get the route numbers. 
        For example, user might want yo travel by route 6 OR route 9. Then we feed both actual bus numbers for route6 and 9 to this function.
        Output: Each bus running on the input route along with its latitude and longitude.
        """
        #Query doublemap API and get status for each route
        dict_bus_lat_lng = self.get_coordinates_of_buses(bus_number_list)
        # use this dict to store distances
        dict_bus_distance = {}
        for bus, latLng in dict_bus_lat_lng.iteritems():
            dict_bus_distance[bus] = self.find_distance_between_coordinates(latLng, target_location_coordinates)
        logging.info("\nIn get_bus_distance: dict_bus_distance:"+str(dict_bus_distance))
        return dict_bus_distance

    def is_bus_approaching_waiting_or_leaving_point(self, bus_coordinates_before, bus_coordinates_later, target_location_coordinates):
        """
        Find if the bus is approaching a given location or not.
        bus_coordinates_before : coordinates of bus at time T
        bus_coordinates_later : coordinates of bus at time T+t where t!=0
        """
        #find difference between distance_before and distance_later
        distance_before = self.find_distance_between_coordinates(bus_coordinates_before, target_location_coordinates)
        distance_later = self.find_distance_between_coordinates(bus_coordinates_later, target_location_coordinates)
        distance = distance_before - distance_later
        logging.info("\nIn is_bus_approaching_waiting_or_leaving_point: distance:"+str(distance))
        if distance == 0:
            return (distance, self.STOPPED)
        elif distance > 0:
            return (distance, self.APPROACHING)
        else:
            return (distance, self.LEAVING)

    def find_distance_between_coordinates(self, bus_coordinates, target_location_coordinates):
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
        logging.info("\nIn find_distance_between_coordinates: distance:"+str(distance))
        return distance

    def poll_on_distance(self, colloquialBusNumbersList, target_location_coordinates):
        """
        This function checks if the distance between bus and target location is less than ALERT_DISTANCE,
        and alerts the user accordingly.
        """
        dict_bus_distance = self.get_bus_distance(colloquialBusNumbersList, target_location_coordinates)
        logging.info("\nIn poll_on_distance: dict_bus_distance:"+str(dict_bus_distance))
        approaching_buses = [] #return list of buses that are approaching
        for bus, distance in dict_bus_distance.iteritems():
            colloquial_bus_number = self.MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS[bus]
            #print "bus: ",colloquial_bus_number
            #print "self.ALERT_DISTANCE: ",self.ALERT_DISTANCE
            #print "distance: ",distance
            
            if distance < self.ALERT_DISTANCE:
                # ALERT user
                logging.info("In poll_on_distance: Alert for bus: colloquial_bus_number:"+str(colloquial_bus_number))
                print "Alert for bus ", colloquial_bus_number,
                # remove the bus from list for which user has been alerted.
                approaching_buses.append(bus)
            else:
                bus_distance_string= "Bus "+str(colloquial_bus_number)+" is approaching and is at distance: "+ str(distance)
                logging.info("In poll_on_distance: Alert for bus: colloquial_bus_number:"+bus_distance_string)
                print bus_distance_string
        logging.info("In poll_on_distance: approaching_buses:"+str(approaching_buses))
        #print approaching_buses
        return approaching_buses


    def get_colloquial_bus_numbers_from_actual_bus_numbers(self):
        """
        used to update MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS
        """
        #Fetch all buses data
        doublemap_buses_url = DOUBLEMAP_BUSES_API_URL[self.DOUBLEMAP_CITY] 
        response_buses = json.loads(urllib.urlopen(doublemap_buses_url).read())
        #Fetch all routes data
        doublemap_routes_url = DOUBLEMAP_ROUTES_API_URL[self.DOUBLEMAP_CITY]
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
                self.MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS[bus_number] = dict_actual_route_number_to_colloquial_route_number[route]
        logging.info("\nIn get_colloquial_bus_numbers_from_actual_bus_numbers: MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS:"+str(self.MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS))
        return self.MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS

    def get_actual_bus_numbers(self, colloquial_bus_numbers):
        """
        This function takes in colloquial names for buses (routes) for example, route '6' or route '9' and returns lists
        of buses running on those routes. 
        For example, buses [234,545,5657,2324] might be running on '6' route.
        Since both route numbers and bus numbers change everyday, we use route names by calling 'ROUTES' API to find route numbers.
        Then we use 'BUSES' API to fetch all bus numbers running on those routes and return them.
        """
        #Task 1: Find actual route numbers on which the colloquial bus numbers are running
        dict_actual_route_numbers = self.find_routes_for_colloquial_bus_numbers(colloquial_bus_numbers)
        set_actual_route_numbers = set(dict_actual_route_numbers.values())
        #Task 2: Find actual bus numbers running on the actual route numbers found in above step
        list_actual_bus_numbers = self.find_actual_bus_numbers_for_actual_routes(set_actual_route_numbers)
        logging.info("\nIn get_actual_bus_numbers: set_actual_route_numbers:"+str(set_actual_route_numbers))
        logging.info("In get_actual_bus_numbers: list_actual_bus_numbers :"+str(list_actual_bus_numbers ))
        return list_actual_bus_numbers

    def find_actual_bus_numbers_for_actual_routes(self, set_actual_route_numbers):
        """
        This function returns the actual bus numbers by using actual route numbers
        """
        list_actual_bus_numbers = []
        doublemap_buses_url = DOUBLEMAP_BUSES_API_URL[self.DOUBLEMAP_CITY] 
        response = json.loads(urllib.urlopen(doublemap_buses_url).read())
        logging.info("\nIn find_actual_bus_numbers_for_actual_routes: response :"+str(response))
        if len(response) == 0:
            logging.warn("Something went wrong while getting status of each bus")
            sys.exit(0)
        for bus in response:
            bus_number = bus['id']
            lat = bus['lat']
            lng = bus['lon']
            route = bus['route']
            bus_id = bus['id']
            lastUpdate = bus['lastUpdate']
            #If route number matches the one in dict_colloquial_bus_numbers, add that bus number to the list
            if route in set_actual_route_numbers:
                #Add this bus to the list
                list_actual_bus_numbers.append(bus_number)
        logging.info("In find_actual_bus_numbers_for_actual_routes: list_actual_bus_numbers :"+str(list_actual_bus_numbers ))
        return list_actual_bus_numbers

    def find_routes_for_colloquial_bus_numbers(self, colloquial_bus_numbers):
        """
        Returns a dictionary with key as colloquial bus number and value as actual route numbers associated with it.
        Example:
            INPUT: 
                colloquial_bus_numbers = ['6','9','3','5']
                DOUBLEMAP_CITY = "BLOOMINGTON_TRANSIT"
            OUPUT:
                dict_colloquial_bus_numbers = {u'9': 1001555, u'3': 1001536, u'5': 1001543, u'6': 1001546}
        """
        doublemap_routes_url = DOUBLEMAP_ROUTES_API_URL[self.DOUBLEMAP_CITY]
        response = json.loads(urllib.urlopen(doublemap_routes_url).read())
        set_colloquial_bus_numbers = set(colloquial_bus_numbers)
        dict_colloquial_bus_numbers = {} #This would store mapping of colloquial bus number to their actual route numbers
        for route in response:
            colloquial_route_name = route['short_name']
            #If the user is looking for buses on this particular route, fetch the actual route number 
            if colloquial_route_name in set_colloquial_bus_numbers:
                dict_colloquial_bus_numbers[colloquial_route_name] = route['id']
        logging.info("\nIn find_routes_for_colloquial_bus_numbers: dict_colloquial_bus_numbers :"+str(dict_colloquial_bus_numbers))
        return dict_colloquial_bus_numbers
####    
    def __init__(self, doublemapCity, alertDistance):
        """
        constructor
        """
        self.DOUBLEMAP_CITY = doublemapCity
        self.ALERT_DISTANCE = alertDistance
        #Create map of colloquial bus numbers to actual bus numbers
        self.get_colloquial_bus_numbers_from_actual_bus_numbers()
        self.MAP_COLLOQUIAL_TO_ROUTE = self.create_colloquial_to_route()
        logging.info("\nIn constructor: parameters: DOUBLEMAP_CITY :"+doublemapCity+" ALERT_DISTANCE:"+str(alertDistance))
        logging.info("\nIn colloquial_to_actual: map_colloquial_to_route:"+str(self.MAP_COLLOQUIAL_TO_ROUTE))
        
def run(doublemapCityName, alertDistance, colloquialBusNumbersList, targetLocationCoordinates, enableLoggingFlag=False):
    """
    The function that takes input from user interface and calls above functions to get bus status and send alerts.
    Actually, have write this function in the flask application
    """
    #Enable logging
    if enableLoggingFlag:
        logging.basicConfig(filename=datetime.now().strftime('logfile_%H_%M_%d_%m_%Y.log'),level=logging.DEBUG)
    #test if the API is working
    busOperationsObj = BusOperations(doublemapCityName, alertDistance)
    if busOperationsObj.test_get_all_buses_status():
        logging.info("\nCode accessing Doublemap API is working correctly")
    else:
        logging.warn("\nSomething seems to be wrong with accessing code of Doublemap API")
    bus_number_list = busOperationsObj.get_actual_bus_numbers(colloquialBusNumbersList)
    logging.info("Input buses list by user:"+str(colloquialBusNumbersList))
    
    #Have this while loop in the flask application 
    while True:
        time.sleep(2)
        bus_number_list = busOperationsObj.poll_on_distance(colloquialBusNumbersList, targetLocationCoordinates)
        
        
        if len(bus_number_list) == 0:
            print "No Bus Running"
            logging.warn("None of the input buses are running, exiting")
            sys.exit(0)
        
        logging.info("************************************************************************")
    sys.exit(0)
####################################################################################################################################################################3
class TripleMap:
    """
    This class makes use of all data providing classes and puts up the show together.
    """
    STOPPED = 0
    APPROACHING = 1
    LEAVING = 2
    ALERT_DISTANCE = 0.3
    
    listOfBuses = [] #stores all bus objects that contain information about each bus
    
    def getlistOfBuses(self):
        return self.listOfBuses
        
    def __init__(self, routeObject, constantsObject, busOperationsObject, doublemapCity, alertDistance):
        self.DOUBLEMAP_CITY = doublemapCity
        self.ALERT_DISTANCE = alertDistance
        
        #Create map of colloquial bus numbers to actual bus numbers
        self.get_colloquial_bus_numbers_from_actual_bus_numbers()
        self.MAP_COLLOQUIAL_TO_ROUTE = self.create_colloquial_to_route()
        
        
        
        logging.info("\nIn constructor: parameters: DOUBLEMAP_CITY :"+doublemapCity+" ALERT_DISTANCE:"+str(alertDistance))
        logging.info("\nIn colloquial_to_actual: map_colloquial_to_route:"+str(self.MAP_COLLOQUIAL_TO_ROUTE))
        
    
#####################################################################################################################################################################3
if __name__ == "__main__":
    """
    call run()
    """
    #run("NORTHWESTERN",0.3,['CL','EL'],(42.0549051148951, -87.6870495230669))
    #run("BLOOMINGTON_TRANSIT",0.3,['6L','6'],(39.17155659473131, -86.50890111923218),False)
    
    doublemapCity = "BLOOMINGTON_TRANSIT"
    alertDistance = 0.1
    userColloquialBusList = ['6L','6']
    targetCoordinates = (39.17155659473131, -86.50890111923218)
    routeObj = Route()
    constantsObj = Constants()
    busOperationsObj = BusOperations()
    tripleMapObj = TripleMap(routeObj, constantsObj, busOperationsObj, doublemapCity, alertDistance)
    
    #First initiate all buses with bus objects
    actualBusNumbersList = busOperationsObj.convert_colloquial_bus_number_to_actual_bus_number( userColloquialBusList )
    for actualBusNumber in actualBusNumbersList:
        bus = Bus()
        bus.colloquial_number = colloquialBusNumber
        tripleMapObj.listOfBuses.append(bus)
    
    while(True):
        #get current coordinates of each bus
        dictActualBusNumberToCoordinatesLatLng = busOperationsObj.get_coordinates_of_buses( tripleMapObj.getlistOfBuses() )
        #update each buses status
        for eachBus in tripleMapObj.listOfBuses
            
