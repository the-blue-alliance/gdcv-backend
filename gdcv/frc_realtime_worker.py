import datetime
import json
import logging
from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from db_provider import DbProvider
from firebase_provider import FirebaseProvider
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider
from queue import Queue


class FrcRealtimeWorker(object):
    def __init__(self, metadata: MetadataProvider, cv_provider: CvProvider,
                 apiv3_provider: ApiV3Provider, media: MediaProvider,
                 db: DbProvider, pubsub: PubSubProvider, firebase: FirebaseProvider):
        self.metadata = metadata
        self.cv_provider = cv_provider
        self.apiv3 = apiv3_provider
        self.media = media
        self.db = db
        self.pubsub = pubsub
        self.firebase = firebase

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
        elif message_type == 'process_stream':
            stream_url = message["stream_url"]
            event_key = message["event_key"]
            self._process_stream(event_key, stream_url)
        logging.info("message processing complete")
        return False

    def _process_stream(self, event_key: str, stream_utl: str):
        self.media.process_twitch_stream(event_key, stream_url,
                                         self._live_frame_callback)

    def _live_frame_callback(self, event_key, image):
        if image is None:
            self.firebase.clear_data_in_firebase(event_key)
            return
        details = self.cv_provider.process_live_frame(event_key)
        self.firebase.push_data_to_firebase(details, event_key)
        with self.db.session() as session:
            session.add(details)

    def _process_match_video(self, match_key: str, video_id: str=None):
        logging.info("Loading data for match {}".format(match_key))
        match = self.apiv3.fetch_match_details(match_key)
        year = int(match_key[:4])
        if not match['actual_time']:
            logging.error("Unable to find actual_time for match")
            return Nonefetch_match_details
        start_time = datetime.datetime.utcfromtimestamp(match['actual_time'])
        if not video_id and match["videos"]:
            video_id = match["videos"][0]["key"]
            logging.info("Using video id {} from apiv3".format(video_id))
        elif not match["videos"]:
            logging.warning("No videos found, skipping...")
            return
        logging.info("Match started at {} UTC".format(start_time))
        frame_queue = Queue()
        logging.info("Processing video id {}".format(video_id))
        self.media.fetch_youtube_video(video_id, frame_queue, 10)
        db_rows = self.cv_provider.process_frame_queue(year, match_key,
                                                       start_time, frame_queue)
        logging.info("Inserting {} rows into the DB".format(len(db_rows)))
        with self.db.session() as session:
            for row in db_rows:
                session.add(row)

    def _process_event_videos(self, event_key: str):
        logging.info("Loading matches for event {}".format(event_key))
        matches = self.apiv3.fetch_event_matches(event_key)
        logging.info("Found {} matches".format(len(matches)))

        # TODO should be able to enqueue each match individually to run in parallel

        for match in matches:
            logging.info("Processing {}".format(match["key"]))
            self._process_match_video(match["key"])
