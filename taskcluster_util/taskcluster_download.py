#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import logging
import argparse
import textwrap
from argparse import RawTextHelpFormatter

from util.finder import *
from util.downloader import *
from taskcluster.exceptions import TaskclusterAuthFailure, TaskclusterRestFailure
from model.credentials import Credentials


logger = logging.getLogger(__name__)


class DownloadRunner(object):

    def __init__(self):
        # argument parser
        taskcluster_credentials = 'tc_credentials.json'
        parser = argparse.ArgumentParser(prog='taskcluster_download', description='The simple download tool for Taskcluster.',
                                         formatter_class=RawTextHelpFormatter,
                                         epilog=textwrap.dedent('''\
                                         The tc_credentials.json Template:
                                             {
                                                 "clientId": "",
                                                 "accessToken": ""
                                             }
                                         '''))
        parser.add_argument('--credentials', action='store', default=taskcluster_credentials, dest='credentials', help='The credential JSON file (default: {})'.format(taskcluster_credentials))
        task_group = parser.add_mutually_exclusive_group(required=True)
        task_group.add_argument('-n', '--namespace', action='store', dest='namespace', help='The namespace of task')
        task_group.add_argument('-t', '--taskid', action='store', dest='task_id', help='The taskId of task')
        artifact_group = parser.add_argument_group('Download Artifact', 'The artifact name and dest folder')
        artifact_group.add_argument('-a', '--artifact', action='store', dest='aritfact_name', help='The artifact name on Taskcluster')
        artifact_group.add_argument('-d', '--dest-dir', action='store', dest='dest_dir', help='The dest folder (default: current working folder)')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Turn on verbose output, with all the debug logger.')

        # parser the argv
        self.options = parser.parse_args(sys.argv[1:])
        # setup the logging config
        if self.options.verbose is True:
            verbose_formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(level=logging.DEBUG, format=verbose_formatter)
        else:
            formatter = '%(levelname)s: %(message)s'
            logging.basicConfig(level=logging.INFO, format=formatter)

    def show_latest_artifacts(self, artifact_downloader, task_id):
        logger.info('Getting latest artifacts of TaskID {} ...'.format(task_id))
        ret = artifact_downloader.get_latest_artifacts(task_id)
        artifacts_list = ret.get('artifacts')
        width = 30
        print('{}| {}'.format('[Type]'.ljust(width), '[Name]'.ljust(width)))
        for artifact in artifacts_list:
            print('{}| {}'.format(artifact.get('contentType').ljust(width), artifact.get('name').ljust(width)))

    def run(self):
        # check credentials file
        abs_credentials_path = os.path.abspath(self.options.credentials)

        credentials = Credentials.from_file(abs_credentials_path)
        connection_options = {'credentials': credentials}

        if self.options.namespace is not None:
            # remove the 'index.' and 'root.' of namespace
            task_namespace = self.options.namespace
            logger.info('Finding the TaskID of Namespace [{}] ...'.format(task_namespace))
            if self.options.namespace.startswith('index.'):
                task_namespace = self.options.namespace[len('index.'):]
                logger.info('Remove the ["index."] of Namespace [{}].'.format(task_namespace))
            elif self.options.namespace.startswith('root.'):
                task_namespace = self.options.namespace[len('root.'):]
                logger.info('Remove the ["root."] of Namespace [{}].'.format(task_namespace))
            # find TaskId from Namespace
            task_finder = TaskFinder(connection_options)
            task_id = task_finder.get_taskid_by_namespace(task_namespace)
            logger.info('The TaskID of Namespace [{}] is [{}].'.format(task_namespace, task_id))
        else:
            task_id = self.options.task_id

        artifact_downloader = Downloader(connection_options)
        if self.options.aritfact_name is None:
            # no artifact_name, then get the latest artifacts list
            self.show_latest_artifacts(artifact_downloader, task_id)
        else:
            # has artifact_name, then download it
            logger.info('Downloading latest artifact [{}] of TaskID [{}] ...'.format(self.options.aritfact_name, task_id))
            local_file = artifact_downloader.download_latest_artifact(task_id, self.options.aritfact_name, self.options.dest_dir)
            logger.info('Download [{}] from TaskID [{}] to [{}] done.'.format(self.options.aritfact_name, task_id, local_file))


def main():
    try:
        DownloadRunner().run()
    except Exception as e:
        logger.error(e)
        if e.__dict__:
            logger.error(e.__dict__)
        exit(1)


if __name__ == '__main__':
    main()
