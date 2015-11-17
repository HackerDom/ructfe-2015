import os.path

def checklib_location():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))