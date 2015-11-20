import os.path

def checklib_location():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def merge_dicts(*dicts):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dicts:
        result.update(dictionary)
    return result