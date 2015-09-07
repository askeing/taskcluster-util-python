#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import textwrap
from argparse import RawTextHelpFormatter
import json

import easygui
from util.finder import *
from util.downloader import *
from model.credentials import Credentials

logger = logging.getLogger(__name__)


class TraverseRunner(object):
    _PARENT_NODE = '..'
    _TYPE_NAMESPACE = '[NS]'
    _TYPE_TASK = '[TASK]'

    def __init__(self, connection_options=None):
        if not connection_options:
            connection_options = {}
        self.connection_options = connection_options
        self.dest_dir = None
        self.entry_namespace = ''
        self.downloaded_file_list = []
        self.task_finder = None
        self.artifact_downloader = None

    def cli(self):
        """
        Handle the argument parse, and the return the instance itself.
        """
        # argument parser
        taskcluster_credentials = 'tc_credentials.json'
        parser = argparse.ArgumentParser(prog='taskcluster_traverse',
                                         description='The simple GUI traverse and download tool for Taskcluster.',
                                         formatter_class=RawTextHelpFormatter,
                                         epilog=textwrap.dedent('''\
                                         The tc_credentials.json Template:
                                             {
                                                 "clientId": "",
                                                 "accessToken": ""
                                             }
                                         '''))
        parser.add_argument('--credentials', action='store', default=taskcluster_credentials, dest='credentials',
                            help='The credential JSON file (default: {})'.format(taskcluster_credentials))
        parser.add_argument('-n', '--namespace', action='store', dest='namespace', default='',
                            help='The namespace of task')
        parser.add_argument('-d', '--dest-dir', action='store', dest='dest_dir',
                            help='The dest folder (default: current working folder)')
        parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                            help='Turn on verbose output, with all the debug logger.')

        # parser the argv
        options = parser.parse_args(sys.argv[1:])
        # setup the logging config
        if options.verbose is True:
            verbose_formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            logging.basicConfig(level=logging.DEBUG, format=verbose_formatter)
        else:
            formatter = '%(levelname)s: %(message)s'
            logging.basicConfig(level=logging.INFO, format=formatter)
        # check credentials file
        try:
            abs_credentials_path = os.path.abspath(options.credentials)
            credentials = Credentials.from_file(abs_credentials_path)
            self.connection_options = {'credentials': credentials}
        except Exception as e:
            logger.warning('No connection options.')
            logger.debug(e)
        # assign the variable
        self.entry_namespace = options.namespace
        self.dest_dir = options.dest_dir
        return self

    def _check_target_dir(self):
        """
        GUI: show GUI for selecting the target folder when there is no given "--dest-dir" argument.
        """
        if not self.dest_dir:
            title = 'Select Target Folder'
            self.dest_dir = easygui.diropenbox(title=title, default=os.getcwd())

    def _check_credentials(self):
        """
        GUI: show GUI for entering the credentials when there is no credentials.
        """
        if not self.connection_options:
            title = 'Enter Credentials'
            msg = textwrap.dedent('''\
            Please enter your Credentials for downloading.
            Or you can put it in "<CURRENT_DIR>/tc_credentials.json" file.

            e.g. {"clientId": "XXX", "accessToken": "XXX" ...}

            * Tips: [←][→] Move, [Enter] Select, [Esc] Cancel
            ''')
            ret = easygui.enterbox(msg, title)
            try:
                raw_credentials_dict = json.loads(ret)
                if 'credentials' in raw_credentials_dict:
                    self.connection_options = raw_credentials_dict
                elif 'clientId' in raw_credentials_dict:
                    self.connection_options = {'credentials': raw_credentials_dict}
                logger.debug('connection options: {}'.format(self.connection_options))
            except Exception as e:
                logger.debug(e)
                self.connection_options = {}
                logger.debug('Can not load connection options from user input.')
                title = 'Load Options Error'
                msg = textwrap.dedent('''\
                Can not load Credentials from user input.
                Run with no credentials.

                * Tips: [Enter] OK
                ''')
                easygui.msgbox(msg, title)

    def _get_entry_namespace(self):
        """
        If entry_namespace is task, show GUI for downloading and return parent namespace.
        """
        if self.task_finder.is_task(self.entry_namespace):
            task_name = self.entry_namespace
            task_id = self.task_finder.get_taskid_by_namespace(task_name)
            parent = self.task_finder.get_parent_namespace(task_name)
            self.gui_download_artifacts(task_name, task_id)
            return parent
        else:
            return self.entry_namespace

    def _get_latest_artifacts(self, task_id):
        """
        Return the latest artifacts name list
        """
        logger.debug('Getting latest artifacts of TaskID {} ...'.format(task_id))
        ret = self.artifact_downloader.get_latest_artifacts(task_id)
        artifacts_list = ret.get('artifacts')
        artifacts_name_list = []
        for artifact in artifacts_list:
            artifacts_name_list.append(artifact.get('name'))
        logger.debug('artifact list: {}'.format(artifacts_name_list))
        return artifacts_name_list

    def gui_select_artifacts(self, task_name='', task_id=''):
        """
        GUI: select the artifacts. (multiple)
        @param task_name: the task name.
        @param task_id: the task id.
        @return: list of selections.
        """
        try:
            choices = self._get_latest_artifacts(task_id)
            title = 'Select Artifacts'
            if task_name:
                msg = textwrap.dedent('''\
                Please select the artifacts you want to download.

                - Task Name: [{}]
                - Task ID: [{}]

                * Tips: [↑][↓] Move, [Space] Select, [Enter] OK
                ''').format(task_name, task_id)
            else:
                msg = textwrap.dedent('''\
                Please select the artifacts you want to download.

                - Task ID: [{}]

                * Tips: [↑][↓] Move, [Space] Select, [Enter] OK, [Esc] Cancel
                ''').format(task_id)
            return easygui.multchoicebox(msg, title, choices)
        except Exception as e:
            title = 'Exception'
            msg = textwrap.dedent('''\
            Error: [{}] [{}]

            Exception: {}

            * Tips: [Enter] OK
            ''').format(task_name, task_id, e)
            easygui.msgbox(msg, title)
            return []

    @staticmethod
    def gui_select_namespaces(current_namespace, sub_namespace_list):
        """
        GUI: select the namespace.
        @param current_namespace: the current namespace's name.
        @param sub_namespace_list: the list of sub-namespace under current namespace.
        """
        choices = sub_namespace_list
        msg = textwrap.dedent('''\
        Please select the namespace.

        - Current Namespace: [{}]

        * Tips: [↑][↓] Select, [Enter] OK, [Esc] Cancel
        ''').format(current_namespace)
        title = 'Select Namespace'
        return easygui.choicebox(msg, title, choices)

    def gui_download_artifacts(self, task_name, task_id):
        """
        GUI: select artifacts for downloading.
        @param task_name: the task name.
        @param task_id: the TaskId.
        """
        choice_artifact_list = self.gui_select_artifacts(task_name, task_id)
        if choice_artifact_list:
            # if there is no target dir, then show gui for user
            self._check_target_dir()
            if self.dest_dir:
                self.downloaded_file_list = []
                # after user select the dir, download artifacts
                for item in choice_artifact_list:
                    logger.info('Download: {}'.format(item))
                    try:
                        local_file = self.artifact_downloader.download_latest_artifact(task_id, item, self.dest_dir)
                        self.downloaded_file_list.append(local_file)
                    except Exception as e:
                        title = 'Download Failed'
                        msg = textwrap.dedent('''\
                        Can not download: [{}]

                        Exception: {}

                        * Tips: [Enter] OK
                        ''').format(item, e)
                        easygui.msgbox(msg, title)
                self.do_after_download()
            else:
                # if user cancel the selection of dir, stop download.
                title = 'Cancel'
                msg = textwrap.dedent('''\
                Cancel.

                Would you like to continue traversing?

                * Tips: [←][→] Move, [Enter] Select, [Esc] No
                ''')
                user_choice = easygui.ynbox(msg, title)
                if not user_choice:
                    exit(0)

    def do_after_download(self):
        """
        Do something after downloading finished.
        """
        for f in self.downloaded_file_list:
            logger.debug('Download {}'.format(f))
        title = 'Download'
        msg = textwrap.dedent('''\
        Finished.

        Would you like to continue traversing?

        * Tips: [←][→] Move, [Enter] Select, [Esc] No
        ''')
        user_choice = easygui.ynbox(msg, title)
        if not user_choice:
            exit(0)

    def run(self):
        """
        Entry point.
        """
        # check the credentials for Taskcluster
        self._check_credentials()
        # prepare the utilies
        self.task_finder = TaskFinder(self.connection_options)
        self.artifact_downloader = Downloader(self.connection_options)
        # traverse the Taskcluster
        current_node = self._get_entry_namespace()
        while True:
            ret_ns_task_dict = self.task_finder.get_namespaces_and_tasks(current_node)
            ns_task_list = []
            # namespace format = "namespace FOO.BAR"
            for item in ret_ns_task_dict.get(TaskFinder._NAMESPACES):
                ns_task_list.append('{} {}'.format(self._TYPE_NAMESPACE, item))
            # task format = "task FOO.BAR.TASK TASKID"
            for item in ret_ns_task_dict.get(TaskFinder._TASKS):
                ns_task_list.append('{} {} {}'.format(self._TYPE_TASK, item[0], item[1]))
            # append the ".." for going back to parent
            if not self.task_finder.is_root(current_node):
                ns_task_list.append(TraverseRunner._PARENT_NODE)
            # user choice namespace
            user_choice = self.gui_select_namespaces(current_node, ns_task_list)
            logger.debug('Select: {}'.format(user_choice))
            # Cancel, then break
            if not user_choice:
                logger.debug('Break')
                break
            # Go to parent
            elif user_choice == TraverseRunner._PARENT_NODE:
                current_node = self.task_finder.get_parent_namespace(current_node)
                logger.debug('Change current node to: {}'.format(current_node))
            # Namespace
            else:
                # 'namespace Foo.Bar' or 'task Foo.Task TaskId'
                choice_info = user_choice.split()
                logger.debug('Split user choice: {}'.format(choice_info))
                # go to next namespace if select namespace
                if choice_info[0] == self._TYPE_NAMESPACE:
                    current_node = choice_info[1]
                    logger.debug('Change current node to: {}'.format(current_node))
                # stay at current namespace if select task, open artifacts list
                elif choice_info[0] == self._TYPE_TASK:
                    task_name = choice_info[1]
                    task_id = choice_info[2]
                    logger.debug('Selcet Task: {}, TaskId: {}'.format(task_name, task_id))
                    # select downloading artifacts
                    self.gui_download_artifacts(task_name, task_id)


def main():
    try:
        TraverseRunner().cli().run()
    except Exception as e:
        logger.error(e)
        if e.__dict__:
            logger.error(e.__dict__)
        exit(1)


if __name__ == '__main__':
    main()
