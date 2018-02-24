import cv2
import datetime
import json
import logging
from db.match_state_2017 import MatchState2017
from livescore import Livescore2017 as FrcLivescore2017
from queue import Queue

class CvProvider(object):

    MSEC_IN_SEC = 1000
    TEST_IMAGE_2017 = './test-images/2017/01.png'

    def __init__(self):
        self.livescore = FrcLivescore2017()

    def process_frame_queue(self, year: int, match_key: str, actual_start: datetime, frame_queue: Queue):
        if year != 2017:
            # TODO eventually support other years
            logging.error("Unsupported CV year: {}".format(year))

        logging.info("Processing frame queue of {} frames".format(
            frame_queue.qsize()))
        rows = []
        match_start_msec = None
        while not frame_queue.empty():
            frame, frame_time = frame_queue.get()
            logging.info("Frame time: {}".format(frame_time))
            score_data = self.livescore.read(frame)
            logging.debug("Frame data: {}".format(str(score_data)))
            if not score_data:
                logging.warning("Unable to parse frame")
                continue
            if not score_data.time:
                # Match not started yet, ignore
                continue
            elif not match_start_msec:
                # First frame with a real timestamp, sync with actual start time
                match_start_msec = frame_time

            timestamp = actual_start + datetime.timedelta(
                milliseconds=frame_time - match_start_msec)
            state = MatchState2017()
            state.event_key = match_key.split("_")[0]
            state.match_id = match_key.split("_")[1]
            state.play = 1
            state.wall_time = timestamp.timestamp()
            state.match_time = score_data.time
            state.red_score = score_data.red.score
            state.blue_score = score_data.blue.score

            rows.append(state)

        return rows


    def process_test_image(self):
        logging.info("Processing test image: {}".format(self.TEST_IMAGE_2017))
        image = cv2.imread(self.TEST_IMAGE_2017)
        score_data = self.livescore.read(image)
        return str(score_data)
