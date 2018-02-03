import logging
import time

from cv_provider import CvProvider
from db.test import Test
from db_provider import DbProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider

class FrcRealtimeScoringServiceHandler(object):

    def __init__(self, version: str, metadata: MetadataProvider,
                 pubsub: PubSubProvider, db: DbProvider, cv: CvProvider):
        self.alive = int(time.time())
        self.counters = {}
        self.version = version
        self.metadata = metadata
        self.pubsub = pubsub
        self.db = db
        self.cv = cv

    def getName(self):
        logging.debug("getName() called")
        return "FrcRealtimeScoringServiceHandler"

    def getVersion(self):
        logging.debug("getVersion() called")
        return self.version

    def aliveSince(self):
        logging.debug("aliveSince() called")
        return self.alive

    def getStatus(self):
        logging.debug("getStatus() called")
        return "RUNNING"

    def getMetadataValue(self, key):
        # Hit the local metadata server and get the value for this key
        logging.debug("getMetadataValue() called for key {}".format(key))
        return self.metadata.get(key)

    def sendPubSubMessage(self, message):
        logging.debug(
            "sendPubSubMessage() called with message{}".format(
                message))
        result = self.pubsub.push(message)
        return result.result()

    def getPubSubMessage(self):
        logging.debug("getPubSubMessage() called")
        return self.pubsub.getNextMessage()

    def insertTestRow(self, text):
        logging.debug("insertTestRow({}) called".format(text))
        test = Test(text=text)
        with self.db.session() as session:
            logging.info("Inserting test row with data: {}".format(test))
            session.add(test)

    def getAllTestMessages(self):
        logging.debug("getAllTestMessages() called")
        with self.db.session() as session:
            all_tests = session.query(Test).all()
            return ','.join(map(lambda test: test.text, all_tests))
        return ""

    def clearAllTestMessages(self):
        logging.debug("clearAllTestMessages() called")
        with self.db.session() as session:
            logging.info("clearing all test messages")
            session.query(Test).delete()

    def processTestImage(self):
        logging.debug("processTestImage() called")
        return self.cv.process_test_image()
