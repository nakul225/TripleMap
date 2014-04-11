#!/usr/bin/env python

import gevent
import gevent.monkey
from Bus import *
from Route import *
from constants import *
from BusOperations import *
from gevent.pywsgi import WSGIServer
gevent.monkey.patch_all()

from flask import Flask, request, Response, render_template
const = Constants()
const.load_constants("../src/constants.json")

app = Flask(__name__)

def event_stream():
    count = 0
    city = "IUB"
    #Buses whose coordinates 
    listColloquialBusNumbers = ['3 College Mall / Bradford Place','6 Campus Shuttle','9 Limited']
    #target location coordinates
    targetCoordinates = (39.17149421257152, -86.50918006896973)
    alertDistance = 2.2

    #Create constans object to fetch all constant values
    constantsObject = Constants()
    constantsObject.load_constants("constants.json")
    #Create bus operations object
    busOperationsObject = BusOperations(constantsObject, city)
    #Create route object
    routeObject = Route(constantsObject, city)
    #Create a map of actual to colloquial bus numbers
    map_actual_bus_numbers_to_colloquial_bus_numbers = routeObject.get_colloquial_bus_numbers_from_actual_bus_numbers()
    #Make a list of bus objects
    listOfActualBusNumbers = routeObject.get_actual_bus_numbers(listColloquialBusNumbers)
    #Create bus objects
    listOfBusObjects = [] #Stores list of all bus objects
    for actualNumber in listOfActualBusNumbers:
        busObject = Bus(constantsObject)
        busObject.set_actual_number(actualNumber)
        listOfBusObjects.append(busObject)
    flag = True
    while flag:
        gevent.sleep(2)
        #time.sleep(2) #sleep for 2 second before updating status of each bus
        listOfBusObjects = busOperationsObject.updateBusStatus(listOfBusObjects)
        #check which buses are approaching, then track them or show them or whatever
        for bus in listOfBusObjects:
            status = bus.getBusMovementAgainstTarget(targetCoordinates)
            if status == constantsObject.APPROACHING:
                status = "APPROACHING"
            elif status == constantsObject.LEAVING:
                status = "LEAVING"
            else:
                status = "STOPPED"
            data = map_actual_bus_numbers_to_colloquial_bus_numbers[bus.get_actual_number()]," :",status, " is at distance: ",str(bus.getBusDistanceFromTarget(targetCoordinates))," miles"
            #print " ".join(data)
            gevent.sleep(2)
            if status == "APPROACHING" and  bus.getBusDistanceFromTarget(targetCoordinates) <= alertDistance:
                data = "ALERT, bus: ",map_actual_bus_numbers_to_colloquial_bus_numbers[bus.get_actual_number()],"is near"
            yield 'data: %s\n\n' % " ".join(data)
    
@app.route('/my_event_source')
def sse_request():
    return Response(
            event_stream(),
            mimetype='text/event-stream')

@app.route('/')
def page():
    cities = const.COORDINATES
    mapUrl = const.DOUBLEMAP_BUSES_API_URL
    return render_template('mapTest.html', cities=cities, mapUrl = mapUrl)

if __name__ == '__main__':
    http_server = WSGIServer(('127.0.0.1', 8001), app)
    http_server.serve_forever()
