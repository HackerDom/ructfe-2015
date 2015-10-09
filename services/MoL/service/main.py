#!/usr/local/bin/python3
from collections import defaultdict
from random import choice, randint
from time import monotonic
from uuid import uuid4, UUID
import logging
from signal import signal, SIGTERM
from json import loads, dumps, JSONEncoder
from hashlib import sha256
import datetime

from psycopg2 import ProgrammingError, extras, DataError
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application, StaticFileHandler, RequestHandler
from tornado.websocket import WebSocketHandler
from tornado import gen
from momoko import Pool
import templates as tpl

extras.register_uuid()
JSONEncoder_olddefault = JSONEncoder.default


def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID):
        return str(o)
    if isinstance(o, (datetime.datetime, datetime.date, datetime.time)):
        return o.isoformat()
    return JSONEncoder_olddefault(self, o)
JSONEncoder.default = JSONEncoder_newdefault


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


class Profiles(RequestHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)

    @gen.coroutine
    def get(self):
        cursor = yield self.application.db.execute(
            "select profileid, name, lastname, userpic from profiles"
        )
        db_result = cursor.fetchall()
        users = [
            dict(zip('id name lastname userpic'.split(), row))
            for row in db_result
        ]
        for u in users:
            u["value"] = u["name"] + " " + u["lastname"]
        self.write({'data': users})


