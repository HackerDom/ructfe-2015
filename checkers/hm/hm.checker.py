#!/usr/bin/env python3
# coding=utf-8
from __future__ import print_function
import random
import logging
import string
from hashlib import sha1
from time import time
from urllib.error import URLError as http_error
from urllib.request import build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from socket import error as network_error
from sys import argv, stderr

__author__ = 'm_messiah, crassirostris'

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110

NAMES_FILENAME = 'names.txt'
MAX_PAGE_SIZE = 1024 * 1024


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    print('Exit with code %d' % code, file=stderr)
    exit(code)

def create_name():
    res = ''.join(random.choice(string.ascii_lowercase) for i in range(random.randrange(3, 12)))
    res = random.choice(string.ascii_uppercase) + res
    return res

def create_password():
    return sha1(str(time()).encode("utf-8")).hexdigest()

def generate_comment():
    return "Totally fine!"

def create_metrics(flag):
    return { "Weight": random.randrange(40, 100),
        "BloodPressure": random.randrange(80, 120),
        "Pulse": random.randrange(70, 150),
        "WalkingDistance": random.randrange(1000, 10 * 1000),
        "Comment": flag }

class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)


class Client(object):
    def __init__(self, addr, user):
        self.addr = addr
        self.user = user
        self.cookie_jar = CookieJar()

    def create_user(self):
        logging.info('Create new user on server:')
        self.open_and_check_ok('newuser', self.encode_user_data())

    def auth(self):
        logging.info('Authenticate on server:')
        self.open_and_check_ok('login', self.encode_user_data())

    def add_metrics(self, metrics):
        logging.info('Add metrics: %s', metrics)
        self.open_and_check_ok('addhealthmetrics', urlencode(metrics))

    def get_metrics(self):
        return self.open_and_check_ok('healthmetrics')

    def open_and_check_ok(self, path, data = None):
        opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        url = "http://%s/%s" % (self.addr, path)
        logging.info('Try to get %s', url)
        logging.info('Cookies: %s', self.cookie_jar)
        if isinstance(data, str):
            data = data.encode("utf-8")
        response = opener.open(url, data)
        logging.info('Received http status code %d', response.getcode())
        if response.getcode() != 200:
            raise CheckerException("Recieved status %d on request %s"
                % (response.getcode(), response.geturl()))
        return response.read(MAX_PAGE_SIZE).decode('utf-8')

    def encode_user_data(self):
        logging.info('Encoding user %s', self.user)
        return urlencode({'Login': self.user[0], 'Pass': self.user[1]})


def check(*args):
    addr = args[0]
    c = Client(addr, (create_name(), create_password()))
    try:
        flag = generate_comment()
        c.create_user()
        c.auth()
        c.add_metrics(create_metrics(flag))
        if flag in c.get_metrics():
            close(OK)
        raise CheckerException("Didn't find posted flag")
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    user = (create_name(), create_password())
    c = Client(addr, user)
    try:
        c.create_user()
        c.auth()
        c.add_metrics(create_metrics(flag))
        close(OK, ":".join(user))
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def get(*args):
    addr = args[0]
    checker_flag_id = args[1]
    flag = args[2]
    c = Client(addr, checker_flag_id.split(":"))
    try:
        c.auth()
        if flag in c.get_metrics():
            close(OK)
        close(CORRUPT, "Flag is missing")
    except http_error as e:
        close(DOWN, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except network_error as e:
        close(DOWN, "Netowrk Error", "Network error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(MUMBLE, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(CHECKER_ERROR, "Unknown error", "Unknown error: %s" % e)


def info(*args):
    close(OK, "vulns: 1")


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return CHECKER_ERROR

	
if __name__ == '__main__':
    try:
        COMMANDS.get(argv[1], not_found)(*argv[2:])
    except Exception as e:
        close(CHECKER_ERROR, "Sweet and cute checker =3", "INTERNAL ERROR: %s" % e)