#!/usr/bin/env python3
# coding=utf-8
from random import randrange, shuffle, choice
from hashlib import sha1
from time import time
from urllib.error import URLError as http_error
from urllib.request import build_opener, HTTPCookieProcessor
from urllib.parse import urlencode
from http.cookiejar import CookieJar
from sys import argv, stderr

__author__ = 'm_messiah, crassirostris'

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110

NAMES_FILENAME = 'names.txt'
MAX_PAGE_SIZE = 1024 * 1024


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    exit(code)

def create_name():
    with open(NAMES_FILENAME, 'r') as f:
        lines = f.readlines()
    return choice(lines).strip()

def create_password():
    return sha1(str(time()).encode("utf-8")).hexdigest()

def generate_comment():
    return "Totally fine!"

def create_metrics(flag):
    return { "Weight": randrange(40, 100),
        "BloodPressure": randrange(80, 120),
        "Pulse": randrange(70, 150),
        "WalkingDistance": randrange(1000, 10 * 1000),
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
        self.open_and_check_ok('newuser', self.encode_user_data())

    def auth(self):
        self.open_and_check_ok('login', self.encode_user_data())

    def add_metrics(self, metrics):
        self.open_and_check_ok('addhealthmetrics', urlencode(metrics))

    def get_metrics(self):
        return self.open_and_check_ok('healthmetrics')

    def open_and_check_ok(self, path, data = None):
        opener = build_opener(HTTPCookieProcessor(self.cookie_jar))
        url = "http://%s/%s" % (self.addr, path)
        if isinstance(data, str):
            data = data.encode("utf-8")
        response = opener.open(url, data)
        if response.getcode() != 200:
            raise CheckerException("Recieved status %d on request %s"
                % (response.getcode(), response.geturl()))
        return response.read(MAX_PAGE_SIZE).decode('utf-8')

    def encode_user_data(self):
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
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


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
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


def get(*args):
    addr = args[0]
    checker_flag_id = args[1]
    flag = args[2]
    c = Client(addr, checker_flag_id.split(":"))
    try:
        c.auth()
        if flag in c.get_metrics():
            close(OK)
        close(GET_ERROR, "Flag is missing")
    except http_error as e:
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return INTERNAL_ERROR


if __name__ == '__main__':
    try:
        COMMANDS.get(argv[1], not_found)(*argv[2:])
    except Exception as e:
        close(INTERNAL_ERROR, "Sweet and cute checker =3", "INTERNAL ERROR: %s" % e)