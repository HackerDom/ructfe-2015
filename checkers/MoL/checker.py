#!/usr/local/bin/python3
# coding=utf-8
from random import randrange, choice
from sys import argv, stderr
from websocket import create_connection
from socket import gaierror
from json import loads, dumps

__author__ = 'm_messiah'

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110


def check(*args):
    addr = args[0]
    answer = ""
    if not addr:
        print("Check without ADDR")
        return INTERNAL_ERROR
    try:
        ws = create_connection("ws://%s:1984/websocket" % addr)
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        username, password = ('%x' % randrange(16**15),
                              '%x' % randrange(16**15))

        # 1. Registration
        ws.send(dumps({'action': 'register',
                       'params': {'user': username, 'password': password}}))
        answer = loads(ws.recv())
        if "successful" not in answer["text"]:
            print("registration failed: %s" % answer, file=stderr)
            print("Registration")
            return CORRUPT

        # 2. Authentication
        ws.send(dumps({'action': 'auth',
                       'params': {'user': username, 'password': password}}))
        answer = loads(ws.recv())
        if "Welcome" not in answer["text"]:
            print("authentication failed: %s" % answer, file=stderr)
            print("Authentication")
            return CORRUPT

        if "text" not in answer and "Welcome" not in answer["text"]:
            if "id" not in answer:
                print("authentication failed: %s" % answer, file=stderr)
                print("Authentication")
                return CORRUPT
            else:
                _ = ws.recv()
        if "rows" not in answer:
            answer = loads(ws.recv())
        # 3. Show Profiles
        if ("data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 5):
            print("showProfile failed: %s" % answer, file=stderr)
            print("Profiles")
            return CORRUPT

        # 4. Last crimes
        ws.send(dumps({'action': 'show_crimes',
                       'params': {'offset': 0}}))
        answer = loads(ws.recv())
        if ("rows" not in answer or
                "data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 2 or
                "crimeid" not in answer["rows"][0]["data"][0]):
            print("List crimes failed: %s" % answer, file=stderr)
            print("Crimes")
            return CORRUPT

        # 5. Assign Profile
        ws.send(dumps(
            {'action': 'its_me',
             'params': {'profileid': "3ad31a62-aaf8-431e-aa5b-03c0423f6433",
                        'info': "0483847872"}}))
        answer = loads(ws.recv())
        if "successful" not in answer["text"]:
            print("assignment failed: %s" % answer, file=stderr)
            print("Assignment")
            return CORRUPT

        # 6. My profile

        # 7. Report form

        print(answer)
        return OK
    except gaierror:
        print("No connection to %s" % addr, file=stderr)
        return FAIL
    except (KeyError, IndexError):
        print("Bad answer in %s" % answer, file=stderr)
        print("JSON structure")
        return CORRUPT
    finally:
        try:
            ws.close()
        except:
            pass


def put():
    pass


def get():
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
