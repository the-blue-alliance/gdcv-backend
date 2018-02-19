import logging
import time

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

    def processYoutubeVideo(self, req):
        logging.debug("processYoutubeVideo() called for {}".format(req))
        resp = self.thrift.ProcessYoutubeVideoResp()
        with self.db.session() as session:
            logging.info("clearing all 2017 match data")
            session.query(MatchState2017).delete()
        logging.info("Loading data for match {}".format(req.matchKey))
        match = self.apiv3.fetch_match_details(req.matchKey)
        if not match['actual_time']:
            logging.error("Unable to find actual_time for match")
            resp.success = False
            resp.message = "Unable to find actual_time for match"
            return resp
        start_time = datetime.utcfromtimestamp(match['actual_time'])
        logging.info("Match started at {} UTC".format(start_time))
        frame_queue = Queue()
        logging.info("Processing video id {}".format(req.videoKey))
        self.media.fetch_youtube_video(req.videoKey, frame_queue, 500)
        db_rows = self.cv.process_frame_queue(req.year, req.matchKey,
                                              start_time, frame_queue)
        logging.info("Inserting {} rows into the DB".format(len(db_rows)))
        with self.db.session() as session:
            for row in db_rows:
                session.add(row)
        resp.success = True
        resp.message = "success!"
        return resp

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
