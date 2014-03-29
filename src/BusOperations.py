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
DOUBLEMAP_BUSES_API_URL = 'http://bloomington.doublemap.com/map/v2/buses'
DOUBLEMAP_CITY = "BLOOMINGTON_TRANSIT"

class BusOperations:
    """
    Has all operations to work with data related to buses and routes
    """   
    def updateBusStatus(self, listOfBusObjects):
        """
        This function updates all bus statuses
        """
        dict_bus_lat_lng = {}
        doublemap_buses_url = DOUBLEMAP_BUSES_API_URL
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
    
if __name__ == "__main__":
    #Create bus operations object
    busOperationsObject = BusOperations()
    #Create route object
    routeObject = Route()
    #Make a list of bus objects
    listColloquialBusNumbers = ['6','9','3']
    listOfActualBusNumbers = routeObject.get_actual_bus_numbers(listColloquialBusNumbers)
    print "Colloquial no:",listColloquialBusNumbers
    print "Actual nos:",listOfActualBusNumbers
    #Create bus objects
    listOfBusObjects = [] #Stores list of all bus objects
    for actualNumber in listOfActualBusNumbers:
        busObject = Bus()
        busObject.set_actual_number(actualNumber)
        listOfBusObjects.append(busObject)
    
    #target location coordinates
    targetCoordinates = (39.17155659473131, -86.50890111923218)
    
    while True:
        time.sleep(2) #sleep for 2 second before updating status of each bus
        listOfBusObjects = busOperationsObject.updateBusStatus(listOfBusObjects)
        #check which buses are approaching, then track them or show them or whatever
        for bus in listOfBusObjects:
            print bus.get_actual_number()," :",bus.busMovementAgainstTarget(targetCoordinates)
        
        

