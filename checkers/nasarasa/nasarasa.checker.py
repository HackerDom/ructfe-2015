#!/usr/bin/env python3

import requests
import sys
import checklib


class NasaRasaChecker(checklib.Checker):
    def info(self):
        print('vulns: 1')
        self.exit(checklib.StatusCode.OK)

    def check(self, address):
        main_url = 'http://' + address

        r = self.try_get(main_url)

    def put(self, address, flag_id, flag, vuln):
        pass

    def get(self, address, flag_id, flag, vuln):
        pass

    def try_get(self, url):
        r = requests.get(url)
        if r.status_code >= 400:
            self.exit(checklib.StatusCode.DOWN, 'Got HTTP status code %d on %s' % (r.status_code, url))
        if r.status_code != 200:
            self.exit(checklib.StatusCode.MUMBLE, 'Got HTTP status code %d on %s' % (r.status_code, url))
        return r

if __name__ == '__main__':
    NasaRasaChecker().run(*sys.argv[1:])
