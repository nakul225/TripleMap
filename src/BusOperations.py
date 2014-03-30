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
from constants import *

class BusOperations:
    DOUBLEMAP_CITY = ""
    DOUBLEMAP_ROUTES_API_URL=""
    DOUBLEMAP_BUSES_API_URL=""
    
    def __init__(self, constants, city):
        self.DOUBLEMAP_CITY = city
        self.DOUBLEMAP_ROUTES_API_URL = constants.DOUBLEMAP_ROUTES_API_URL[self.DOUBLEMAP_CITY]
        self.DOUBLEMAP_BUSES_API_URL = constants.DOUBLEMAP_BUSES_API_URL[self.DOUBLEMAP_CITY]

    """
    Has all operations to work with data related to buses and routes
    """   
    def updateBusStatus(self, listOfBusObjects):
        """
        This function updates all bus statuses
        """
        dict_bus_lat_lng = {}
        doublemap_buses_url = self.DOUBLEMAP_BUSES_API_URL
        response = json.loads(urllib.urlopen(doublemap_buses_url).read())
        logging.info("\nIn get_all_buses_status: response:"+str(response))
        if len(response) == 0:
            logging.warn("In get_all_buses_status: Something went wrong while getting status of each bus, exiting")
            sys.exit(0)
        
        for bus in listOfBusObjects:
            #Update status of each bus
            for eachBus in response:
                if int(bus.get_actual_number()) == int(eachBus['name']):
                    #Found our bus
                    #Save previous coordinates of the bus
                    busCurrentLatLng = bus.get_bus_current_lat_lng()
                    bus.set_previous_lat_lng(busCurrentLatLng)
                    #Save current coordinates of the bus
                    bus.set_bus_current_lat_lng((eachBus['lat'],eachBus['lon']) )
        
        return listOfBusObjects
    
