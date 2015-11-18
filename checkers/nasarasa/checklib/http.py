import checklib
import logging
import requests


def build_main_url(fn):
    def wrapper(self, address, *args, **kwargs):
        self.main_url = 'http://%s' % address
        fn(self, address, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    wrapper.__doc__ = fn.__doc__
    return wrapper


class HttpChecker(checklib.Checker):
    def __init__(self):
        super().__init__()
        logging.info('Created requests session')
        self._session = requests.Session()

    def _check_response(self, response):
        if response.status_code >= 400:
            self.exit(checklib.StatusCode.DOWN, 'Got HTTP status code %d on %s' % (response.status_code, response.url))
        if response.status_code != 200:
            self.exit(checklib.StatusCode.MUMBLE, 'Got HTTP status code %d on %s' % (response.status_code, response.url))        
        return response

    def try_http_get(self, url, *args, **kwargs):
        return self._check_response(self._session.get(url, *args, **kwargs))

    def try_http_post(self, url, *args, **kwargs):
        return self._check_response(self._session.post(url, *args, **kwargs))

    def check_page_content(self, response, strings_for_check, failed_message=None):
        message = 'Invalid page content at %url'
        if failed_message != None:
            message += ': ' + failed_message
        if '%url' in message:
            message = message.replace('%url', response.url)

        for s in strings_for_check:
            self.mumble_if_false(s in response.text, message, 'Can\'t find string "%s" in response from %s' % (s, response.url))

        