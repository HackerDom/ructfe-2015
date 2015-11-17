#!/usr/bin/env python3
# coding=utf-8
from random import randrange, shuffle, choice
from hashlib import sha1
from time import time
from urllib.error import URLError as http_error
from urllib.request import urlopen
from urllib.parse import urlencode
from sys import argv, stderr
from subprocess import check_output

__author__ = 'm_messiah, crassirostris'

OK, GET_ERROR, CORRUPT, FAIL, INTERNAL_ERROR = 101, 102, 103, 104, 110

NAMES_FILENAME = 'names.txt'
MAX_PAGE_SIZE = 1024 * 1024

def close(code, public="", private=""):
    if public:
        print(public)
    if private:
        print(private, file=stderr)
    exit(code)

def calc_checksum(account_name, amount):
    return check_output("LD_LIBRARY_PATH=./validator/dict ./validator/validator '%s' %d"
        % (account_name, amount), shell=True).decode("utf-8").strip()

def create_name():
    with open(NAMES_FILENAME, 'r') as f:
        lines = f.readlines()
    return " ".join([ choice(lines).strip() for e in range(3) ])

def create_account_name():
    return "The main account of thouself"

class CheckerException(Exception):
    """Custom checker error"""
    def __init__(self, msg):
        super(CheckerException, self).__init__(msg)

class Client(object):
    def __init__(self, addr):
        self.addr = addr

    def login(self, login):
        return self.open_and_check_ok('account.cgi?' + urlencode({'login': login}))

    def create_account(self, login, account, amount):
        return self.open_and_check_ok('add_money.cgi?' +
            urlencode({"login": login, "account": account, "amount": amount}))

    def make_transfer(self, login, account, login_to, account_to, amount):
        return self.open_and_check_ok('transfer_money.cgi?' +
            urlencode({"login": login, "account": account, "amount": amount,
                "login_to": login_to, "account_to": account_to}))

    def open_and_check_ok(self, path, data = None):
        url = "http://%s/%s" % (self.addr, path)
        if isinstance(data, str):
            data = data.encode("utf-8")
        response = urlopen(url, data)
        if response.getcode() != 200:
            raise CheckerException("Recieved status %d on request %s"
                % (response.getcode(), response.geturl()))
        return response.read(MAX_PAGE_SIZE).decode('utf-8')

    def encode_user_data(self):
        return urlencode({'Login': self.user[0], 'Pass': self.user[1]})


def check(*args):
    addr = args[0]
    c = Client(addr)
    try:
        name_1, name_2 = create_name(), create_name()
        account_name_1, account_name_2 = create_account_name(), create_account_name()
        amount_1, amount_2 = randrange(1, 100500), randrange(1, 100500)
        transfer_amount = randrange(1, amount_1)

        page = c.login(name_1)
        c.create_account(name_1, account_name_1, amount_1)
        if not calc_checksum(account_name_1, amount_1) in c.login(name_1):
            close(CORRUPT, "Checksum validation failed")

        c.login(name_2)
        c.create_account(name_2, account_name_2, amount_2)
        if not calc_checksum(account_name_2, amount_2) in c.login(name_2):
            close(CORRUPT, "Checksum validation failed")

        c.make_transfer(name_1, account_name_1, name_2, account_name_2, transfer_amount)
        if not str(transfer_amount + amount_2) in c.login(name_2):
            raise CheckerException("Failed to transfer money at '%s'" % addr)
        close(OK)
    except http_error as e:
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


def put(*args):
    addr = args[0]
    flag_id = args[1]
    flag = args[2]
    c = Client(addr)
    try:
        name = create_name()
        c.login(name)
        c.create_account(name, flag, randrange(1, 100500))
        close(OK, name)
    except http_error as e:
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


def get(*args):
    addr = args[0]
    checker_flag_id = args[1]
    flag = args[2]
    c = Client(addr)
    try:
        name = checker_flag_id
        page = c.login(name)
        if flag in page:
            close(OK)
        close(GET_ERROR)
    except http_error as e:
        close(FAIL, "HTTP Error", "HTTP error sending to '%s': %s" % (addr, e))
    except CheckerException as e:
        close(CORRUPT, "Service did not work as expected", "Checker exception: %s" % e)
    except Exception as e:
        close(INTERNAL_ERROR, "Unknown error", "Unknown error: %s" % e)


def info(*args):
    close(OK, "vulns: 1")


COMMANDS = {'check': check, 'put': put, 'get': get, 'info': info}


def not_found(*args):
    print("Unsupported command %s" % argv[1], file=stderr)
    return INTERNAL_ERROR


if __name__ == '__main__':
    try:
        COMMANDS.get(argv[1], not_found)(*argv[2:])
    except Exception as e:
        close(INTERNAL_ERROR, "Sweet and cute checker =3", "INTERNAL ERROR: %s" % e)