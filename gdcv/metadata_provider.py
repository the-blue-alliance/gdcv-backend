import requests

class MetadataProvider(object):

    def get(self, key):
        url = "http://metadata.google.internal/computeMetadata/v1/project/attributes/{}".format(key)
        r = requests.get(url, headers={"Metadata-Flavor": "Google"})
        return r.content
