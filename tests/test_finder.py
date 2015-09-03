# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import textwrap
import unittest
from mock import patch, Mock
from taskcluster_util.util.finder import TaskFinder


class FinderTester(unittest.TestCase):

    def test_get_parent_namespace(self):
        """
        test get_parent_namespace
        """
        f = TaskFinder()
        expected_ret = 'foo'
        ret = f.get_parent_namespace('foo.bar')
        self.assertEqual(ret, expected_ret)

        expected_ret = ''
        ret = f.get_parent_namespace('root')
        self.assertEqual(ret, expected_ret)

        expected_ret = 'root.foo.bar.test_v1.moz'
        ret = f.get_parent_namespace('root.foo.bar.test_v1.moz.node')
        self.assertEqual(ret, expected_ret)

    def test_get_namespaces(self):
        """
        test get_namespaces
        """
        expected_ret = [u'foo.test', u'foo.v1', u'foo.bar']

        with patch('taskcluster.Index') as MockClass:
            instance = MockClass.return_value
            instance.listNamespaces.return_value = {u'namespaces': [{u'expires': u'2016-03-30T00:00:00.000Z', u'namespace': u'foo.test', u'name': u'test'}, {u'expires': u'2016-08-31T00:00:00.000Z', u'namespace': u'foo.v1', u'name': u'v1'}, {u'expires': u'2016-08-31T00:00:00.000Z', u'namespace': u'foo.bar', u'name': u'bar'}]}

            f = TaskFinder()
            ret = f.get_namespaces('foo')
            self.assertEqual(ret, expected_ret)

    def test_get_tasks(self):
        """
        test get_tasks
        """
        expected_ret = [(u'foo', u'bar')]
        with patch('taskcluster.Index') as MockClass:
            instance = MockClass.return_value
            instance.listTasks.return_value = {u'tasks': [{u'data': {u'test': u'data'}, u'expires': u'2015-09-09T19:19:15.879Z', u'namespace': u'foo', u'rank': 1, u'taskId': u'bar'}]}

            f = TaskFinder()
            ret = f.get_tasks('foo')
            self.assertEqual(ret, expected_ret)

    def test_get_namespaces_and_tasks(self):
        """
        test get_namespaces_and_tasks
        """
        expected_ret = {'node': 'foo', 'tasks': [(u'foo', u'bar')], 'namespaces': [u'foo.test', u'foo.v1', u'foo.bar']}

        with patch('taskcluster.Index') as MockClass:
            instance = MockClass.return_value
            instance.listNamespaces.return_value = {u'namespaces': [{u'expires': u'2016-03-30T00:00:00.000Z', u'namespace': u'foo.test', u'name': u'test'}, {u'expires': u'2016-08-31T00:00:00.000Z', u'namespace': u'foo.v1', u'name': u'v1'}, {u'expires': u'2016-08-31T00:00:00.000Z', u'namespace': u'foo.bar', u'name': u'bar'}]}
            instance.listTasks.return_value = {u'tasks': [{u'data': {u'test': u'data'}, u'expires': u'2015-09-09T19:19:15.879Z', u'namespace': u'foo', u'rank': 1, u'taskId': u'bar'}]}

            f = TaskFinder()
            ret = f.get_namespaces_and_tasks('foo')
            self.assertEqual(ret, expected_ret)

    def test_get_taskid_by_namespace(self):
        """
        test get_taskid_by_namespace
        """
        expected_ret = u'foobar_taskid'

        with patch('taskcluster.Index') as MockClass:
            instance = MockClass.return_value
            instance.findTask.return_value = {u'data': {}, u'expires': u'2016-08-30T20:26:07.196Z', u'namespace': u'foo', u'rank': 999, u'taskId': u'foobar_taskid'}

            f = TaskFinder()
            ret = f.get_taskid_by_namespace('foo')
            self.assertEqual(ret, expected_ret)


if __name__ == '__main__':
    unittest.main()
