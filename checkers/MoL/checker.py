#!/usr/local/bin/python3
# coding=utf-8
from random import randrange, choice
from sys import argv, stderr
from os import path
from websocket import create_connection
from socket import gaierror
from json import loads, dumps
from csv import reader

__author__ = 'm_messiah'

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110


def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    exit(code)


class Client(object):
    def __init__(self, sock, username, password):
        self.username = username
        self.password = password
        self.ws = sock

    def register(self):
        """Registration"""
        self.ws.send(dumps(
            {'action': 'register',
             'params': {'user': self.username, 'password': self.password}}))
        answer = loads(self.ws.recv())
        if "successful" not in answer["text"]:
            close(CORRUPT, "Registration", "registration failed: %s" % answer)
        return answer

    def auth(self):
        """Authentication"""
        self.ws.send(dumps(
            {'action': 'auth',
             'params': {'user': self.username, 'password': self.password}}))
        answer = loads(self.ws.recv())
        if "Welcome" not in answer["text"]:
            close(CORRUPT,
                  "Authentication", "authentication failed: %s" % answer)

        if "text" not in answer and "Welcome" not in answer["text"]:
            if "id" not in answer:
                close(CORRUPT,
                      "Authentication", "authentication failed: %s" % answer)
            else:
                _ = self.ws.recv()
        if "rows" not in answer:
            answer = loads(self.ws.recv())
        # Show Profiles"""
        if ("data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 5):
            close(CORRUPT, "Profiles", "showProfile failed: %s" % answer)
        return answer

    def crimes(self):
        """Last crimes"""
        self.ws.send(dumps({'action': 'show_crimes',
                            'params': {'offset': 0}}))
        answer = loads(self.ws.recv())
        if ("rows" not in answer or
                "data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 2 or
                "crimeid" not in answer["rows"][0]["data"][0]):
            close(CORRUPT, "Crimes", "List crimes failed: %s" % answer)
        return answer

    def assign_profile(self):
        """Assign Profile"""
        self.ws.send(dumps(
            {'action': 'its_me',
             'params': {'profileid': "3ad31a62-aaf8-431e-aa5b-03c0423f6433",
                        'info': "0483847872"}}))
        answer = loads(self.ws.recv())
        if "successful" not in answer["text"]:
            close(CORRUPT, "Assignment", "assignment failed: %s" % answer)
        return answer

    def my_profile(self):
        """My profile"""
        self.assign_profile()
        self.ws.send(dumps({'action': 'show_my_profile'}))
        answer = loads(self.ws.recv())
        if ("rows" not in answer or
                "cols" not in answer["rows"][0] or
                'rows' not in answer['rows'][0]['cols'][0] or
                'hidden' not in answer['rows'][0]['cols'][0]['rows'][0] or
                not answer['rows'][0]['cols'][0]['rows'][0]['hidden']):
            close(CORRUPT, "My profile", "My profile failed: %s" % answer)
        return answer

    def report(self, flag_id=None, flag=None):
        crimes = list(reader(open(
            path.join(path.dirname(path.realpath(__file__)), "crimes.csv"))))
        tags, crimes = crimes[0], crimes[1:]
        crime = dict(zip(tags, choice(crimes)))
        if flag_id:
            crime['name'] = flag_id
        if flag:
            crime['description'] += " " + flag
        crime['closed'] = crime['closed'] == "true"

        self.ws.send(dumps({'action': 'report', 'params': crime}))
        answer = loads(self.ws.recv())
        if "submited" not in answer["text"]:
            close(CORRUPT, "Report", "flag put failed: %s" % answer)
        return answer

    def show_report(self, flag_id, flag):
        pass


def check(*args):
    addr = args[0]
    answer = ""
    if not addr:
        close(INTERNAL_ERROR, None, "Check without ADDR")
    try:
        ws = create_connection("ws://%s:1984/websocket" % addr)
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        c = Client(ws, '%x' % randrange(16**15), '%x' % randrange(16**15))
        c.register()
        c.auth()
        choice([c.crimes, c.my_profile])()
        choice([c.crimes, c.my_profile])()
        c.report()
        close(OK)
    except gaierror:
        close(FAIL, "No connection to %s" % addr)
    except (KeyError, IndexError):
        close(CORRUPT, "JSON structure", "Bad answer in %s" % answer)
    finally:
        try:
            ws.close()
        except:
            pass


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    answer = ""
    if not addr or not flag_id or not flag:
        close(INTERNAL_ERROR, None, "Incorrect parameters")
    try:
        ws = create_connection("ws://%s:1984/websocket" % addr)
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        c = Client(ws, '%x' % randrange(16**15), '%x' % randrange(16**15))
        c.register()
        c.auth()
        c.report(flag_id, flag)
        close(OK, "%s:%s:%s" % (c.username, c.password, flag_id))
    except gaierror:
        close(FAIL, "No connection to %s" % addr)
    except (KeyError, IndexError):
        close(CORRUPT, "JSON structure", "Bad answer in %s" % answer)
    finally:
        try:
            ws.close()
        except:
            pass


def get(*args):
    addr = args[0]
    username, password, flag_id = args[1].split(":")
    flag = args[2]
    answer = ""
    if not addr or not username or not password or not flag_id or not flag:
        close(INTERNAL_ERROR, None, "Incorrect parameters")
    try:
        ws = create_connection("ws://%s:1984/websocket" % addr)
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        c = Client(ws, username, password)
        c.auth()
        c.show_report(flag_id, flag)
        close(OK)
    except gaierror:
        close(FAIL, "No connection to %s" % addr)
    except (KeyError, IndexError):
        close(CORRUPT, "JSON structure", "Bad answer in %s" % answer)
    finally:
        try:
            ws.close()
        except:
            pass


COMMANDS = {'check': check, 'put': put, 'get': get}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return INTERNAL_ERROR


if __name__ == '__main__':
    # try:
    exit(COMMANDS.get(argv[1], not_found)(*argv[2:]))
    # except:
    #    exit(INTERNAL_ERROR)
