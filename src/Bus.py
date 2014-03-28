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
    """
    Stores bus information
    """    
    lat_lng = (0,0)
    previous_stop_lat_lng = (0,0)
    next_stop_lat_lng = (0,0)
    actual_number = 0
    colloquial_number = 0
    
    #function to update and retrieve coordinates of bus
    #getters
    def get_bus_current_lat_lng():
        return self.lat_lng
    def get_previous_lat_lng():
        return self.previous_stop_lat_lng
    def get_next_lat_lng():
        return self.next_stop_lat_lng
    def get_actual_number():
        return self.actual_number
    def get_colloquial_number():
        return self.colloquial_number
   
    #setters
    def set_bus_current_lat_lng(lat_lng):
        self.lat_lng = lat_lng
    def set_previous_lat_lng(lat_lng):
        self.previous_stop_lat_lng = lat_lng
    def set_next_lat_lng(lat_lng):
        self.next_stop_lat_lng = lat_lng
    def set_actual_number(lat_lng):
        self.actual_number = lat_lng
    def set_colloquial_number(lat_lng):
        self.colloquial_number = lat_lng

