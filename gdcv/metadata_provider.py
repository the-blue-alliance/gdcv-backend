import logging
import requests

class MetadataProvider(object):

    def get(self, key, default=None):
        url = "http://metadata.google.internal/computeMetadata/v1/project/attributes/{}".format(key)
        r = requests.get(url, headers={"Metadata-Flavor": "Google"})
        if r.status_code == 404:
            return default
        elif r.status_code != 200:
            raise Exception("Error fetching metadata key {}: {}".format(
                key, r.content))
        return r.content

    def getInstance(self, key, default=None):
        url = "http://metadata.google.internal/computeMetadata/v1/instance/attributes/{}".format(key)
        r = requests.get(url, headers={"Metadata-Flavor": "Google"})
        if r.status_code == 404:
            return default
        elif r.status_code != 200:
            raise Exception("Error fetching metadata key {}: {}".format(
                key, r.content))
        return r.content
