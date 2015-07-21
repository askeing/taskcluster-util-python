#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import json
import shutil
import logging
import argparse

from util.finder import *
from util.downloader import *
from taskcluster.exceptions import TaskclusterAuthFailure, TaskclusterRestFailure


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class DownloadRunner(object):

    def __init__(self):
        # argument parser
        parser = argparse.ArgumentParser(prog='taskcluster_download', description='The simple download tool for Taskcluster.')
        parser.add_argument('--credential', action='store', default='credential.json', dest='credential', help='The credential JSON file (default: credential.json)')
        task_group = parser.add_mutually_exclusive_group(required=True)
        task_group.add_argument('-n', '--namespace', action='store', dest='namespace', help='The namespace of task')
        task_group.add_argument('-t', '--taskid', action='store', dest='task_id', help='The taskId of task')
        artifact_group = parser.add_argument_group('Download Artifact', 'The artifact name and dest folder')
        artifact_group.add_argument('-a', '--artifact', action='store', dest='aritfact_name', help='The artifact name on Taskcluster')
        artifact_group.add_argument('-d', '--dest-dir', action='store', dest='dest_dir', help='The dest folder')

        # parser the argv
        self.options = parser.parse_args(sys.argv[1:])

    def show_latest_artifacts(self, artifact_downloader, task_id):
        print('### Getting latest artifacts of TaskID {} ...'.format(task_id))
        ret = artifact_downloader.get_latest_artifacts(task_id)
        artifacts_list = ret.get('artifacts')
        width = 30
        print('### {}| {}'.format('[Type]'.ljust(width), '[Name]'.ljust(width)))
        for artifact in artifacts_list:
            print('### {}| {}'.format(artifact.get('contentType').ljust(width), artifact.get('name').ljust(width)))

    def run(self):
        # check credential file
        abs_credential_path = os.path.abspath(self.options.credential)
        if not os.path.isfile(abs_credential_path):
            print('### {} is not a file or is not exist.\n'.format(abs_credential_path))
            exit(-1)
        with open(abs_credential_path) as fd:
            json_string = fd.read()
            credential = json.loads(json_string)
            client_id = credential.get('clientId')
            access_token = credential.get('accessToken')
            certificate = credential.get('certificate')
            print certificate

        if self.options.namespace is not None:
            # remove the 'index.' and 'root.' of namespace
            task_namespace = self.options.namespace
            print('### Finding the TaskID of Namespace [{}] ...'.format(task_namespace))
            if self.options.namespace.startswith('index.'):
                task_namespace = self.options.namespace[len('index.'):]
                print('### Remove the ["index."] of Namespace [{}].'.format(task_namespace))
            elif self.options.namespace.startswith('root.'):
                task_namespace = self.options.namespace[len('root.'):]
                print('### Remove the ["root."] of Namespace [{}].'.format(task_namespace))
            # find TaskId from Namespace
            task_finder = TaskFinder(client_id, access_token)
            try:
                task_id = task_finder.get_taskid_by_namespace(task_namespace)
                print('### The TaskID of Namespace [{}] is [{}].'.format(task_namespace, task_id))
            except TaskclusterRestFailure as e:
                print('### Can not get the TaskID due to [{}]'.format(e.message))
                log.error(e.body)
                exit(-1)
        else:
            task_id = self.options.task_id

        artifact_downloader = Downloader(client_id, access_token, certificate)
        if self.options.aritfact_name is None and self.options.dest_dir is None:
            # no artifact_ and dest_dir, then get the latest artifacts list
            self.show_latest_artifacts(artifact_downloader, task_id)
        elif self.options.aritfact_name is None or self.options.dest_dir is None:
            # if one of artifact_name and dest_dir is specified, return error
            print('### Please specify the artifact name and dest folder at the same time.\n')
            exit(-1)
        else:
            # has artifact_name and dest_dir, then download it
            abs_dest_dir = os.path.abspath(self.options.dest_dir)
            if os.path.exists(abs_dest_dir) and (not os.path.isdir(abs_dest_dir)):
                print('### {} is not a folder.\n'.format(abs_dest_dir))
                exit(-1)
            print('### Downloading latest artifact [{}] of TaskID [{}] ...'.format(self.options.aritfact_name, task_id))
            try:
                local_file = artifact_downloader.download_latest_artifact(task_id, self.options.aritfact_name, abs_dest_dir)
            except (TaskclusterAuthFailure, TaskclusterRestFailure) as e:
                print('### Can not download due to [{}]'.format(e.message))
                log.error(e.body)
                exit(-1)
            print('### Download [{}] from TaskID [{}] to [{}] done.'.format(self.options.aritfact_name, task_id, local_file))


def main():
    myapp = DownloadRunner()
    myapp.run()


if __name__ == '__main__':
    main()
