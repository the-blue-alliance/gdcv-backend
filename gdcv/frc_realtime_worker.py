import datetime
import json
import logging
import time
from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from db_provider import DbProvider
from firebase_provider import FirebaseProvider
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider
from queue import Queue
from typing import Tuple


class FrcRealtimeWorker(object):

    NO_WEBCAST_TIMEOUT_SEC = 60 * 5

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
        # Returns a tuple of <should exit, should ack message>
        action = 'ack'
        try:
            message = json.loads(message_data)
            message_type = message["type"]
            logging.info("Processing message type: {}".format(message_type))
            if message_type == 'exit':
                return True, action
            elif message_type == 'test':
                logging.info("Got test message: {}".format(message["message"]))
            elif message_type == 'process_match':
                match_key = message["match_key"]
                video_id = message.get("video_id")
                self._process_match_video(match_key, video_id)
            elif message_type == 'process_event':
                event_key = message["event_key"]
                self._process_event_videos(event_key)
            elif message_type == 'process_stream':
                skip_date_check = message.get("skip_date_check", False)
                event_key = message["event_key"]
                stream_url = self._get_stream_url(event_key)
                if not stream_url:
                    logging.warning("No supported streams found...")
                    action = 'nack'
                else:
                    logging.info("Using stream {}".format(stream_url))
                    action = self._process_stream(event_key, stream_url, skip_date_check)
            self.pubsub.completeProcessing(action)
            logging.info("message processing complete")
        except Exception:
            logging.exception("Exception processing message")

        return False, action

    def _get_stream_url(self, event_key: str):
        logging.info("Loading event data for {}".format(event_key))
        event = self.apiv3.fetch_event_details(event_key)
        if not event:
            logging.warning("Unable to load event")
            return None
        webcasts = event["webcasts"]
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        twitch_stream = next(iter([w for w in webcasts if w["type"] == 'twitch']), None)
        livestream = next(iter([w for w in webcasts if w["type"] == 'livestream']), None)
        youtube_stream = next(iter([w for w in webcasts if w["type"] == 'youtube' and w.get("date", now) == now]), None)
        stream_url = None
        if twitch_stream:
            return 'https://twitch.tv/{}'.format(twitch_stream["channel"])
        elif livestream:
            return 'https://livestream.com/accounts/{}/events/{}'.format(
                livestream["channel"], livestream["file"])
        elif youtube_stream:
            return 'https://www.youtube.com/watch?v={}'.format(youtube_stream["channel"])
        return None

    def _process_stream(self, event_key: str, stream_url: str=None, skip_date_check: bool=False):
        logging.info("Processing stream for event {}".format(event_key))
        event_info = self.apiv3.fetch_event_details(event_key)
        event_end = datetime.datetime.strptime(event_info['end_date'], "%Y-%m-%d")
        event_end += datetime.timedelta(days=1)
        now = datetime.datetime.now()
        if not skip_date_check and now > event_end:
            # Event is over, we can now ack the message
            logging.info("Event {} is over, acking message")
            return 'ack'

        if not stream_url and event_info["webcasts"]:
            twitch_streams = filter(lambda w: w.type == 'twitch', event_info["webcasts"])
            stream_url = next(["https://twitch.tv/{}".format(w.channel) for w in twitch_streams])
            logging.info("Using webcast {} from APIv3".format(stream_url))

        if not stream_url:
            logging.warning(
                "No webcasts found for event {}, sleeping for {} seconds".
                format(event_key, self.NO_WEBCAST_TIMEOUT_SEC))
            time.sleep(self.NO_WEBCAST_TIMEOUT_SEC)
            return 'ack'

        # If the twitch worker times out, it will reurn 'ack' or 'nack'
        return self.media.process_twitch_stream(event_key, stream_url,
                                                self._live_frame_callback)


    def _live_frame_callback(self, event_key, image):
        if image is None:
            self.firebase.clear_data_in_firebase(event_key)
            return None
        details = self.cv_provider.process_live_frame(event_key, image)
        if not details:
            logging.warning("Unable to parse score overlay")
            return None
        self.firebase.push_data_to_firebase(details)
        match_mode = details.mode
        with self.db.session() as session:
            session.add(details)

        # Allow the calling code to make decisions based on match state
        return match_mode

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
        cv_start = time.time()
        db_rows = self.cv_provider.process_frame_queue(year, match_key,
                                                       start_time, frame_queue)
        cv_time = time.time() - cv_start
        logging.info("Processing frame queue took {} seconds or {} fps".format(
            cv_time,
            len(db_rows) / cv_time))
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
