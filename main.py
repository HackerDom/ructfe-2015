#!/usr/local/bin/python3
from uuid import uuid4
from psycopg2 import ProgrammingError
from tornado.httpserver import HTTPServer

__author__ = 'm_messiah'
import logging
from signal import signal, SIGTERM
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado import gen
from json import loads, dumps
import momoko
from hashlib import sha256

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)

import templates as tpl


def authorized(f):
    def wrapper(*args):
        if args[0].uid:
            return f(*args)
        else:
            args[0].write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Not authorized"))
            )
    return wrapper


class Handler(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.uid = None

    def open(self):
        print("WebSocket opened")

    @gen.coroutine
    def on_message(self, message):
        message = loads(message)
        if hasattr(self, message['action']):
            return getattr(self, message['action'])(message)
        else:
            return self.write_message(dumps(tpl.AUTH_FORM))

    def auth(self, message):
        if 'params' not in message:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid request"))
            )
        params = message['params']
        if 'user' not in params or params['user'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Username must not be empty"))
            )
        if 'password' not in params or params['password'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Password must not be empty"))
            )

        username, password = (
            params['user'],
            sha256(params['password'].encode("utf8")).hexdigest()
        )
        cursor = yield self.application.db.execute(
            "select uid, password from users where username=%s", (username,)
        )
        db_result = cursor.fetchone()
        if not db_result:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Username does not exists"))
            )
        if password != db_result[1]:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid password"))
            )

        self.uid = db_result[0]
        #return self.write_message(dumps(dict(tpl.MESSAGE, text="%s" % self.uid)))
        return self.write_message(dumps(tpl.INDEX))

    def register(self, message):
        if 'params' not in message:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid request"))
            )
        params = message['params']
        if 'user' not in params or params['user'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Username must not be empty"))
            )
        if 'password' not in params or params['password'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Password must not be empty"))
            )

        username, password = (
            params['user'],
            sha256(params['password'].encode("utf8")).hexdigest()
        )
        cursor = yield self.application.db.execute(
            "select uid, password from users where username=%s", (username,)
        )
        db_result = cursor.fetchone()
        if db_result:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="User already exists"))
            )
        try:
            cursor = yield self.application.db.execute(
                "INSERT INTO users(uid, username, password, role)"
                "VALUES (%(uid)s, %(username)s, %(password)s, false)",
                {'username': username, 'password': password,
                 'uid': str(uuid4().hex)}
            )
        except ProgrammingError:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Error while registration"))
            )
        else:
            return self.write_message(
                dumps(dict(tpl.MESSAGE, text="Registration successful"))
            )

    @authorized
    def show_all(self, message):
        return self.write_message(dumps(tpl.INDEX))

    def on_close(self):
        print("WebSocket closed")


def signal_term_handler(sig, _):
    logging.error("Got %s. Quit.", sig)
    exit(0)


if __name__ == '__main__':
    signal(SIGTERM, signal_term_handler)
    app = Application([
        (r"/websocket", Handler),
        (r"/()", StaticFileHandler, {'path': 'static/index.html'}),
        (r"/(.+)", StaticFileHandler, {'path': 'static/'}),
    ])
    try:
        ioloop = IOLoop.instance()
        app.db = momoko.Pool(dsn="dbname=mot user=mot password=motpassword "
                                 "host=localhost port=5432",
                             size=1, ioloop=ioloop)
        future = app.db.connect()
        ioloop.add_future(future, lambda _: ioloop.stop())
        ioloop.start()
        future.result()
        http_server = HTTPServer(app)
        http_server.listen("1984")
        ioloop.start()
    except KeyboardInterrupt:
        signal_term_handler(SIGTERM, None)
