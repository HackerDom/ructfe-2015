import os.path
import random
import checklib.utils

def string(chars, count, first_uppercase=False):
    if type(count) is not int:
        count = random.choice(count)

    if count < 0:
        raise Exception('Can\'t generate string with %d chars' % count)

    result = ''.join([random.choice(chars) for _ in range(count)])

    if first_uppercase and len(result) > 0:
        result = result[0].upper() + result[1:]

    return result


def integer(variants):
    return random.choice(variants)


def _from_collection(name):
    with open(os.path.join(checklib.utils.checklib_location(), 'collections', name)) as f:
        collection = f.readlines()
    collection = [s.rstrip() for s in collection]
    return random.choice(collection)

def firstname():
    return _from_collection('firstname')

def lastname():
    return _from_collection('lastname')

def color():
    return _from_collection('color')