class Handler(WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super().__init__(application, request, **kwargs)
        self.uid = None
        self.role = False
        self.profile = None

    def open(self):
        logging.info("WebSocket opened")

    @gen.coroutine
    def on_message(self, message):
        message = loads(message)
        logging.debug("Message received")
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
        user = defaultdict(lambda: None, message['params'])
        if 'username' not in user or user['username'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Username must not be empty"))
            )
        if 'password' not in user or user['password'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Password must not be empty"))
            )

        user['password'] = sha256(user['password'].encode("utf8")).hexdigest()
        cursor = yield self.application.db.execute(
            "select uid, password, role, profile "
            "from users where username=%(username)s", user
        )
        db_result = cursor.fetchone()
        if not db_result:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Username does not exists"))
            )
        if user['password'] != db_result[1]:
            if db_result[0] in self.application.wsPool:
                self.application.wsPool[db_result[0]].write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="Someone wants to hack you")))
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid password"))
            )

        self.uid = db_result[0]
        self.role = db_result[2]
        self.profile = db_result[3]
        name = user['username']
        if self.profile:
            cursor = yield self.application.db.execute(
                "select name, lastname from profiles where profileid=%s",
                (self.profile,)
            )
            db_result = cursor.fetchone()
            if db_result:
                name = " ".join(db_result)

        self.write_message(dumps(dict(tpl.MESSAGE,
                                      text="Welcome, %s" % name)))

        self.application.wsPool[self.uid] = self
        yield self.show_profiles({'params': {'offset': 0}})

    def register(self, message):
        if 'params' not in message:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid request"))
            )
        user = defaultdict(lambda: None, message['params'])

        if 'username' not in user or user['username'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Username must not be empty"))
            )
        if 'password' not in user or user['password'] == "":
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Password must not be empty"))
            )

        user['password'] = sha256(user['password'].encode("utf8")).hexdigest()

        cursor = yield self.application.db.execute(
            "select uid from users where username=%(username)s", user
        )
        db_result = cursor.fetchone()
        if db_result:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="User already exists"))
            )
        try:
            user['uid'] = str(uuid4().hex)
            user['role'] = len(user['username']) < 3
            cursor = yield self.application.db.execute(
                "INSERT INTO users(uid, username, password, role, profile)"
                "VALUES (%(uid)s, %(username)s, "
                "%(password)s, %(role)s, %(profile)s)",
                user
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
    def search(self, message):
        try:
            text = message['params']['text']
            if not text:
                return
            text = text.split()
            if len(text) > 1:
                cursor = yield self.application.db.execute(
                    "select profileid, name, lastname from profiles "
                    "where name LIKE '%%'||%s||'%%' and "
                    "lastname LIKE '%%'||%s||'%%' limit 5 ",
                    (text[0], text[1])
                )
            else:
                cursor = yield self.application.db.execute(
                    "select profileid, name, lastname from profiles "
                    "where name LIKE '%%'||%s||'%%' or "
                    "lastname LIKE '%%'||%s||'%%' limit 5 ",
                    (text[0], text[0])
                )

            cursor_crimes = yield self.application.db.execute(
                "select crimeid, name, crimedate from crimes "
                "where name LIKE '%%'||%s||'%%' limit 5 ",
                (text[0], )
            )

            db_result = cursor.fetchall()
            users = [
                dict(zip('profileid name lastname'.split(), row))
                for row in db_result
            ]
            db_result = cursor_crimes.fetchall()
            crimes = [
                dict(zip('crimeid name crimedate'.split(), row))
                for row in db_result
            ]

            result = tpl.SEARCH.copy()
            result['rows'][0]['data'] = users
            result['rows'][1]['data'] = crimes
            return self.write_message(dumps(result))
        except:
            pass

    #@authorized
    @gen.coroutine
    def show_profiles(self, message):
        offset = message['params']['offset'] * 10
        try:
            cursor = yield self.application.db.execute(
                "select profileid, name, lastname, userpic from profiles "
                "limit 10 offset %s", (offset,)
            )
        except (DataError, ProgrammingError):
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Error while fetching"))
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
    def show_my_profile(self, message):
        try:
            if self.profile:
                return self.show_profile({'params': {'uid': str(self.profile)}})
            else:
                self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="You does not have a profile")))
        except Exception as e:
            self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                          text="Bad request: %s" % e)))

    #@authorized
    @gen.coroutine
    def show_profile(self, message):
        try:
            profileid = UUID(message['params']['uid'])
            cursor = yield self.application.db.execute(
                "select name, lastname, userpic, birthdate, "
                "city, mobile, marital, crimes from profiles "
                "where profileid=%s", (profileid, )
            )
            db_result = cursor.fetchone()
            if not db_result:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="Profile not found")))
            user = dict(zip("name lastname userpic birthdate "
                            "city mobile marital crimes".split(),
                            db_result))
            if not (self.role or self.profile == profileid):
                user['birthdate'] = user['mobile'] = "&lt;hidden&gt;"
            user['marital_icon'] = (
                choice(['fa-venus-mars', 'fa-venus-double', 'fa-mars-double'])
                if user['marital'] else 'fa-genderless'
            )
            if user['crimes']:
                crimes = yield self.get_crimes(user['crimes'], profileid)
            else:
                crimes = None
            result = tpl.PROFILE.copy()
            result['rows'][0]['cols'][0]['rows'][0]['hidden'] = (
                self.profile is not None
            )
            result['rows'][0]['cols'][0]['rows'][0]['click'] = ("itsMe('%s')"
                                                                % profileid)
            result['rows'][0]['cols'][0]['rows'][1]['data'] = {
                'userpic': user['userpic']
            }
            result['rows'][0]['cols'][0]['rows'][2]['data'] = {
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

    #@authorized
    @gen.coroutine
    def its_me(self, message):
        try:
            profileid = message['params']['profileid']
            info = message['params']['info']
            if self.profile:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="You already have a profile"))
                )
            if not self.uid:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="You does not have user account"))
                )
            try:
                cursor = yield self.application.db.execute(
                    "select birthdate, mobile from profiles "
                    "where profileid=%s",
                    (profileid, )
                )
                db_result = cursor.fetchone()
                if not db_result:
                    return self.write_message(
                        dumps(dict(tpl.ERROR_MESSAGE,
                                   text="Profile not found"))
                    )
                if (info == db_result[0].isoformat() or
                        "".join(filter(str.isdigit, info)) ==
                        "".join(filter(str.isdigit, db_result[1]))):
                    cursor = yield self.application.db.execute(
                        "UPDATE users SET profile=%s WHERE uid=%s",
                        (profileid, self.uid)
                    )
                else:
                    return self.write_message(
                        dumps(dict(tpl.ERROR_MESSAGE,
                                   text="Wrong information"))
                    )
            except ProgrammingError:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="Error while assignment"))
                )
            else:
                self.profile = profileid
                return self.write_message(
                    dumps(dict(tpl.MESSAGE, text="Assignment successful"))
                )

        except Exception as e:
            self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                          text="Bad request: %s" % e)))


    @gen.coroutine
    def get_crimes(self, crimes, current_profile):
        result = []
        try:
            cursor = yield self.application.db.execute(
                "SELECT crimeid, name, article, city, country,"
                "crimedate, description, participants, "
                "judgement, closed, public "
                "FROM crimes WHERE crimeid = ANY(%s)",
                (crimes,)
            )

            db_result = cursor.fetchall()
            if not db_result:
                return result
            for row in db_result:
                crime = dict(zip("crimeid name article city country "
                                 "crimedate description participants "
                                 "judgement closed public".split(),
                                 row))
                if crime['closed']:
                    crime['verdict'] = crime['judgement']
                else:
                    crime['verdict'] = "In processing"
                if not crime['public']:
                    if not (self.role or
                            self.profile == current_profile or
                            self.profile in crime['participants']):
                        continue
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
        try:
            cursor = yield self.application.db.execute(
                "select crimeid, name, article, city, "
                "country, crimedate, public "
                "FROM crimes ORDER BY crimeid "
                "DESC limit 10 offset %s" % (offset,)
            )
        except (DataError, ProgrammingError):
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE,
                           text="Error while fetching")))
        db_result = cursor.fetchall()
        crimes = [
            dict(zip(
                'crimeid name article city country crimedate public'.split(),
                row))
            for row in db_result
        ]
        for crime in crimes:
            crime['public'] = "" if crime['public'] else "fa-lock"
        result = tpl.CRIMES.copy()
        result['rows'][0]['data'] = crimes
        return self.write_message(dumps(result))

    #@authorized
    @gen.coroutine
    def show_crime(self, message):
        try:
            cursor = yield self.application.db.execute(
                "SELECT name, article, city, country, "
                "crimedate, description, participants, judgement, "
                "closed, public, author "
                "FROM crimes WHERE crimeid=%s", (message['params']['crimeid'],)
            )
            db_result = cursor.fetchone()
            crime = dict(zip("name article city country "
                             "crimedate description participants "
                             "judgement closed public author".split(),
                             db_result))

            cursor_participants = yield self.application.db.execute(
                "select profileid, name, lastname "
                "from profiles where profileid=ANY(%s)",
                (crime["participants"],)
            )
            db_result_participants = cursor_participants.fetchall()
            if not db_result_participants:
                    crime['participants'] = ""
            else:
                crime['participants'] = "<br>".join(
                    '<a onclick="showProfile(0,0, this);" '
                    'data-uid="%s">%s %s</a>' % (r[0], r[1], r[2])
                    for r in db_result_participants
                )
            result = tpl.CRIME.copy()
            result['rows'][0]['data'] = crime

            if (crime['public'] or self.role or self.uid == crime['author'] or
                    (self.profile and crime["participants"] and
                     str(self.profile) in crime["participants"])):
                return self.write_message(dumps(result))
            else:
                self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE,
                               text="You are not the Author or %s"
                               % " or ".join(
                                   [p[1][0] + ".&nbsp;" + p[2]
                                    for p in db_result_participants]))))
        except Exception as e:
            self.write_message(dumps(dict(tpl.ERROR_MESSAGE,
                                          text="Can't get crime: %s" % e)))


    #@authorized
    def report(self, message):
        try:
            if 'params' not in message:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE, text="Invalid request"))
                )
            params = dict(filter(lambda i: i[1], message['params'].items()))
            if len(params) < 6:
                return self.write_message(
                    dumps(dict(tpl.ERROR_MESSAGE, text="Small input"))
                )
            params['city'] = params['city'].title()
            if len(params['country']) < 4:
                params['country'] = params['country'].upper()
            else:
                params['country'] = params['country'].title()

            params['crimedate'] = datetime.datetime.strptime(
                params['crimedate'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
            if 'closed' not in params:
                params['judgement'] = None
                params['closed'] = False
            else:
                params['closed'] = params['closed'] > 0
            params['public'] = 'private' not in params
            params['crimeid'] = int(monotonic() * 1000000000)
            params['author'] = self.uid

            if 'participants' in params:
                params['participants'] = list(
                    map(UUID, params['participants'].split(','))
                )
            else:
                params['participants'] = None
            sql = [(
                "INSERT INTO crimes(crimeid, name, article, city, "
                "country, crimedate, description, participants, "
                "judgement, closed, public, author) "
                "VALUES (%(crimeid)s, %(name)s, %(article)s, %(city)s, "
                "%(country)s, %(crimedate)s, %(description)s, "
                "%(participants)s, %(judgement)s, %(closed)s, "
                "%(public)s, %(author)s)", params
            ),]
            if params['participants']:
                sql.append((
                    "UPDATE profiles SET crimes=crimes|| %(crimeid)s::bigint "
                    "WHERE profileid = ANY(%(participants)s)", params
                ))
            cursors = self.application.db.transaction(sql)
        except ProgrammingError:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Error while reporting"))
            )
        except Exception as e:
            return self.write_message(
                dumps(dict(tpl.ERROR_MESSAGE, text="Invalid input %s " % e))
            )
        else:
            try:
                for ws in self.application.wsPool:
                    if self.application.wsPool[ws] == self:
                        continue
                    self.application.wsPool[ws].write_message(
                        dumps(dict(tpl.MESSAGE,
                                   text="New crime (%s)" % params['name']))
                    )
            except Exception as e:
                logging.warning("%s. Clients: %s"
                                % (e, self.application.wsPool.keys()))
            else:
                return self.write_message(
                    dumps(dict(tpl.MESSAGE,
                               text="Crime %s submited" % params['name']))
                )

    def on_close(self):
        logging.info("WebSocket %s closed" % self.uid)
        if self.uid in self.application.wsPool:
            del self.application.wsPool[self.uid]


def signal_term_handler(sig, _):
    logging.error("Got %s. Quit.", sig)
    exit(0)


if __name__ == '__main__':
    signal(SIGTERM, signal_term_handler)
    app = Application([
        (r"/websocket", Handler),
        (r"/profiles", Profiles),
        (r"/()", StaticFileHandler, {'path': 'static/index.html'}),
        (r"/(.+)", StaticFileHandler, {'path': 'static/'}),
    ])
    try:
        ioloop = IOLoop.instance()
        app.db = Pool(dsn="dbname=mol user=mol password=molpassword "
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
