#!/usr/local/bin/python3
from random import choice
from uuid import uuid4
from psycopg2 import ProgrammingError
from tornado.httpserver import HTTPServer
import logging
from signal import signal, SIGTERM
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado import gen
from json import loads, dumps, JSONEncoder
import momoko
from hashlib import sha256
import templates as tpl
import datetime

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)


def authorized(f):
    def wrapper(*args):
        if args[0].uid:
            return f(*args)
        else:
            args[0].write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Not authorized"))
            )
            args[0].write_message(dumps(tpl.AUTH_FORM))

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
            try:
                return getattr(self, message['action'])(message)
            except:
                self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                              text="Bad request")))
        else:
            return self.write_message(dumps(tpl.AUTH_FORM))

    @gen.coroutine
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
            if db_result[0] in self.application.wsPool:
                self.application.wsPool[db_result[0]].write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="Someone wants to hack you")))
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid password"))
            )

        self.uid = db_result[0]
        self.write_message(dumps(dict(tpl.MESSAGE,
                                      text="Welcome, %s" % username)))
        self.application.wsPool[self.uid] = self
        yield self.show_profiles({'params': {'offset': 0}})

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

    #@authorized
    @gen.coroutine
    def show_profiles(self, message):
        offset = message['params']['offset'] * 10
        if offset < 0:
            offset = 0

        cursor = yield self.application.db.execute(
            "select profileid, name, lastname, userpic from profiles "
            "limit 10 offset %s" % (offset,)
        )
        db_result = cursor.fetchall()
        users = [
            dict(zip('uid name lastname userpic'.split(), row))
            for row in db_result
        ]
        result = tpl.PROFILES.copy()
        result['rows'][0]['data'] = users
        return self.write_message(dumps(result))

    #@authorized
    @gen.coroutine
    def show_profile(self, message):
        try:
            cursor = yield self.application.db.execute(
                "select name, lastname, userpic, birthdate, "
                "city, mobile, marital, crimes from profiles "
                "where profileid=%s", (message['params']['uid'], )
            )
            db_result = cursor.fetchone()
            if not db_result:
                raise Exception
            user = dict(zip("name lastname userpic birthdate "
                            "city mobile marital crimes".split(),
                            db_result))
            user['birthdate'] = user['birthdate'].isoformat()
            user['marital_icon'] = (
                choice(['fa-venus-mars', 'fa-venus-double', 'fa-mars-double'])
                if user['marital'] else 'fa-genderless'
            )
            if user['crimes']:
                crimes = yield self.get_crimes(user['crimes'])
            else:
                crimes = None
            result = tpl.PROFILE.copy()
            result['rows'][0]['cols'][0]['rows'][0]['data'] = {
                'userpic': user['userpic']
            }
            result['rows'][0]['cols'][0]['rows'][1]['data'] = {
                'icon': 'fa-balance-scale' if not crimes
                else ''
            }
            result['rows'][0]['cols'][1]['rows'][0]['data'] = user
            if crimes:
                result['rows'][0]['cols'][1]['rows'][1]['hidden'] = False
                result['rows'][0]['cols'][1]['rows'][1]['data'] = crimes
            else:
                result['rows'][0]['cols'][1]['rows'][1]['hidden'] = True
            return self.write_message(dumps(result))
        except Exception as e:
            self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                          text="Bad request: %s" % e)))

    @gen.coroutine
    def get_crimes(self, crimes):
        result = []
        try:
            cursor = yield self.application.db.execute(
                "SELECT crimeid, name, article, city, country,"
                "crimedate, description, participants, judgement, closed "
                "FROM crimes WHERE public=true AND crimeid = ANY(%s)",
                (crimes,)
            )
            db_result = cursor.fetchall()
            if not db_result:
                raise Exception("db error")
            for row in db_result:
                crime = dict(zip("crimeid name article city country "
                                 "crimedate description participants "
                                 "judgement closed".split(),
                                 row))
                crime['crimedate'] = crime['crimedate'].isoformat()
                cursor_participants = yield self.application.db.execute(
                    "select profileid, name, lastname "
                    "from profiles where profileid=ANY(%s)",
                    (crime["participants"],)
                )
                db_result_participants = cursor_participants.fetchall()
                if not db_result_participants:
                    raise Exception("participants not in database")
                crime['participants'] = "<br>".join(
                    '<a onclick="showProfile(0,0, this);" '
                    'data-uid="%s">%s %s</a>' % (r[0], r[1], r[2])
                    for r in db_result_participants
                )
                result.append(crime)

            return result
        except Exception as e:
            self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                          text="Can't get crimes: %s" % e)))

    #@authorized
    @gen.coroutine
    def show_crimes(self, message):
        offset = message['params']['offset'] * 10
        if offset < 0:
            offset = 0

        cursor = yield self.application.db.execute(
            "select crimeid, name, article, city, country, crimedate "
            "FROM crimes limit 10 offset %s", (offset,)
        )
        db_result = cursor.fetchall()
        crimes = [
            dict(zip('crimeid name article city country crimedate'.split(),
                     row))
            for row in db_result
        ]
        for crime in crimes:
            crime['crimedate'] = crime['crimedate'].isoformat()
        result = tpl.CRIMES.copy()
        result['rows'][0]['data'] = crimes
        return self.write_message(dumps(result))

    def on_close(self):
        print("WebSocket %s closed" % self.uid)


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
        app.wsPool = {}
        ioloop.start()
        future.result()
        http_server = HTTPServer(app)
        http_server.listen("1984")
        ioloop.start()
    except KeyboardInterrupt:
        signal_term_handler(SIGTERM, None)
