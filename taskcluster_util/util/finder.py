# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import logging

import taskcluster


log = logging.getLogger(__name__)


class TaskFinder(object):
    def __init__(self, options):
        # ref: http://docs.taskcluster.net/services/index/
        self.index = taskcluster.Index(options)

    def get_taskid_by_namespace(self, namespace):
        if namespace is None or namespace is "":
            return None

        # format {'data':..., 'expires':..., 'namespace':..., 'rank':..., 'taskId':...}
        ret = self.index.findTask(namespace)
        return ret['taskId']
