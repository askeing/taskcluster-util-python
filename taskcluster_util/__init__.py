# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

""" Taskcluster Utilities """

import logging
import os
from util import *

log = logging.getLogger(__name__)

if os.environ.get('DEBUG_TASKCLUSTER_UTILITIES'):
    log.setLevel(logging.DEBUG)
    if len(log.handlers) == 0:
        log.addHandler(logging.StreamHandler())
log.addHandler(logging.NullHandler())
