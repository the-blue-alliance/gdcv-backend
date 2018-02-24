import datetime
import json
import logging
from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from db_provider import DbProvider
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider
from queue import Queue


class FrcRealtimeWorker(object):
    def __init__(self, metadata: MetadataProvider, cv_provider: CvProvider,
                 apiv3_provider: ApiV3Provider, media: MediaProvider,
                 db: DbProvider, pubsub: PubSubProvider):
        self.metadata = metadata
        self.cv_provider = cv_provider
        self.apiv3 = apiv3_provider
        self.media = media
        self.db = db
        self.pubsub = pubsub

    def process_message(self, message_data: str):
        message = json.loads(message_data)
        message_type = message["type"]
        logging.info("Processing message type: {}".format(message_type))
        if message_type == 'exit':
            return True
        elif message_type == 'test':
            logging.info("Got test message: {}".format(message["message"]))
        elif message_type == 'process_match':
            match_key = message["match_key"]
            video_id = message["video_id"]
            self._process_match_video(match_key, video_id)
        elif message_type == 'process_event':
            event_key = message["event_key"]
            self._process_event_videos(event_key)
        logging.info("message processing complete")
        return False

    def _process_match_video(self, match_key: str, video_id: str):
        logging.info("Loading data for match {}".format(match_key))
        match = self.apiv3.fetch_match_details(match_key)
        year = int(match_key[:4])
        if not match['actual_time']:
            logging.error("Unable to find actual_time for match")
            return Nonefetch_match_details
        start_time = datetime.datetime.utcfromtimestamp(match['actual_time'])
        logging.info("Match started at {} UTC".format(start_time))
        frame_queue = Queue()
        logging.info("Processing video id {}".format(video_id))
        self.media.fetch_youtube_video(video_id, frame_queue, 500)
        db_rows = self.cv_provider.process_frame_queue(year, match_key,
                                                       start_time, frame_queue)
        logging.info("Inserting {} rows into the DB".format(len(db_rows)))
        with self.db.session() as session:
            for row in db_rows:
                session.add(row)

    def _process_event_videos(self, event_key: str):
        logging.info("Loading matches for event {}".format(event_key))
        matches = self.apiv3.fetch_event_matches(event_key)

        # If we're running with more than one instance, support enqueueing
        # each match individual to pubsub so they can run in parallel
        should_fanout = self.metadata.get('fanout_event_videos', False)
        match_key = match["key"]
        video_id = match["videos"][0]  # TODO validation
        if should_fanout:
            for match in matches:
                logging.info("Enqueueing match {} to pubsub".format(
                    match["key"]))
                message = {
                    'type': 'process_match',
                    'match_key': match_key,
                    'video_id': video_id,
                }
                self.pubsub.push(json.dumps(message))
        else:
            for match in matches:
                self._process_match_video(match_key, video_id)
