import cv2
import logging
import os
import shutil
import time
from pytube import YouTube
from queue import Queue

class YouTubeVideoParser(object):
    '''
    Supports processing an existing YouTube video and extracting frames
    '''

    YOUTUBE_URL_FORMAT = 'https://www.youtube.com/watch?v={}'
    DOWNLOAD_DIR = '/tmp'

    def __init__(self):
        pass

    def download_video(self, video_id: str):
        logging.info("Downloading youtube video with id: {}".format(video_id))
        yt = YouTube(self.YOUTUBE_URL_FORMAT.format(video_id))
        logging.debug('Will download video: {}'.format(yt.title))

        stream = yt.streams.first()
        path = "{}/{}.mp4".format(self.DOWNLOAD_DIR, video_id)
        logging.debug('Output file to: {}'.format(path))
        time_start = time.time()
        stream.download(self.DOWNLOAD_DIR, video_id)
        time_end = time.time()
        time_download = time_end - time_start
        logging.info("Video download took {} seconds".format(time_download))
        return path

    def extract_frames(self,
                       video_id: str,
                       filepath: str,
                       frame_queue: Queue,
                       save_every_n: int = 5):
        logging.info('Extracting frames from {}'.format(filepath))
        vidcap = cv2.VideoCapture(filepath)
        success, image = vidcap.read()
        if not success:
            logging.error("Unable to open file {}".format(filepath))
            return None
        count = 0
        success = True

        frame_count = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
        logging.info("Video has {} frames".format(frame_count))
        time_start = time.time()
        while vidcap.isOpened():
            ret, image = vidcap.read()
            if not ret:
                logging.warning("Failed to read frame from video file")
            if count % save_every_n == 0:
                frame_time = int(vidcap.get(cv2.CAP_PROP_POS_MSEC))  # in msec
                frame_queue.put((image, frame_time))
            count += 1
            if (count == frame_count):
                time_end = time.time()
                vidcap.release()

        extraction_time = time_end - time_start
        logging.info("Frame extraction took {} seconds".format(extraction_time))
