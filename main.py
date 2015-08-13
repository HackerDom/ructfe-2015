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

# Monkey-patch
json.JSONEncoder.default = lambda self, obj: obj.__dict__

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)


def static(filename):
    return ospath.join(ospath.abspath(__file__), filename)


class Term(object):
    def __init__(self, term="div", name="", term_id="", classes="", typ="",
                 style="", children=None, content="", value=""):
        self.term = term
        self.name = name
        self.id = term_id
        self.classes = classes
        self.style = style
        self.content = content
        self.children = children
        self.typ = typ
        self.value = value

    def __str__(self):
        return json.dumps(self)


class Form(Term):
    def __init__(self, name="", term_id="",
                 children=None, classes="", style="", errors=None):
        super(Form, self).__init__(self, name=name, term_id=term_id,
                                   classes=classes, style=style,
                                   children=children)
        self.term = "form"
        self.method = "POST"
        self.errors = errors


AUTH_FORM = Form(classes="auth-form",
            children=[Term(term="input", typ="text", name="user"),
                      Term(term="input", typ="password", name="password"),
                      Term(term="button", typ="submit",
                           content="Submit")])

class Handler(WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    #@gen.coroutine
    def on_message(self, message):
        message = json.loads(message)
        if message['action'] == 'auth':
            AUTH_FORM.errors = []
            if 'params' not in message:
                AUTH_FORM.errors.append(Term(classes="error",
                                   content="Invalid request"))
                return self.write_message(json.dumps(AUTH_FORM))
            params = message['params']
            if 'user' not in params or params['user'] == "":
                AUTH_FORM.errors.append(Term(classes="error",
                                        content="username is not present"))
            else:
                if 'password' not in params or params['password'] == "":
                    AUTH_FORM.errors.append(
                        Term(classes="error",
                             content="password is not present"))
                    return self.write_message(json.dumps(AUTH_FORM))
                username, password = params['user'], params['password']

                if username != 'admin':
                    AUTH_FORM.errors.append(Term(classes="error",
                                            content="Invalid user"))
                else:
                    if password != 'qwerty':
                        AUTH_FORM.errors.append(
                            Term(classes="error",
                                 content="Invalid password"))
                        return self.write_message(json.dumps(AUTH_FORM))
                    return self.write_message(json.dumps(
                        Term(children=[
                            Term(term="h1",
                                 content="Hello %s" % username),
                            Term(term="h2",
                                 content="Your password: %s" % password)
                        ])
                    ))

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