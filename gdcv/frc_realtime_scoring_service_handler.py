import logging
import time
import json

from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from datetime import datetime
from db.match_state_2017 import MatchState2017
from db.test import Test
from db_provider import DbProvider
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider
from queue import Queue

class FrcRealtimeScoringServiceHandler(object):
    def __init__(self, version: str, thrift, metadata: MetadataProvider,
                 pubsub: PubSubProvider, db: DbProvider, cv: CvProvider,
                 media: MediaProvider, apiv3: ApiV3Provider):
        self.alive = int(time.time())
        self.counters = {}
        self.version = version
        self.thrift = thrift
        self.metadata = metadata
        self.pubsub = pubsub
        self.db = db
        self.cv = cv
        self.media = media
        self.apiv3 = apiv3

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

    def enqueueSingleMatch(self, req):
        logging.debug("enqueueSingleMatch() called for {}".format(req))
        self.db.deleteMatchData(req.matchKey)
        message_data = {
            'type': 'process_match',
            'match_key': req.matchKey,
            'video_id': req.videoKey ,
        }
        self.pubsub.push(json.dumps(message_data))
        resp = self.thrift.EnqueueProcessResponse()
        resp.success = True
        resp.message = "request enqueued!"
        return resp

    def enqueueEvent(self, req):
        self.db.deleteEventData(req.eventKey)
        message_data = {
            'type': 'process_event',
            'event_key': req.eventKey,
        }
        self.pubsub.push(json.dumps(message_data))
        resp = self.thrift.EnqueueProcessResponse()
        resp.success = True
        resp.message = "request enqueued!"
        return resp

    def blockUntilNotProcessing(self):
        while self.pubsub.current_message is not None:
            time.sleep(1)

    def getMetadataValue(self, key):
        # Hit the local metadata server and get the value for this key
        logging.debug("getMetadataValue() called for key {}".format(key))
        return self.metadata.get(key)

    def sendPubSubMessage(self, message):
        logging.debug(
            "sendPubSubMessage() called with message{}".format(
                message))
        message = {
            'type': 'test',
            'message': message,
        }
        result = self.pubsub.push(json.dumps(message))
        return result.result()

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
