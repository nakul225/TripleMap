from GoogleMapsApiInterface import *
import json
import urllib
import sys
from math import sin, cos, sqrt, atan2, radians
from pprint import pprint
import time
import logging
from datetime import datetime

class Bus:
    APPROACHING = 0
    STOPPED = 0
    LEAVING = 0

    def __init__(self, constantsObject):
        self.APPROACHING = constantsObject.APPROACHING
        self.STOPPED = constantsObject.STOPPED
        self.LEAVING = constantsObject.LEAVING
        
    """
    Stores bus information
    """    
    lat_lng = (0,0)
    previous_lat_lng = (0,0)
    next_stop_lat_lng = (0,0)
    actual_number = 0
    colloquial_number = 0

    #function to update and retrieve coordinates of bus
    #getters
    def get_bus_current_lat_lng(self):
        return self.lat_lng
    def get_previous_lat_lng(self):
        return self.previous_lat_lng
    def get_next_lat_lng(self):
        return self.next_stop_lat_lng
    def get_actual_number(self):
        return self.actual_number
    def get_colloquial_number(self):
        return self.colloquial_number
   
    #setters
    def set_bus_current_lat_lng(self, lat_lng):
        self.lat_lng = lat_lng
    def set_previous_lat_lng(self, lat_lng):
        self.previous_lat_lng = lat_lng
    def set_next_lat_lng(self, lat_lng):
        self.next_stop_lat_lng = lat_lng
    def set_actual_number(self, lat_lng):
        self.actual_number = lat_lng
    def set_colloquial_number(self, lat_lng):
        self.colloquial_number = lat_lng
      
    #Geocodes distance
    def getBusMovementAgainstTarget(self, targetCoordinates):
        #Compare if the current coordinate of bus is less or greater than target
        #This gives us idea if the bus is moving towards or away from the target coordinates
        distanceBefore = self.__find_distance_between_coordinates( self.get_previous_lat_lng(), targetCoordinates)
        distanceAfter = self.__find_distance_between_coordinates( self.get_bus_current_lat_lng(), targetCoordinates)
        if distanceAfter > distanceBefore:
            return self.LEAVING
        elif distanceAfter < distanceBefore:
            return self.APPROACHING
        else:
            return self.STOPPED
    
    def getBusDistanceFromTarget(self, targetCoordinates):
        return self.__find_distance_between_coordinates( self.get_bus_current_lat_lng(), targetCoordinates)
    
    def __find_distance_between_coordinates(self, bus_coordinates, target_location_coordinates):
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
    
