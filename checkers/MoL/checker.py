#!/usr/local/bin/python3
# coding=utf-8
from random import randrange
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
        answer = ws.recv()
        if loads(answer)['rows'][0]['view'] != "form":
            raise KeyError
        username, password = ('%x' % randrange(16**15),
                              '%x' % randrange(16**15))
        ws.send(dumps({'action': 'register',
                       'params': {'user': username, 'password': password}}))
        answer = ws.recv()
        if "successfull" not in loads(answer)["text"]:
            print("registration failed: %s" % answer, file=stderr)
            print("Registration")
            return CORRUPT

        print(answer)
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
