#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import textwrap
from argparse import RawTextHelpFormatter

from util.finder import *
from util.downloader import *
from model.credentials import Credentials
from model.login_policy import LOGGING_POLICY

logger = logging.getLogger(__name__)


class DownloadRunner(object):
    def __init__(self, connection_options=None):
        """
        @param connection_options: the options argument for connection. e.g. {'credentials': ...}
        """
        if not connection_options:
            connection_options = {}
        self.connection_options = connection_options
        self.namespace = None
        self.task_id = None
        self.artifact_name = None
        self.dest_dir = None
        self.artifact_downloader = None
        self.taskcluster_credentials = os.path.join(os.path.expanduser('~'), 'tc_credentials.json')
        self.should_display_signed_url_only = False
        self.is_verbose = False

    def parser(self):
        # argument parser
        parser = argparse.ArgumentParser(prog='taskcluster_download',
                                         description='The simple download tool for Taskcluster.',
                                         formatter_class=RawTextHelpFormatter,
                                         epilog=textwrap.dedent('''\
                                         The tc_credentials.json Template:
                                             {
                                                 "clientId": "",
                                                 "accessToken": "",
                                                 "certificate": {
                                                     "version":1,
                                                     "scopes":["*"],
                                                     "start":xxx,
                                                     "expiry":xxx,
                                                     "seed":"xxx",
                                                     "signature":"xxx"
                                                 }
                                             }
                                         '''))
        parser.add_argument('--credentials', action='store', default=self.taskcluster_credentials, dest='credentials',
                            help='The credential JSON file\n(default: {})'.format(self.taskcluster_credentials))
        task_group = parser.add_mutually_exclusive_group(required=True)
        task_group.add_argument('-n', '--namespace', action='store', dest='namespace', help='The namespace of task')
        task_group.add_argument('-t', '--taskid', action='store', dest='task_id', help='The taskId of task')
        artifact_group = parser.add_argument_group('Download Artifact', 'The artifact name and dest folder')
        artifact_group.add_argument('-a', '--artifact', action='store', dest='aritfact_name',
                                    help='The artifact name on Taskcluster')
        artifact_group.add_argument('-d', '--dest-dir', action='store', dest='dest_dir',
                                    help='The dest folder (default: current working folder)')
        artifact_group.add_argument('-u', '--signed-url-only', action='store_true', help='Retrieve the signed url and display it.\nNo download is done.')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                            help='Turn on verbose output, with all the debug logger.')
        return parser.parse_args(sys.argv[1:])

    def cli(self):
        """
        This method will parse the argument for CLI.
        """
        # parser the argv
        options = self.parser()

        self.namespace = options.namespace
        self.task_id = options.task_id
        self.artifact_name = options.aritfact_name
        self.dest_dir = options.dest_dir
        self.is_verbose = options.verbose
        self.should_display_signed_url_only = options.signed_url_only

        self._configure_login()
        self._check_crendentials_file(options)
        return self

    def _configure_login(self):
        if self.is_verbose is True:
            logging_config = LOGGING_POLICY['verbose']
        elif self.should_display_signed_url_only is True:
            logging_config = LOGGING_POLICY['no_logs']
        else:
            logging_config = LOGGING_POLICY['default']
        logging.basicConfig(level=logging_config['level'], format=logging_config['format'])

    def _check_crendentials_file(self, options):
        try:
            abs_credentials_path = os.path.abspath(options.credentials)
            credentials = Credentials.from_file(abs_credentials_path)
            self.connection_options = {'credentials': credentials}
            logger.info('Load Credentials from {}'.format(abs_credentials_path))
        except Exception as e:
            if os.path.isfile(abs_credentials_path):
                logger.error('Please check your credentials file: {}'.format(abs_credentials_path))
                raise e
            else:
                logger.warning('No credentials. Run with "--help" for more information.')
                logger.debug(e)

    def show_latest_artifacts(self, task_id):
        """
        Print the artifacts by given TaskId.
        @param task_id: the given TaskId.
        """
        logger.info('Getting latest artifacts of TaskID {} ...'.format(task_id))
        ret = self.artifact_downloader.get_latest_artifacts(task_id)
        artifacts_list = ret.get('artifacts')
        width = 30
        print('{}| {}'.format('[Type]'.ljust(width), '[Name]'.ljust(width)))
        for artifact in artifacts_list:
            print('{}| {}'.format(artifact.get('contentType').ljust(width), artifact.get('name').ljust(width)))

    def run(self):
        """
        Run the download process.
        """
        if self.namespace is not None:
            # remove the 'index.' and 'root.' of namespace
            task_namespace = self.namespace
            logger.info('Finding the TaskID of Namespace [{}] ...'.format(task_namespace))
            if self.namespace.startswith('index.'):
                task_namespace = self.namespace[len('index.'):]
                logger.info('Remove the ["index."] of Namespace [{}].'.format(task_namespace))
            elif self.namespace.startswith('root.'):
                task_namespace = self.namespace[len('root.'):]
                logger.info('Remove the ["root."] of Namespace [{}].'.format(task_namespace))
            # find TaskId from Namespace
            task_finder = TaskFinder(self.connection_options)
            task_id = task_finder.get_taskid_by_namespace(task_namespace)
            logger.info('The TaskID of Namespace [{}] is [{}].'.format(task_namespace, task_id))
        else:
            task_id = self.task_id

        self.artifact_downloader = Downloader(self.connection_options)
        if self.artifact_name is None:
            # no artifact_name, then get the latest artifacts list
            self.show_latest_artifacts(task_id)
        elif self.should_display_signed_url_only is True:
            print self.artifact_downloader.get_signed_url(task_id, self.artifact_name)
        else:
            # has artifact_name, then download it
            logger.info('Downloading latest artifact [{}] of TaskID [{}] ...'.format(self.artifact_name, task_id))
            local_file = self.artifact_downloader.download_latest_artifact(task_id, self.artifact_name, self.dest_dir)
            logger.info('Download [{}] from TaskID [{}] to [{}] done.'.format(self.artifact_name, task_id, local_file))


def main():
    try:
        DownloadRunner().cli().run()
    except Exception as e:
        logger.error(e)
        if e.__dict__:
            logger.error(e.__dict__)
        exit(1)


if __name__ == '__main__':
    main()
