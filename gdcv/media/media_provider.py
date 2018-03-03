import logging
import time
from queue import Queue
from media.twitch_stream_processor import TwitchStreamProcessor
from media.youtube_video_parser import YouTubeVideoParser
from typing import Callable

class MediaProvider(object):
    '''
    A class that encapsulates an entry for all things media-streaming realted
    This can handle streaming live webcasts and parsing historical videos
    from YouTube. This class will end up being a thin wrapper around others.
    This is done to keep things simple when passing objects around
    '''

    NO_STREAM_FOUND_DELAY = 30

    def __init__(self):
        self.yt_video_processor = YouTubeVideoParser()
        self.twitch_processor = TwitchStreamProcessor()

    def fetch_youtube_video(self,
                            video_id: str,
                            frame_queue: Queue,
                            save_every_n_frames: int = 5):
        '''
        Fetch frames from a (not live) YouTube video. Rough outline:
            1. Download the video to a temporary file
            2. Extract frames and insert them into the given queue
        '''
        video_path = self.yt_video_processor.download_video(video_id)
        frame_paths = self.yt_video_processor.extract_frames(
            video_id, video_path, frame_queue, save_every_n_frames)

        logging.info("Frame queue has {} items".format(frame_queue.qsize()))

    def process_twitch_stream(self, event_key: str, stream_url: str,
                              frame_callback: Callable):
        stream, resolution = self.twitch_processor.load_stream(stream_url)
        if stream:
            return self.twitch_processor.process_stream(event_key, stream, resolution,
                                                        frame_callback)
        # No stream found, put this event back in queue
        logging.warning(
            "No stream found, sleeping for {} seconds and trying again".format(
                self.NO_STREAM_FOUND_DELAY))
        time.sleep(self.NO_STREAM_FOUND_DELAY)
        return 'nack'
