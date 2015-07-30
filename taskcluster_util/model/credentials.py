import json
import logging


logger = logging.getLogger(__name__)


class Credentials(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        # We don't follow PEP8 here because we only pass this object as a JSON
        self.clientId = kwargs['clientId']
        self.accessToken = kwargs['accessToken']

        try:
            self.certificate = kwargs['certificate']
        except KeyError:
            logger.warning('''No certificate is present in the given credentials. If the credentials are temporary you won't be able to download anything''')

    def __getitem__(self, item):
        value = dict.__getitem__(self, item)
        # The taskcluster client always expects each argument of the Credentials to be a string,
        # even for the certificate. To let the user copy and paste the certificate directly from
        # https://auth.taskcluster.net/ without escaping all the quotes, we perform this change
        # of type.
        return self._enforce_string(value)

    @staticmethod
    def from_file(file_path):
        with open(file_path) as fd:
            credentials = json.load(fd)
        return Credentials(**credentials)

    @staticmethod
    def _enforce_string(value):
        return value if type(value) in (str, unicode) else json.dumps(value, ensure_ascii=True)
