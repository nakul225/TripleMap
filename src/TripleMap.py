from Bus import *
from Route import *
from constants import *
from BusOperations import *

class TripleMapClient:

    alertDistance = 0.3
    busList = []
    targetCoordinates = (39.17155659473131, -86.50890111923218)
    city = "IUB"
    #interface = Interface()

    def __init__(self, userRequest):
        if 'alertDistance' in userRequest:
            self.alertDistance = userRequest['alertDistance']
        if 'busList' in userRequest:
            self.busList = userRequest['busList']
        #if post data contains latitude it contains target co-ordinates
        if 'lat' in userRequest:
            self.targetCoordinates = (float(userRequest['lat']), float(userRequest['lng']))
        if 'city' in userRequest:
            self.city = userRequest['city']

        #TODO work on the direction of bus (would be specified by user)
        self.constantsObject = Constants()
        #TODO constants path :/ 
        self.constantsObject.load_constants("/Users/pushkarjoshi/constants.json")
        #Create bus operations object
        self.busOperationsObject = BusOperations(self.constantsObject, self.city)
        #Create route object
        self.routeObject = Route(self.constantsObject, self.city)

    def pollDistance(self):
        #get the actual bus objects from the user specified name list
        pprint(self.busList)
        print '-'*20
        listOfActualBusNumbers = self.routeObject.get_actual_bus_numbers(self.busList)
        print '-'*20
        pprint(listOfActualBusNumbers)
        #Create bus objects
        listOfBusObjects = [] #Stores list of all bus objects
        for actualNumber in listOfActualBusNumbers:
            busObject = Bus(self.constantsObject)
            busObject.set_actual_number(actualNumber)
            listOfBusObjects.append(busObject)
        #Create a map of actual to colloquial bus numbers
        map_actual_bus_numbers_to_colloquial_bus_numbers = self.routeObject.get_colloquial_bus_numbers_from_actual_bus_numbers()

        while True:
            time.sleep(2) #sleep for 2 second before updating status of each bus
            listOfBusObjects = self.busOperationsObject.updateBusStatus(listOfBusObjects)
            #check which buses are approaching, then track them or show them or whatever
            for bus in listOfBusObjects:
                status = bus.getBusMovementAgainstTarget(self.targetCoordinates)
                if status == self.constantsObject.APPROACHING:
                    status = "APPROACHING"
                elif status == self.constantsObject.LEAVING:
                    status = "LEAVING"
                else:
                    status = "STOPPED"
                currentDist = bus.getBusDistanceFromTarget(self.targetCoordinates)
                if currentDist <= 0.4:
                    #send notification & remove it from the list
                    #TODO sending notification to the client
                    listOfBusObjects.remove(bus)
                    yield bus.get_colloquial_number()
                print map_actual_bus_numbers_to_colloquial_bus_numbers[bus.get_actual_number()]," :",status, \
                " is at distance: ",bus.getBusDistanceFromTarget(self.targetCoordinates)," miles"



if __name__ == "__main__":

    #Input
    city = "IUB"
    #target location coordinates
    targetCoordinates = (39.17155659473131, -86.50890111923218)

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
    listColloquialBusNumbers = ['3 College Mall / Bradford Place','6 Limited','9 Limited']
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
        
        

