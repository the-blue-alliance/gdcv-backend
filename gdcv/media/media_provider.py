import logging
from queue import Queue
from media.youtube_video_parser import YouTubeVideoParser

class MediaProvider(object):
    '''
    A class that encapsulates an entry for all things media-streaming realted
    This can handle streaming live webcasts and parsing historical videos
    from YouTube. This class will end up being a thin wrapper around others.
    This is done to keep things simple when passing objects around
    '''

    def __init__(self):
        self.yt_video_processor = YouTubeVideoParser()

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
