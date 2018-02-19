import logging
import requests
from metadata_provider import MetadataProvider

class ApiV3Provider(object):

    BASE_URL = 'https://www.thebluealliance.com/api/v3/{}'

    def __init__(self, metadata: MetadataProvider):
        self.metadata = metadata

    def _get_auth_key(self):
        return self.metadata.get('apiv3_auth_key')

    def fetch_match_details(self, match_key):
        auth_key = self._get_auth_key()
        if not auth_key:
            logging.error("No apiv3 auth key found")
            return None
        url = self.BASE_URL.format('match/{}'.format(match_key))
        logging.debug("Making apiv3 request: {}".format(url))
        r = requests.get(url, headers={'X-TBA-Auth-Key': auth_key})
        return r.json()
