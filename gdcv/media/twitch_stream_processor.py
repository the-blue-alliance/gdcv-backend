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

    TIMEOUT_SEC = 60 * 10  # About one match cycle (plus margin for error)
    FPS = 1

    def __init__(self):
        pass

    def load_stream(self, stream_url: str):
        logging.info("Loading streams for {}".format(stream_url))
        streams = streamlink.streams(stream_url)
        stream = None
        for quality in ['720p', '720p60']:  # Order of decreasing priority
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
            pipe = sp.Popen([
                'ffmpeg',
                '-loglevel', 'warning',
                '-re',
                '-timeout', '5',
                '-i', stream.url,
                '-an',   # disable audio
                '-f', 'image2pipe',
                '-vf', 'fps={}'.format(self.FPS),
                '-pix_fmt', 'bgr24',
                '-vcodec', 'rawvideo', '-'],
                stdout=sp.PIPE, bufsize=8**10)

            data_queue = Queue()
            def worker():
                while not stop:
                    data = pipe.stdout.read(720 * 1280 * 3)
                    if data:
                        data_queue.put(data)
            w = threading.Thread(target=worker)
            w.start()

            seen_match = False
            start_process_time = time.time()
            last_process_time = time.time()
            while True:
                cur_time = time.time()
                if cur_time >= last_process_time + 1.0 / self.FPS:
                    error = cur_time - last_process_time
                    last_process_time = cur_time

                    qsize = data_queue.qsize()
                    logging.info("Queue length: {}".format(qsize))
                    while data_queue.qsize() > 5:
                        data_queue.get()
                        logging.info("Decreasing queue size: {}".format(data_queue.qsize()))
                    if qsize > 0:
                        data = data_queue.get()
                        frame_start = time.time()
                        image = np.fromstring(data, dtype='uint8').reshape((720, 1280, 3))
                        if image is not None:
                            try:
                                match_state = frame_callback(event_key, image)
                            except Exception:
                                logging.error("Exception processing frame")
                                match_state = None

                        seen_match = seen_match or match_state == 'auto' or match_state == 'teleop'
                        runtime = time.time() - start_process_time
                        frame_latency = time.time() - frame_start
                        logging.info("Frame processed in {} seconds".format(frame_latency))

                        timeout = runtime > self.TIMEOUT_SEC \
                            and match_state != 'auto' \
                            and match_state != 'teleop'

                        # Stop processing after one match or if we go long enough
                        # without seeing another match start
                        if match_state == 'post_match' or timeout:
                            logging.info(
                                "Stopping processing. Running for {} seconds. Current state is {}".
                                format(runtime, match_state))
                            stop = True
                            w.join()
                            return 'nack'
        except:
            logging.exception("Error processing stream")
            stop = True
