from flask import Flask, current_app, request, session, Flask, render_template, \
        flash, send_from_directory, redirect, g
from pprint import pprint
import json
import sys
from src.constants import Constants
from src.Route import Route

app = Flask(__name__)
app.debug = True
app.config.from_object(__name__)
const = Constants()
const.load_constants("../src/constants.json")

@app.route('/', methods=['POST', 'GET'])
def load():
    print "Loading!!"
    #urls = json.load(json_data)
    cities = const.COORDINATES
    if request.method == "POST":
        formData  = request.form
        userRequest = {}
        if 'busList' in formData:
            userRequest['busList'] = formData.getlist('busList')
        for key, value in formData.iteritems():
            if key != 'busList':
                userRequest[key] = value
    return render_template('mapTest.html', cities=cities)

@app.route('/busList/<city>', methods=['GET'])
def getBuses(city):
    route = Route(const, city)
    busList = route.get_all_buses()
    return json.dumps(busList)

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
