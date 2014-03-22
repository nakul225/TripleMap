from flask import Flask, current_app, request, session, Flask, render_template, \
        flash, send_from_directory, redirect, g
from pprint import pprint

app = Flask(__name__)
app.debug = True
app.config.from_object(__name__)


@app.route('/route', methods=['POST', 'GET'])
def load():
    print "Loading!!"
    if request.method == "POST":
        userRequestLat = request.form['lat']
        userRequestLng = request.form['lng']
    return render_template('mapTest.html')

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
