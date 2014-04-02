import json
import sys

class Singleton(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(Singleton, cls).__call__(*args, **kwargs)
            return cls.__instance

class Constants(object):
    __metaclass__ = Singleton
    """
    This class reads data from JSON files and stores all the constants.
    """
    DOUBLEMAP_BUSES_API_URL = {}
    DOUBLEMAP_ROUTES_API_URL = {}
    COORDINATES = {}
    APPROACHING = 0
    STOPPED = 0
    LEAVING = 0
    def load_constants(self, filename):
        """
        Read json file and load all constants
        """
        try:
            dict_values = json.loads(open(filename,"r").read())
        except:
            print "Error loading constants json file because: ",sys.exc_info()[1]
            sys.exit(0)
        self.DOUBLEMAP_BUSES_API_URL = dict_values['DOUBLEMAP_BUSES_API_URL']
        self.DOUBLEMAP_ROUTES_API_URL = dict_values['DOUBLEMAP_ROUTES_API_URL']
        self.COORDINATES = dict_values['COORDINATES']
        self.APPROACHING = dict_values['APPROACHING']
        self.STOPPED = dict_values['STOPPED']
        self.LEAVING = dict_values['LEAVING']
        
if __name__ == "__main__":
    filename = "constants.json"
    myTestObj = Constants()
    myTestObj.load_constants(filename)
    print myTestObj.DOUBLEMAP_BUSES_API_URL['NW']
    print myTestObj.DOUBLEMAP_ROUTES_API_URL 
    print myTestObj.APPROACHING
    print myTestObj.STOPPED
    print myTestObj.LEAVING
    
