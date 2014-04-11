from Bus import *
from Route import *
from constants import *
from BusOperations import *


if __name__ == "__main__":

    #Input
    city = "IUB"
    #Buses whose coordinates 
    listColloquialBusNumbers = ['3 College Mall / Bradford Place','6 Campus Shuttle','9 Limited']
    #target location coordinates
    targetCoordinates = (39.17149421257152, -86.50918006896973)

    #Create constans object to fetch all constant values
    constantsObject = Constants()
    constantsObject.load_constants("constants.json")
    #Create bus operations object
    busOperationsObject = BusOperations(constantsObject, city)
    #Create route object
    routeObject = Route(constantsObject, city)
    #Create a map of actual to colloquial bus numbers
    map_actual_bus_numbers_to_colloquial_bus_numbers = routeObject.get_colloquial_bus_numbers_from_actual_bus_numbers()
    print "-"*50
    print map_actual_bus_numbers_to_colloquial_bus_numbers 
    print '-'*50
    
    #Make a list of bus objects
    listOfActualBusNumbers = routeObject.get_actual_bus_numbers(listColloquialBusNumbers)
    print "Colloquial no:",listColloquialBusNumbers
    print "Actual nos:",listOfActualBusNumbers
    #Create bus objects
    listOfBusObjects = [] #Stores list of all bus objects
    for actualNumber in listOfActualBusNumbers:
        busObject = Bus(constantsObject)
        busObject.set_actual_number(actualNumber)
        listOfBusObjects.append(busObject)
    
    while True:
        time.sleep(2) #sleep for 2 second before updating status of each bus
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
            print map_actual_bus_numbers_to_colloquial_bus_numbers[bus.get_actual_number()]," :",status, " is at distance: ",bus.getBusDistanceFromTarget(targetCoordinates)," miles"
        
        

