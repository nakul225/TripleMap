#This code will keep a track of locations of each bus
from GoogleMapsApiInterface import *
import json
import urllib
import sys

map_colloquial_bus_number_to_route =    {
                                                    '1 S.Walnut':'1001529',
                                                    '1 Fee Lane':'1001531',
                                                    '2 S.Rogers':'1001527',
                                                    '3 Curry Pike':'1001537',
                                                    '3 College Mall':'1001536',
                                                    '4 High Street':'1001541',
                                                    '4 Bloomfield':'1001539',
                                                    '5':'1001543',
                                                    '6':'1001545',
                                                    '9':'1001561',
                                                    'A':'2000316',
                                                    'B':'2000318',
                                                    'D':'2000319',
                                                    'E':'2000320'
                                                }

def get_all_buses_status():
    """
    This function returns latitude and longitude of each bus
    format : {"bus name/number":(latitude, longitude)}
    example:    (
                    "555":(39.16641998291, -86.526893615723)
                )
    """
    dict_bus_lat_lng = {}
    doublemap_url = "http://bloomington.doublemap.com/map/v2/buses"
    response = json.loads(urllib.urlopen(doublemap_url).read())
    if len(response) == 0:
        print "Something went wrong while getting status of each bus..."
        sys.exit(0)    
    for bus in response:
        bus_number = bus['name']
        lat = bus['lat']
        lng = bus['lon']
        route = bus['route']
        bus_id = bus['id']
        lastUpdate = bus['lastUpdate']
        dict_bus_lat_lng[bus_number] = (lat,lng)
    return dict_bus_lat_lng

def test_get_all_buses_status():
    """
    Test function
    """
    return len(get_all_buses_status())

def get_route_status(input_colloquial_bus_numbers_list):
    """
    This function returns a dictionary with status of each bus on each input route
    input_route_list can have one or a list of bus numbers. This will be used to get the route numbers. 
    For example, user might want yo travel by route 6 OR route 9. Then we feed both route numbers for route6 and 9 to this function.
    Output: Each bus running on the input route along with its latitude and longitude.
    """
    #Find route numbers from input bus numbers list
    dict_colloquial_bus_route = {}
    for bus_number in input_colloquial_bus_numbers_list:
        dict_colloquial_bus_route[bus] = map_colloquial_bus_number_to_route[bus_number]
    
    #Query doublemap API and get status for each route
    #To be done in JS now
    return None

if __name__ == "__main__":
    #test if the API is working
    if test_get_all_buses_status():
        print "Code accessing Doublemap API is working correctly"
    else:
        print "Something seems to be wrong with accessing code of Doublemap API"

    
