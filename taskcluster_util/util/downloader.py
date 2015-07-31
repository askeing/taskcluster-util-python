# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys
import shutil
import logging
import tempfile

import taskcluster


logger = logging.getLogger(__name__)


class Downloader(object):
    def __init__(self, options):
        self.temp_dir = tempfile.mkdtemp(prefix='tmp_tcdl_')
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
        final_file_path = temp_local_file
        abs_dest_dir = os.path.abspath(dest_dir) if dest_dir else os.getcwd()
        try:
            FolderHandler(abs_dest_dir).copy_elements_from(temp_local_file)
            final_file_path = os.path.join(abs_dest_dir, base_filename)
            # remove temp folder
            try:
                shutil.rmtree(self.temp_dir)  # delete directory
            except OSError:
                logger.warning('Can not remove temporary folder: {}'.format(self.temp_dir))
        except Exception as e:
            logger.error(e.message)
            logger.debug('local file: [{}]'.format(temp_local_file))

        return final_file_path


class FolderHandler:
    def __init__(self, path):
        self.path = path
        self._check_if_folder_is_valid()

    def _check_if_folder_is_valid(self):
        if not os.path.exists(self.path):
            logger.debug("[{}] doesn't exist, trying to create it".format(self.path))
            self._create_folder()
        if not os.path.isdir(self.path):
            raise Exception('[{}] is not a folder.'.format(self.path))
        if not os.access(self.path, os.W_OK):
            raise Exception('Write permission denied on [{}].'.format(self.path))

    def _create_folder(self):
        try:
            os.makedirs(self.path)
        except os.error as e:
            logger.debug('errno: [{}], strerror: [{}], filename: [{}]'.format(e.errno, e.strerror, e.filename))
            raise Exception('Can not create the folder: [{}]'.format(self.path))

    def copy_elements_from(self, origin):
        shutil.copy(origin, self.path)
