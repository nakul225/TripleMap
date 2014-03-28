from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
from pprint import pprint
import time
import logging
from datetime import datetime

class BusOperations:
    """
    Has all operations to work with data related to buses and routes
    """   
    def get_all_buses_status(self):
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

    def get_coordinates_of_buses(self, actual_bus_number_list):
    """
    def pulls out coordinates information for the actual_bus_number_list given as input
    """
    dict_all_buses_lat_lng = self.get_all_buses_status()
    dict_bus_lat_lng = {}
    #actual_bus_number_list = self.convert_colloquial_bus_number_to_actual_bus_number(bus_number_list).values()
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

    def convert_colloquial_bus_number_to_actual_bus_number(self,colloquial_bus_numbers):
        """
        The route numbers and actual bus numbers change daily from Transport service provider. 
        This function creates a map of colloquial numbers to route number and then gets the actual bus numbers on these routes
        Returns a dict of colloquial_bus_numbers to actual_bus_numbers {'EL': [29724, 29727]}
        """
        dict_colloquial_bus_number_to_actual_bus_number = {}
        bus_number_list = []
        route_list = []
        
        #map_colloquial_to_route = self.create_colloquial_to_route(colloquial_bus_numbers) #Created a global variable since this function needs to be called only once as data doesn't change every hour
        map_route_to_actual = self.create_route_to_actual()
        logging.info("In convert_colloquial_bus_number_to_actual_bus_number: map_route_to_actual:"+str(map_route_to_actual))
        logging.info("In convert_colloquial_bus_number_to_actual_bus_number: colloquial_bus_numbers:"+str(colloquial_bus_numbers))
        for colloquial_bus in colloquial_bus_numbers:
            dict_colloquial_bus_number_to_actual_bus_number[colloquial_bus] = map_route_to_actual[self.MAP_COLLOQUIAL_TO_ROUTE[colloquial_bus]]
        logging.info("In convert_colloquial_bus_number_to_actual_bus_number: dict_colloquial_bus_number_to_actual_bus_number:"+str(dict_colloquial_bus_number_to_actual_bus_number))
        return dict_colloquial_bus_number_to_actual_bus_number

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

class Geocodes:
    """
    This class deals with stuff to do with geocodes 
    """    
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

class TestBusOperations:
    def test_get_all_buses_status(self):
        """
        Test function
        """
        return len(self.get_all_buses_status())


