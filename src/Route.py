from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
from pprint import pprint
import time
import logging
from datetime import datetime

class Route:
    """
    Has a map of routes in the city: which buses are running, what are the stops on each route, path
    """
    DOUBLEMAP_CITY = ""
    DOUBLEMAP_ROUTES_API_URL=""
    DOUBLEMAP_BUSES_API_URL=""
    
    def __init__(self, constants, city):
        self.DOUBLEMAP_CITY = city
        self.DOUBLEMAP_ROUTES_API_URL = constants.DOUBLEMAP_ROUTES_API_URL[self.DOUBLEMAP_CITY]
        self.DOUBLEMAP_BUSES_API_URL = constants.DOUBLEMAP_BUSES_API_URL[self.DOUBLEMAP_CITY]

    #variables    
    map_actual_bus_numbers_to_colloquial_bus_numbers = {}
    map_colloquial_route_numbers_to_actual_route_numbers = {}

    # This procedure uses routes to find colloquial to actual bus numbers and so kept in Route class
    def get_colloquial_bus_numbers_from_actual_bus_numbers(self):
        """
        used to update MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS
        """
        #Fetch all buses data
        doublemap_buses_url = self.DOUBLEMAP_BUSES_API_URL  
        response_buses = json.loads(urllib.urlopen(doublemap_buses_url).read())
        #Fetch all routes data
        doublemap_routes_url = self.DOUBLEMAP_ROUTES_API_URL
        response_routes = json.loads(urllib.urlopen(doublemap_routes_url).read())
        dict_actual_bus_number_actual_route_number = {}
        for bus in response_buses:
            bus_number = bus['name']
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
                self.map_actual_bus_numbers_to_colloquial_bus_numbers[bus_number] = dict_actual_route_number_to_colloquial_route_number[route]
        logging.info("\nIn get_colloquial_bus_numbers_from_actual_bus_numbers: MAP_ACUTAL_TO_COLLOQUIAL_BUS_NUMBERS:"+str(self.map_actual_bus_numbers_to_colloquial_bus_numbers))
        return self.map_actual_bus_numbers_to_colloquial_bus_numbers


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
        doublemap_buses_url = self.DOUBLEMAP_BUSES_API_URL
        response = json.loads(urllib.urlopen(doublemap_buses_url).read())
        logging.info("\nIn find_actual_bus_numbers_for_actual_routes: response :"+str(response))
        if len(response) == 0:
            logging.warn("Something went wrong while getting status of each bus")
            sys.exit(0)
        for bus in response:
            bus_number = bus['name']
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
                DOUBLEMAP_CITY = "IUB"
            OUPUT:
                dict_colloquial_bus_numbers = {u'9': 1001555, u'3': 1001536, u'5': 1001543, u'6': 1001546}
        """
        doublemap_routes_url = self.DOUBLEMAP_ROUTES_API_URL
        response = json.loads(urllib.urlopen(doublemap_routes_url).read())
        set_colloquial_bus_numbers = set(colloquial_bus_numbers)
        dict_colloquial_bus_numbers = {} #This would store mapping of colloquial bus number to their actual route numbers
        for route in response:
            colloquial_route_name = route['name']
            #If the user is looking for buses on this particular route, fetch the actual route number 
            if colloquial_route_name in set_colloquial_bus_numbers:
                dict_colloquial_bus_numbers[colloquial_route_name] = route['id']
        logging.info("\nIn find_routes_for_colloquial_bus_numbers: dict_colloquial_bus_numbers :"+str(dict_colloquial_bus_numbers))
        return dict_colloquial_bus_numbers

    def get_all_buses(self):
        """
        Returns the list of colloquial_bus_numbers for the specified city/university.
        """
        doublemap_routes_url = self.DOUBLEMAP_ROUTES_API_URL
        response = json.loads(urllib.urlopen(doublemap_routes_url).read())

        busList = []
        for route in response:
            busList.append(route['name'])
        return busList

