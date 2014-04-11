#This file has functions to get data using Google maps API
import json
import sys
import urllib

def form_request_url(API_KEY, address, sensor):
    """
    forms a url that can be requested to get json data from geoding api
    output sample: https://maps.googleapis.com/maps/api/geocode/json?key=AIzaSyBWBstysdfsdfhMOsdfsdFkpQGMzsdfsdfHUJRZ8Ps&address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&sensor=false
    """
    geocoding_url = "https://maps.googleapis.com/maps/api/geocode/"
    output_format = "json?"
    parameters = "key="+API_KEY+"&address="+ "+".join(address.split()) + "&sensor="+ sensor
    
    output_url = geocoding_url+output_format+parameters
    return output_url

def extract_long_lat_from_response(input_geocoded_json):
    """
    This function extracts longitude and latitiude information from response received from Google Geocoding API.
    Returns tuple(lat,lng)
    """
    #check if status of response is OK, only then proceed to next step.
    if input_geocoded_json['status'] == "OK":
        lat = input_geocoded_json['results'][0]['geometry']['location']['lat']
        lng = input_geocoded_json['results'][0]['geometry']['location']['lng']
        return (lat,lng)
    else:
        return (0,0)

def get_lat_lng_of_address(API_KEY, input_address):
    """
    Returns latitude and longitude of input address.
    """
    url = form_request_url(API_KEY, input_address, 'false')
    (latitude,longitude) = extract_long_lat_from_response(json.loads(urllib.urlopen(url).read()))
    return (latitude,longitude)

def test_get_lat_lng_of_address():
    """
    Tests if get_lat_lng_of_address() function is working correctly
    """
    #case 1: address : 1600 Amphitheatre Parkway, Mountain View, CA.
    #Expected output : "lat" : 37.42291810, "lng" : -122.08542120
    API_KEY=open("API_KEY.txt","r").readlines()[0].strip("\n").strip("\r")
    address = "2029 Ridge Ave, Evanston, IL, United States"
    return ( (37.421998500000001,-122.0839544) == get_lat_lng_of_address(API_KEY,address) )

if __name__ == "__main__":
        
    if test_get_lat_lng_of_address():
        print "get_lat_lng_of_address() working correctly"
    else:
        print "get_lat_lng_of_address() NOT working correctly"
