#!/usr/local/bin/python3
__author__ = 'm_messiah'
import logging
from signal import signal, SIGTERM
from os import path as ospath
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from tornado.websocket import WebSocketHandler
#from tornado import gen
import json
from copy import deepcopy

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)


AUTH_FORM = {'view': "form",
             'id': "auth",
             'width': 300,
             'elements': [
                 {'view': 'text', 'label': "Username", 'name': "user"},
                 {'view': 'text', 'label': "Password", 'name': "password",
                  'type': 'password'},
                 {'view': 'button', 'label': "Login", 'click': 'submit',
                  'type': 'iconButton', 'icon': 'sign-in', 'align': 'center'},
             ]}


class Handler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    #@gen.coroutine
    def on_message(self, message):
        message = json.loads(message)
        if message['action'] == 'auth':
            err_form = deepcopy(AUTH_FORM)
            if 'params' not in message:
                err_form['elements'].append(
                    {'view': 'label', 'label': "Invalid request"}
                )
                return self.write_message(json.dumps(err_form))
            params = message['params']
            if 'user' not in params or params['user'] == "":
                err_form['elements'].append(
                    {'view': 'label', 'label': "Username is not present"}
                )
                return self.write_message(json.dumps(err_form))
            else:
                if 'password' not in params or params['password'] == "":
                    err_form['elements'].append(
                        {'view': 'label', 'label': "Password is not present"}
                    )
                    return self.write_message(json.dumps(err_form))
                username, password = params['user'], params['password']

                if username != 'admin':
                    err_form['elements'].append(
                        {'view': 'label', 'label': "Invalid user"}
                    )
                    return self.write_message(json.dumps(err_form))
                else:
                    if password != 'qwerty':
                        err_form['elements'].append(
                            {'view': 'label', 'label': "Invalid password"}
                        )
                        return self.write_message(json.dumps(err_form))
                    return self.write_message(json.dumps({
                        'id': 'output',
                        'rows': [
                            {'template': '<h1>Hello, %s</h1>' % username},
                            {'template': '<h2>Your password is: %s</h2>'
                                         % password},
                        ]}))

        self.write_message(json.dumps(AUTH_FORM))
        #yield gen.sleep(2)

    def on_close(self):
        print("WebSocket closed")


def signal_term_handler(sig, _):
    logging.error("Got %s. Quit.", sig)
    exit(0)

app = Application([(r"/websocket", Handler),
                   (r"/()", StaticFileHandler, {'path': 'static/index.html'}),
                   (r"/(.+)", StaticFileHandler, {'path': 'static/'}),
                   ])

if __name__ == '__main__':
    signal(SIGTERM, signal_term_handler)
    try:
        app.listen("2707")
        IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(SIGTERM, None)