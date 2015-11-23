#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import json
import shutil
import urllib
import logging
import argparse
import threading
import webbrowser
from argparse import ArgumentDefaultsHelpFormatter
from urlparse import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from model.login_policy import LOGGING_POLICY


logger = logging.getLogger(__name__)


def _yesno(path):
    choice = raw_input('Do you want to delete {}? [Y/n]'.format(path)).lower()
    if choice == 'n':
        print('Stop login.')
        exit(0)


def _remove_exist_file(file_path):
    abs_file_path = os.path.abspath(file_path)
    try:
        if os.path.isdir(abs_file_path):
            _yesno(abs_file_path)
            logger.info('Remove folder: {}'.format(abs_file_path))
            shutil.rmtree(abs_file_path)
        elif os.path.isfile(abs_file_path):
            _yesno(abs_file_path)
            logger.info('Remove file: {}'.format(abs_file_path))
            os.remove(abs_file_path)
    except Exception as e:
        if os.path.exists(abs_file_path):
            logger.error('Please check: {}'.format(abs_file_path))
            raise e


class LoginBot(object):
    def __init__(self):
        self.server = None
        self.address = 'localhost'
        self.port = 0
        self.credentials_file = os.path.join(os.path.expanduser('~'), 'tc_credentials.json')
        self.is_verbose = False

    def parse(self):
        # argument parser
        parser = argparse.ArgumentParser(description='The simple login tool for Taskcluster.',
                                         formatter_class=ArgumentDefaultsHelpFormatter)
        parser.add_argument('-a', '--address', action='store', default='localhost', dest='address',
                            help='Specify the server address.')
        parser.add_argument('-p', '--port', action='store', type=int, default=0, dest='port',
                            help='Specify the server port.')
        parser.add_argument('--file', action='store', default=self.credentials_file, dest='credentials_file',
                            help='The credentials file. It will be overwritten if it already exist.')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                            help='Turn on verbose output, with all the debug logger.')
        return parser.parse_args(sys.argv[1:])

    def _configure_login(self):
        if self.is_verbose is True:
            logging_config = LOGGING_POLICY['verbose']
        else:
            logging_config = LOGGING_POLICY['default']
        logging.basicConfig(level=logging_config['level'], format=logging_config['format'])

    def cli(self):
        options = self.parse()
        self.address = options.address
        self.port = options.port
        self.credentials_file = options.credentials_file
        global credentials_file
        credentials_file = self.credentials_file
        self.is_verbose = options.verbose

        self._configure_login()
        _remove_exist_file(self.credentials_file)
        return self

    class ServerHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            logger.debug('======= GET STARTED =======')
            logger.debug(self.headers)
            # get parameters
            query = urlparse(self.path).query
            query_components = {}
            for query_item in query.split('&'):
                k, v = query_item.split('=')
                if k == 'certificate':
                    certificate = json.loads(urllib.unquote(v).decode('utf-8'))
                    query_components[k] = certificate
                else:
                    query_components[k] = v
            logger.debug('GET Parameters: {}'.format(query_components))
            # write to file
            logger.info('Write credentials to {}'.format(credentials_file))
            with open(credentials_file, mode='w') as f:
                json.dump(query_components, f, indent=4)
            # response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<h1>Login Successful</h1><br>You can close this window now...')
            # stop server
            logger.debug('======= Stop Server =======')
            assassin = threading.Thread(target=self.server.shutdown)
            assassin.daemon = True
            assassin.start()

        def log_message(self, format, *args):
            return

    def run(self):
        try:
            self.server = HTTPServer((self.address, self.port), self.ServerHandler)
            server_addr, server_port = self.server.socket.getsockname()
            # TODO: now only can send server address as localhost.
            print('Started server for listening credentials on {}:{}'.format(self.address, server_port))
            print('Press ^C will stop server')
            # open broswer
            params = {'target': 'http://{}:{}'.format(self.address, server_port),
                      'description': '`taskcluster_login` will save the credentials in `{}`.'.format(credentials_file)}
            urllib.urlencode(params)
            webbrowser.open_new('https://auth.taskcluster.net/?{}'.format(urllib.urlencode(params)))
            # listening
            self.server.serve_forever()

        except KeyboardInterrupt:
            print('^C received, shutdown server')
            self.server.socket.close()


def main():
    try:
        LoginBot().cli().run()
    except Exception as e:
        logger.error(e)
        if e.__dict__:
            logger.error(e.__dict__)
        exit(1)


if __name__ == '__main__':
    main()
