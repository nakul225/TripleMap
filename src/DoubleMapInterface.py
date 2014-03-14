#This code will keep a track of locations of each bus
from GoogleMapsApiInterface import *
import json
import urllib
import sys
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

def map_route_to_colloquial_bus_number():
    """
    This code maps route numbers to natural numbers used for buses. For example, route 6 (bus name:553 ) runs on route no. 1001545
    """
    dict_route_number_to_colloquial_bus_number =    {
                                                        '1001529' : '1 S.Walnut',
                                                        '1001531':'1 Fee Lane',
                                                        '1001527':'2 S.Rogers',
                                                        '1001537':'3 Curry Pike',
                                                        '1001536':'3 College Mall',
                                                        '1001541':'4 High Street',
                                                        '1001539':'4 Bloomfield',
                                                        '1001543':'5',
                                                        '1001545':'6',
                                                        '1001561':'9',
                                                        '2000316':'A',
                                                        '2000318':'B',
                                                        '2000319':'D',
                                                        '2000320':'E'
                                                    }

if __name__ == "__main__":
    #test if the API is working
    if test_get_all_buses_status():
        print "Code accessing Doublemap API is working correctly"
    else:
        print "Something seems to be wrong with accessing code of Doublemap API"

    
