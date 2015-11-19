#!/usr/bin/env python3

import collections
import json
import logging
import requests
import re
import sys
import string

import checklib.http
import checklib.random


class DictedModel:
    def as_dict(self, keys=None):
        result = dict(zip(self._fields, list(self)))
        if keys != None:
            {k: v for k, v in result.items() if k in keys}
        return result


class User(collections.namedtuple('User', ['login', 'password', 'first_name', 'last_name']), DictedModel):
    @staticmethod
    def generate_random():
        login = checklib.random.string(string.ascii_lowercase, range(10, 20), first_uppercase=True)
        password = checklib.random.string(string.ascii_letters + string.digits, range(10, 20))
        first_name = checklib.random.firstname()
        last_name = checklib.random.lastname()

        return User(login, password, first_name, last_name)

    @property
    def fullname(self):
        return '%s %s' % (self.first_name, self.last_name)


class Planet(collections.namedtuple('Planet', ['declination', 'hour_angle', 'brightness', 'size', 'color', 'message']), DictedModel):
    @staticmethod
    def generate_random(**kwargs):
        declination = checklib.random.integer(range(-90, 91))
        hour_angle = checklib.random.integer(range(-12, 13))
        brightness = checklib.random.integer(range(0, 101))
        size = checklib.random.integer(range(0, 101))
        color = checklib.random.color()
        message = kwargs.get('message', checklib.random.string(string.ascii_lowercase, range(10, 20)))

        return Planet(declination, hour_angle, brightness, size, color, message) 


class NasaRasaChecker(checklib.http.HttpChecker):
    def info(self):
        print('vulns: 1')
        self.exit(checklib.StatusCode.OK)

    def check_main_page_content(self, r, logged=False):
        self.check_page_content(r, ['Report us information about unknown planet and it\'ll be named after you.',
                                    'Hackerdom team, hackerdom.ru, Andrew Gein aka andgein',
                                    '/static/logos/nasarasa.png',
                                   ])
        if logged:
            self.check_page_content(r, ['Let us know about unknown planet',
                                        'Size (from 0 to 100)',
                                        'Any message which will be visible only for you and site administrators',
                                       ])


    def check_main_page(self):
        logging.info('Checking main page')
        self.check_main_page_content(self.try_http_get(self.main_url))

    def check_users_page(self):
        logging.info('Checking users page')
        r = self.try_http_get(self.main_url + '/users')
        self.check_page_content(r, ['Last registered users',
                                    'NASA RASA',
                                    'system for reporting information about found planets',
                                    '<div class="last-users">',
                                   ])
        return r

    def try_signup(self):
        user = User.generate_random()

        logging.info('Try to signup user: %s', user)
        self.check_main_page_content(self.try_http_post(self.main_url + '/signup', data=user.as_dict()),
                                     logged=True)
        
        logging.info('Try to find just registereg user on `users` page by fullname: %s', user.fullname)
        r = self.try_http_get(self.main_url + '/users')
        self.check_page_content(r, [user.fullname], 'can\'t find just registered user')
        logging.info('Successfully found!')

        return user

    def try_signin(self, user):
        logging.info('Try to signin as user: %s', user)
        r = self.try_http_post(self.main_url + '/signin', data=user.as_dict(['login', 'password']))
        if r.url.endswith('/signin'):
            logging.error('Can\'t signin as user: %s', user)
            self.exit(checklib.StatusCode.CORRUPT, 'Can\'t signin as registered user')
        self.check_main_page_content(r, logged=True)

    def try_report_planet(self, message=None):
        planet = Planet.generate_random(message=message)

        logging.info('Are you ready?! We\'re putting flag now!')
        logging.info('Try to report information about planet: %s', planet)
        r = self.try_http_post(self.main_url + '/report', data=planet.as_dict())

        self.check_page_content(r, ['Information has been successfully added, thank you! You can see it on your'])
        logging.info('Information about planet has been reported successfully')

        return planet

    def find_user_link(self):
        r = self.try_http_get(self.main_url)
        
        cursor = 'You\'re logged in as '
        self.check_page_content(r, [cursor])
        position = r.text.find(cursor)
        text_part = r.text[position:position + 100]
        logging.info('Try to find user_link in "%s"', text_part)
        
        user_link_re = re.compile('(/users/\d+)')
        matches = user_link_re.findall(text_part)

        if len(matches) == 0:
            logging.info('Not found :-(')
            self.exit(checklib.StatusCode.MUMBLE, 'Can\'t find link to my profile page on %s' % self.main_url)

        user_link = self.main_url + matches[0]
        logging.info('Found: %s', user_link)
        return user_link


    @checklib.http.build_main_url
    def check(self, address):
        self.check_main_page()
        self.check_users_page()

    @checklib.http.build_main_url
    def put(self, address, flag_id, flag, vuln):
        user = self.try_signup()
        planet = self.try_report_planet(flag)

        logging.info('Now I print flag_id to STDOUT. My flag_id is serialized user')
        flag_id = json.dumps(user.as_dict())
        print(flag_id)

    @checklib.http.build_main_url
    def get(self, address, flag_id, flag, vuln):
        try:
            user = User(**json.loads(flag_id))
        except Exception as e:
            logging.error('Can\'t extract user from flag_id:')
            logging.exception(e)
            self.exit(checklib.StatusCode.ERROR)

        logging.info('Extracted user from flag_id: %s', user)
        
        self.try_signin(user)
        my_user_link = self.find_user_link()
        
        logging.info('Looking for login on user\'s page')
        r = self.try_http_get(my_user_link)
        self.check_page_content(r, [user.login])

        logging.info('Looking for flag on user\'s page')
        found = flag in r.text
        if found:
            logging.info('I found flag on user\'s page: %s', flag)
        else:
            logging.info('I can\'t found flag on user\'s page')
            self.exit(checklib.StatusCode.CORRUPT, 'Can\'t find flag in private planet\'s info')


if __name__ == '__main__':
    NasaRasaChecker().run(*sys.argv[1:])
