import cv2
import datetime
import json
import logging
from db.match_state_2017 import MatchState2017
from livescore import Livescore2017 as FrcLivescore2017
from livescore import Livescore2018 as FrcLivescore2018
from queue import Queue

class CvProvider(object):

    MSEC_IN_SEC = 1000
    TEST_IMAGE_2017 = './test-images/2017/01.png'

    def __init__(self):
        self.livescore2017 = FrcLivescore2017()
        self.livescore2018 = FrcLivescore2018()

    def _livescore_for_year(self, year: int):
        if year == 2017:
            return self.livescore2017
        elif year == 2018:
            return self.livescore2018
        return None

    def process_frame_queue(self, year: int, match_key: str, actual_start: datetime, frame_queue: Queue):
        if year not in [2017, 2018]:
            # TODO eventually support other years
            logging.error("Unsupported CV year: {}".format(year))

        livescore = self._livescore_for_year(year)
        logging.info("Processing frame queue of {} frames".format(
            frame_queue.qsize()))
        rows = []
        match_start_msec = None
        while not frame_queue.empty():
            frame, frame_time = frame_queue.get()
            logging.info("Frame time: {}".format(frame_time))
            score_data = livescore.read(frame)
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
            state.red_fuel_score = score_data.red.fuel_score
            state.red_rotor_count = score_data.red.rotor_count
            state.red_touchpad_count = score_data.red.touchpad_count

            state.blue_score = score_data.blue.score
            state.blue_fuel_score = score_data.blue.fuel_score
            state.blue_rotor_count = score_data.blue.rotor_count
            state.blue_touchpad_count = score_data.blue.touchpad_count

            rows.append(state)

        return rows


    def process_test_image(self):
        logging.info("Processing test image: {}".format(self.TEST_IMAGE_2017))
        image = cv2.imread(self.TEST_IMAGE_2017)
        score_data = self.livescore2017.read(image)
        return str(score_data)
