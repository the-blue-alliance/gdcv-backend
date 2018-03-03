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
from typing import Callable, Tuple
from streamlink.stream import Stream

class TwitchStreamProcessor(object):

    WORKER_RESTART_SEC = 10
    MAX_NO_FRAMES = 15
    TIMEOUT_SEC = 60 * 10  # About one match cycle (plus margin for error)
    FPS = 1
    QUALITIES = ['720p', '720p60', '1080p', '1080p60', '432p', '288p']
    RESOLUTIONS = {
        '288p':  (288,512,3),
        '432p': (432,768,3),
        '720p': (720,1280,3),
        '720p60': (720,1280,3),
        '1080p': (1080,1920,3),
        '1080p60': (1080,1920,3),
    }

    def __init__(self):
        pass

    def load_stream(self, stream_url: str):
        logging.info("Loading streams for {}".format(stream_url))
        try:
            streams = streamlink.streams(stream_url)
        except Exception:
            logging.exception("Unable to load stream")
            return None, None
        stream = None
        resolution = None
        for quality in self.QUALITIES:  # Order of decreasing priority
            if quality in streams:
                stream = streams[quality]
                resolution = self.RESOLUTIONS[quality]
                break

        if stream:
            logging.info("Got stream! {}".format(stream))
            return stream, resolution
        else:
            logging.warning("No stream available")
            return None, None

    def process_stream(self, event_key: str, stream: Stream, resolution: Tuple, frame_callback: Callable):
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
                stdout=sp.PIPE, stderr=sp.PIPE, bufsize=8**10)

            data_queue = Queue()
            frame_size = resolution[0] * resolution[1] * resolution[2]
            def worker():
                while not stop:
                    stderr = pipe.stderr.readlines()
                    for line in stderr:
                        logging.warning("Stderr: {}".format(line))
                        if 'Connection timed out' in str(line):
                            logging.warning("Connection to timed out. Retrying")
                            return
                    data = pipe.stdout.read(frame_size)
                    if data:
                        data_queue.put(data)
            w = threading.Thread(target=worker)
            w.start()

            seen_match = False
            consecutive_no_frames = 0
            start_process_time = time.time()
            last_process_time = time.time()
            while True:
                if not w.is_alive():
                    logging.warning(
                        "Worker thread died, restarting connection in {} seconds".
                        format(self.WORKER_RESTART_SEC))
                    time.sleep(self.WORKER_RESTART_SEC)
                    break
                cur_time = time.time()
                if cur_time >= last_process_time + 1.0 / self.FPS:
                    error = cur_time - last_process_time
                    last_process_time = cur_time

                    qsize = data_queue.qsize()
                    logging.info("Queue length: {}".format(qsize))
                    while data_queue.qsize() > 5:
                        data_queue.get()
                        logging.info("Decreasing queue size: {}".format(data_queue.qsize()))
                    if qsize == 0:
                        consecutive_no_frames += 1

                    if consecutive_no_frames >= self.MAX_NO_FRAMES:
                        logging.warning(
                            "No frames found {} times in a row, reconnecting in {} seconds".
                            format(consecutive_no_frames,
                                   self.WORKER_RESTART_SEC))
                        stop = True
                        break
                    if qsize > 0:
                        consecutive_no_frames = 0
                        data = data_queue.get()
                        frame_start = time.time()
                        image = np.fromstring(data, dtype='uint8').reshape(resolution)
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
                        if (seen_match and match_state == 'post_match') or timeout:
                            logging.info(
                                "Stopping processing. Running for {} seconds. Current state is {}".
                                format(runtime, match_state))
                            stop = True
                            break

            # Loop is done, wait for worker thread to stop and backoff/retry
            w.join()
            return 'nack'
        except:
            logging.exception("Error processing stream")
            stop = True
