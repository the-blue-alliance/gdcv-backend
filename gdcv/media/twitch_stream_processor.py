import csv
import cv2
import datetime
import io
import json
import logging
import numpy as np
from queue import Queue
import streamlink
import subprocess as sp
import threading
import time
import traceback
import urlfetch
from typing import Callable
from streamlink.stream import Stream

class TwitchStreamProcessor(object):

    FPS = 1

    def __init__(self):
        pass

    def load_stream(self, stream_url: str):
        logging.info("Loading streams for {}".format(stream_url))
        streams = streamlink.streams(stream_url)
        stream = None
        for quality in ['720p', '1080p', 'best', 'source', '480p', '360p', '160p']:  # Order of decreasing priority
            if quality in streams:
                stream = streams[quality]
                break

        if stream:
            logging.info("Got stream! {}".format(stream))
            return stream
        else:
            logging.warning("No stream available")
            return None

    def process_stream(self, event_key: str, stream: Stream, frame_callback: Callable):
        stop = False
        try:
            pipe = sp.Popen(['ffmpeg', "-i", stream.url,
                      "-loglevel", "quiet", # no text output
                      "-an",   # disable audio
                      "-f", "image2pipe",
                      "-pix_fmt", "bgr24",
                      "-vcodec", "rawvideo", "-"],
                      stdin = sp.PIPE, stdout = sp.PIPE)

            image_queue = Queue()
            def image_worker():
                while not stop:
                    raw_image = pipe.stdout.read(1280*720*3)
                    image_queue.put(raw_image)
                    time.sleep(1.0 / 60.0)  # Shorter than 1/30 be safe

            w = threading.Thread(target=image_worker)
            w.start()

            last_process_time = time.time()
            while True:
                cur_time = time.time()
                if cur_time >= last_process_time + 1.0 / self.FPS:
                    logging.info("Queue length: {}".format(image_queue.qsize()))
                    error = cur_time - last_process_time
                    last_process_time = cur_time

                    num_frames = int(error * 30) + 1
                    logging.info("Skipping {} Frames".format(num_frames))
                    raw_image = None
                    for _ in range(num_frames):
                        if image_queue.qsize() > 0:
                            raw_image = image_queue.get()
                    if not raw_image:
                        logging.warning("Unable to read image from stream queue")
                        continue
                    image = np.fromstring(raw_image, dtype='uint8').reshape((720,1280,3))
                    frame_callback(event_key, image)
        except:
            logging.exception("Error processing stream")
            stop = True
