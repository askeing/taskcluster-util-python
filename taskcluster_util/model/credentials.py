import json

class Credentials(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        # We don't follow PEP8 here because we only pass this object as a JSON
        self.clientId = kwargs['clientId']
        self.accessToken = kwargs['accessToken']

        try:
            self.certificate = kwargs['certificate']
        except KeyError:
            # TODO: Replace by log.warning once the loggers works.
            print '''Warning: no certificate is present in the given credentials. If the credentials are temporary you won't be able to download anything'''

    @staticmethod
    def from_file(file_path):
        with open(file_path) as fd:
            credentials = json.load(fd)
        return Credentials(**credentials)
