import enum
import logging
import sys
import traceback
import requests


class StatusCode(enum.Enum):
    OK = 101
    CORRUPT = 102
    MUMBLE = 103
    DOWN = 104
    ERROR = 110

    def __str__(self):
        return "%s (%d)" % (self._name_, self.value)


class exception_wrapper:
    def __init__(self, code):
        self.exit_code = code

    def __call__(self, fn):
        code = self.exit_code
        def wrapper(self, *args, **kwargs):
            try:
                fn(self, *args, **kwargs)
            except Exception as e:
                logging.info('Catched exception: %s', e)
                logging.exception(e)

                if isinstance(e, requests.exceptions.RequestException):
                    logging.debug('It\'s `requests` module exception')

                self.exit(code, str(e))
            else:
                self.exit(StatusCode.OK)
        return wrapper


class Checker:
    def __init__(self):
        logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s', level=logging.DEBUG)

    def check(self, address):
        raise CheckerException('Not implemented')

    def put(self, address, flag_id, flag, vuln):
        raise CheckerException('Not implemented')

    def get(self):
        raise CheckerException('Not implemented')

    def info(self):
        raise CheckerException('Not implemented')

    def exit(self, code, message=''):
        if message != '':
            logging.info('Exit with code %s and message "%s"', code, message)
            print(message)
        else:
            logging.info('Exit with code %s', code)

        sys.exit(code.value)

    def mumble_if_false(self, statement, public_message='Invalid content', private_message=''):
        if not statement:
            if private_message != '':
                logging.error(private_message)
            self.exit(StatusCode.MUMBLE, public_message)

    @exception_wrapper(StatusCode.DOWN)
    def run_command(self, function, arguments):
        if len(arguments) == 0:
            logging.info('Run "%s" without arguments', function.__name__)
        else:
            logging.info('Run "%s" with arguments %s', function.__name__, arguments)
        function(*arguments)

    @exception_wrapper(StatusCode.ERROR)
    def run(self, command='', address='', flag_id='', flag='', vuln_id='1', *args):
        vuln_id = int(vuln_id)
        commands = {'info':  {'method': self.info,  'arguments': []},
                    'check': {'method': self.check, 'arguments': [address]},
                    'put':   {'method': self.put,   'arguments': [address, flag_id, flag, vuln_id]},
                    'get':   {'method': self.get,   'arguments': [address, flag_id, flag, vuln_id]}
                   }

        if command not in commands:
            self.exit(StatusCode.ERROR, 'Invalid command: %s' % command)

        self.run_command(commands[command]['method'], commands[command]['arguments'])


class CheckerException(Exception):
    pass