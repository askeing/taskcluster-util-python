# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

import taskcluster


logger = logging.getLogger(__name__)


class TaskFinder(object):
    _NODE = 'node'
    _NAMESPACES = 'namespaces'
    _TASKS = 'tasks'
    _LIMIT = 'limit'
    _CONTINUATION_TOKEN = 'continuationToken'
    _NAMESPACE = 'namespace'
    _TASK = 'task'
    _TASK_ID = 'taskId'

    def __init__(self, options={}):
        """
        Ref: U{http://docs.taskcluster.net/services/index/}
        """
        self.index = taskcluster.Index(options)

    def is_root(self, ns_node):
        """
        Check the namespace is root node or not.
        For now, the root node is "".
        @param ns_node: given namespace.
        @return: True if it is root, False if not.
        """
        if not ns_node:
            return True
        return False

    def is_task(self, namespace):
        """
        Check the given namespace is task or it's a namespace.
        @param namespace: the given namespace.
        @return: True if it's task. False if it's namespace.
        """
        try:
            # if it's a task
            self.index.findTask(namespace)
            return True
        except:
            # except if it's not task
            return False

    def get_taskid_by_namespace(self, namespace):
        """
        Get the TaskId of task.
        @param namespace: the namespace of Task.
        @return: the TaskId of Task.
        """
        if namespace is None or namespace is "":
            return None
        # format {'data':..., 'expires':..., 'namespace':..., 'rank':..., 'taskId':...}
        ret = self.index.findTask(namespace)
        return ret['taskId']

    def get_parent_namespace(self, ns_node=''):
        """
        Get the parent namespace of given namepsace.
        @param ns_node: given namespace.
        @return: Return the parent namespace. Return itself when given namespace is root node.
        """
        ret = ns_node.split('.')
        if len(ret) > 1:
            ret = ret[:len(ret) - 1]
        elif len(ret) == 1:
            ret = ''
        return '.'.join(ret)

    def get_namespaces(self, ns_node='', limit=1000):
        """
        Get the namespaces of given namespace.
        @param ns_node: given namespace.
        @param limit: 1-1000, the return list of API up to 1000 namespace per-call.
        @return: return the namespaces list. e.g. [NAME, ...]
        """
        result_list = []
        continuationToken = None
        try:
            while True:
                # prepare payload
                payload = {TaskFinder._LIMIT: limit}
                if continuationToken:
                    payload[TaskFinder._CONTINUATION_TOKEN] = continuationToken
                # query API
                ret = self.index.listNamespaces(ns_node, payload)
                for item in ret.get(TaskFinder._NAMESPACES):
                    if item.get(TaskFinder._NAMESPACE) != '':
                        result_list.append(item.get(TaskFinder._NAMESPACE))
                # if there is continuationToken, then query API agian with token.
                if not ret.get(TaskFinder._CONTINUATION_TOKEN):
                    break
                else:
                    continuationToken = ret.get(TaskFinder._CONTINUATION_TOKEN)
        except Exception as e:
            logger.debug(e)
        return result_list

    def get_tasks(self, ns_node='', limit=1000):
        """
        Get the tasks of given namespace.
        @param ns_node: given namespace.
        @param limit: 1-1000, the return list of API up to 1000 namespace per-call.
        @return: return the tasks list. e.g. [(NAME, TASK_ID), ...]
        """
        result_list = []
        continuationToken = None
        try:
            while True:
                # prepare payload
                payload = {TaskFinder._LIMIT: limit}
                if continuationToken:
                    payload[TaskFinder._CONTINUATION_TOKEN] = continuationToken
                # query API
                ret = self.index.listTasks(ns_node, payload)
                for item in ret.get(TaskFinder._TASKS):
                    if item.get(TaskFinder._TASK) != '':
                        result_list.append((item.get(TaskFinder._NAMESPACE), item.get(TaskFinder._TASK_ID)))
                # if there is continuationToken, then query API agian with token.
                if not ret.get(TaskFinder._CONTINUATION_TOKEN):
                    break
                else:
                    continuationToken = ret.get(TaskFinder._CONTINUATION_TOKEN)
        except Exception as e:
            logger.debug(e)
        return result_list

    def get_namespaces_and_tasks(self, ns_node='', limit=1000):
        """
        Get the namespaces and tasks of given namespace.
        @param ns_node: given namespace.
        @param limit: 1-1000, the return list of API up to 1000 namespace per-call.
        @return: return the namespaces and tasks dict. e.g. {'node': 'foo', 'tasks': [('tname', 'tid'), ...], 'namespaces': ['n1', 'n2', ...]}
        """
        result = {TaskFinder._NODE: ns_node}
        # get namespaces
        result[TaskFinder._NAMESPACES] = self.get_namespaces(ns_node, limit)
        # get tasks
        result[TaskFinder._TASKS] = self.get_tasks(ns_node, limit)
        return result
