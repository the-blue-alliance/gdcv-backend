import cv2
import datetime
import json
import logging
import time
from db.match_state_2017 import MatchState2017
from db.match_state_2018 import MatchState2018
from livescore.LivescoreBase import NoOverlayFoundException
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
            try:
                score_data = livescore.read(frame)
            except NoOverlayFoundException:
                continue
            except Exception as e:
                logging.exception(e)
                continue
            if not score_data:
                logging.warning("Unable to parse frame")
                continue
            if not score_data.time or score_data.mode == 'pre_match' or score_data.mode == 'post_match':
                # Match not started yet, ignore
                continue
            elif not match_start_msec:
                # First frame with a real timestamp, sync with actual start time
                match_start_msec = frame_time

            logging.debug("Frame data: {}".format(str(score_data)))
            timestamp = (actual_start.timestamp() * 1000) + (frame_time - match_start_msec)
            state = None
            event_key = match_key.split("_")[0],
            match_id = match_key.split("_")[1],
            if year == 2017:
                state = self._get_state_2017(event_key, match_id,
                                             timestamp, score_data)
            elif year == 2018:
                state = self._get_state_2018(event_key, match_id,
                                             timestamp, score_data)

            if state:
                rows.append(state)

        return rows

    def process_live_frame(self, event_key, image):
        year = int(event_key[:4])
        livescore = self._livescore_for_year(year)
        try:
            s = time.time()
            details = livescore.read(image)
            cv_time = time.time() - s
            logging.debug("CV latency: {}".format(cv_time))
            if year == 2018:
                return self._get_state_2018(event_key, details.match_key,
                                            time.time(), details)
        except NoOverlayFoundException:
            logging.warning("No overlay found")
            return None


    def process_test_image(self):
        logging.info("Processing test image: {}".format(self.TEST_IMAGE_2017))
        image = cv2.imread(self.TEST_IMAGE_2017)
        score_data = self.livescore2017.read(image)
        return str(score_data)

    def _set_common_state(self, state, event_key, match_id, wall_time, score_data):
        state.event_key = event_key
        state.match_id = match_id
        state.play = 1
        state.wall_time = wall_time
        state.time_remaining = score_data.time
        state.mode = score_data.mode
        state.red_score = score_data.red.score
        state.blue_score = score_data.blue.score

    def _get_state_2017(self, event_key, match_id, wall_time, score_data):
        state = MatchState2017()
        self._set_common_state(state, event_key, match_id, wall_time,
                               score_data)

        state.red_fuel_score = score_data.red.fuel_score
        state.red_rotor_count = score_data.red.rotor_count
        state.red_touchpad_count = score_data.red.touchpad_count

        state.blue_fuel_score = score_data.blue.fuel_score
        state.blue_rotor_count = score_data.blue.rotor_count
        state.blue_touchpad_count = score_data.blue.touchpad_count
        return state

    def _get_state_2018(self, event_key, match_id, wall_time, score_data):
        state = MatchState2018()
        self._set_common_state(state, event_key, match_id, wall_time,
                               score_data)

        for alliance in ['red', 'blue']:
            alliance_data = getattr(score_data, alliance)
            for attr in [
                    'boost_count', 'boost_played', 'force_count',
                    'force_played', 'levitate_count', 'levitate_played',
                    'switch_owned', 'scale_owned', 'current_powerup',
                    'powerup_time_remaining', 'auto_quest', 'face_the_boss'
            ]:
                cv_attr = getattr(alliance_data, attr)
                setattr(state, "{}_{}".format(alliance, attr), cv_attr)
        return state
