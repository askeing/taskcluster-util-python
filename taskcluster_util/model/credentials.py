import json
import logging
import datetime


logger = logging.getLogger(__name__)


class Credentials(dict):
    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)
        # We don't follow PEP8 here because we only pass this object as a JSON
        self.clientId = kwargs['clientId']
        self.accessToken = kwargs['accessToken']

        try:
            self.certificate = kwargs['certificate']
            self.is_expired()
        except KeyError:
            logger.warning('''No certificate is present in the given credentials. If the credentials are temporary you won't be able to download anything''')

    def __getitem__(self, item):
        value = dict.__getitem__(self, item)
        # The taskcluster client always expects each argument of the Credentials to be a string,
        # even for the certificate. To let the user copy and paste the certificate directly from
        # https://auth.taskcluster.net/ without escaping all the quotes, we perform this change
        # of type.
        return self._enforce_string(value)

    def is_expired(self):
        if self.certificate:
            try:
                expiry_timestamp = self.certificate.get('expiry')
                if len(str(expiry_timestamp)) == 13:
                    expiry_timestamp = int(str(expiry_timestamp)[0:-3])
                expiry = datetime.datetime.fromtimestamp(expiry_timestamp)
                now = datetime.datetime.now()
                if now > expiry:
                    logger.warning('Temporary credentials expired!!!')
                    return True
                else:
                    logger.info('Temporary credentials will expire on {}/{}/{} {}:{}.'
                                .format(expiry.year, expiry.month, expiry.day, expiry.hour, expiry.minute))
                    return False
            except Exception as e:
                logger.debug(e)

    @staticmethod
    def from_file(file_path):
        with open(file_path) as fd:
            credentials = json.load(fd)
        return Credentials(**credentials)

    @staticmethod
    def _enforce_string(value):
        return value if type(value) in (str, unicode) else json.dumps(value, ensure_ascii=True)
