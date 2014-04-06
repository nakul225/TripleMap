from flask import Flask, current_app, request, session, Flask, render_template, \
        flash, send_from_directory, redirect, g, Response
from pprint import pprint

from src.constants import Constants
from src.Route import Route
from src.TripleMap import TripleMapClient

import json
import sys
import time

import gevent
from gevent.wsgi import WSGIServer
from gevent.queue import Queue

app = Flask(__name__)
app.debug = True
app.config.from_object(__name__)
const = Constants()
const.load_constants("../src/constants.json")
tplClient = None

@app.route('/home', methods=['POST', 'GET'])
def load():
    print "Loading!!"
    #urls = json.load(json_data)
    cities = const.COORDINATES
    mapUrl = const.DOUBLEMAP_BUSES_API_URL
    if request.method == "POST":
        formData  = request.form
        userRequest = formData.to_dict()
        if 'busList' in userRequest:
            userRequest['busList'] = json.loads(userRequest['busList'])
            #publish()
            tplClient = TripleMapClient(userRequest)
            #tplClient.pollDistance()

    return render_template('mapTest.html', cities=cities, mapUrl = mapUrl)
#http://www.watchcric.com/channel/live-cricket-4
@app.route('/busList/<city>', methods=['GET'])
def getBuses(city):
    route = Route(const, city)
    busList = route.get_all_buses()
    return json.dumps(busList)

@app.route('/alert')
def publish():
    def alert():
        busNumber = tplClient.pollDistance()
        return 'data: ' + busNumber
        '''
        while True:
            time.sleep(3)
            yield 'data: %s\n' % 'hola!'
        '''
    return Response(alert(), mimetype="text/event-stream")

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def server_error(e):
    """Return a custom 500 error."""
    print
    return 'Sorry, unexpected error:\n{}'.format(e), 500

def main():
    app.debug = True
    app.run()

if __name__ == '__main__':
    main()
