import json
import sys

class Constants:
    """
    This class reads data from JSON files and stores all the constants.
    """
    DOUBLEMAP_BUSES_API_URL = {}
    DOUBLEMAP_ROUTES_API_URL = {}
    
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
        
if __name__ == "__main__":
    filename = "constants.json"
    myTestObj = Constants()
    myTestObj.load_constants(filename)
    print myTestObj.DOUBLEMAP_BUSES_API_URL['NORTHWESTERN']
    print myTestObj.DOUBLEMAP_ROUTES_API_URL 
