#!/usr/bin/env python
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import logging
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

    def __init__(self, connection_options={}):
        self.connection_options = connection_options
        self.dest_dir = None

    def cli(self):
        """
        Handle the argument parse, and the return the instance itself.
        """
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
        parser.add_argument('-n', '--namespace', action='store', dest='namespace', default='', help='The namespace of task')
        parser.add_argument('-d', '--dest-dir', action='store', dest='dest_dir', help='The dest folder (default: current working folder)')
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
        # check credentials file
        try:
            abs_credentials_path = os.path.abspath(self.options.credentials)
            credentials = Credentials.from_file(abs_credentials_path)
            self.connection_options = {'credentials': credentials}
        except Exception as e:
            logger.debug(e)
        # assign the variable
        self.entry_namespace = self.options.namespace
        self.dest_dir = self.options.dest_dir
        return self

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
            if task_name:
                msg = 'Please select the artifacts you want to download.\n\nTask Name: [{}]\nTask ID: [{}]'.format(task_name, task_id)
            else:
                msg = 'Please select the artifacts you want to download.\n\nTask ID: [{}]'.format(task_id)
            title = 'Select Artifacts'
            return easygui.multchoicebox(msg, title, choices)
        except Exception as e:
            title = 'Exception'
            easygui.msgbox(e, title)
            return []

    def gui_select_namespaces(self, current_namespace, sub_namespace_list):
        """
        GUI: select the namespace.
        @param current_namespace: the current namespace's name.
        @param sub_namespace_list: the list of sub-namespace under current namespace.
        """
        choices = sub_namespace_list
        msg = 'Please select the namespace.\n\nCurrent Namespace: [{}]'.format(current_namespace)
        title = 'Select Namespace'
        return easygui.choicebox(msg, title, choices)

    def _check_target_dir(self, dest_dir):
        """
        GUI: show GUI for selecting the target folder when there is no given "--dest-dir" argument.
        @param dest_dir: the target folder from cli.
        """
        if not dest_dir:
            title = 'Select Target Folder'
            return easygui.diropenbox(title=title, default=os.getcwd())

    def _check_credentials(self):
        """
        GUI: show GUI for entering the credentials when there is no credentials.
        """
        if not self.connection_options:
            msg = 'Please enter your credentials for downloading.\nOr you can put tc_credentials.json file under your current folder.\ne.g. {"credentials": {"clientId": "XXX", "accessToken": "XXX" ...}}'
            title = 'Enter Credentials'
            ret = easygui.enterbox(msg, title)
            try:
                self.connection_options = json.loads(ret)
                logger.debug('connection options: {}'.format(self.connection_options))
            except:
                self.connection_options = {}
                logger.debug('Can not load connection options from user input.')
                easygui.msgbox('Can not load connection options from user input.\nRun with no connection options.')

    def gui_download_artifacts(self, task_name, task_id):
        """
        GUI: select artifacts for downloading.
        @param task_name: the task name.
        @param task_id: the TaskId.
        """
        choice_artifact_list = self.gui_select_artifacts(task_name, task_id)
        if choice_artifact_list:
            self._check_target_dir(self.dest_dir)
            for item in choice_artifact_list:
                logger.info('Download: {}'.format(item))
                local_file = self.artifact_downloader.download_latest_artifact(task_id, item, self.dest_dir)
            easygui.msgbox('Download Finished.')

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
