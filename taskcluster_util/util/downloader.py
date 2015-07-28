# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import shutil
import logging
import tempfile

import taskcluster


log = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, options):
        self.temp_dir = tempfile.mkdtemp()
        self.queue = taskcluster.Queue(options)

    def get_latest_artifacts(self, task_id):
        ret = self.queue.listLatestArtifacts(task_id)
        return ret

    def download_latest_artifact(self, task_id, full_filename, dest_dir):
        base_filename = os.path.basename(full_filename)

        ret = self.queue.getLatestArtifact(task_id, full_filename)
        response = ret.get('response')

        total_length = 0
        content_length = response.headers.get('content-length')
        if content_length is not None:
            total_length = int(content_length)

        chunk_size = 1024
        current_size = 0
        # download file into temp folder
        temp_local_file = os.path.join(self.temp_dir, base_filename)
        with open(temp_local_file, 'wb') as fd:
            for chunk in response.iter_content(chunk_size):
                current_size = current_size + len(chunk)
                fd.write(chunk)
                if total_length > 0:
                    progress = int((50 * current_size) / total_length)
                    if progress <= 50:
                        sys.stdout.write('\r[%s%s] %s/%s' % ('#' * progress, ' ' * (50 - progress), str(current_size), str(total_length)))
                        sys.stdout.flush()
                    else:
                        sys.stdout.write('\r[%s] %s/%s' % ('#' * 50, str(current_size), str(total_length)))
                        sys.stdout.flush()
        sys.stdout.write('\nDone.\n\n')
        sys.stdout.flush()

        # move file to dest folder
        abs_dest_dir = os.path.abspath(dest_dir)
        log.debug('dest dir: {}'.format(abs_dest_dir))
        if os.path.exists(abs_dest_dir) and (not os.path.isdir(abs_dest_dir)):
            log.warning('Not a directory: {}'.format(abs_dest_dir))
            final_file_path = os.path.abspath(temp_local_file)
            log.debug('local file: {}'.format(final_file_path))
        else:
            if not os.path.exists(abs_dest_dir):
                os.makedirs(abs_dest_dir)
            shutil.copy(temp_local_file, abs_dest_dir)
            final_file_path = os.path.join(abs_dest_dir, base_filename)
            log.debug('local file: {}'.format(final_file_path))

        # remove temp folder
        try:
            shutil.rmtree(self.temp_dir)  # delete directory
        except OSError:
            log.warning('Can not remove temporary folder: {}'.format(self.temp_dir))

        return final_file_path
