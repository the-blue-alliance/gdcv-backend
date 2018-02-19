import cv2
import json
import logging
from db.match_state_2017 import MatchState2017
from livescore import Livescore as FrcLivescore
from queue import Queue

class CvProvider(object):

    TEST_IMAGE_2017 = './test-images/2017/01.png'

    def __init__(self):
        self.livescore = FrcLivescore()

    def process_frame_queue(self, year: int, match_key: str, frame_queue: Queue):
        if year != 2017:
            # TODO eventually support other years
            logging.error("Unsupported CV year: {}".format(year))

        logging.info("Processing frame queue of {} frames".format(
            frame_queue.qsize()))
        i = 0
        rows = []
        while not frame_queue.empty():
            frame = frame_queue.get()
            score_data = self.livescore.read(frame)
            logging.debug("Frame data: {}".format(json.dumps(score_data)))
            state = MatchState2017()
            state.event_key = match_key.split("_")[0]
            state.match_id = match_key.split("_")[1]
            state.play = 1
            state.wall_time = i  # TODO use video time codes + API start time here
            state.match_time = score_data['time']
            state.red_score = score_data['red']['score']
            state.blue_score = score_data['blue']['score']

            rows.append(state)
            i += 1

        return rows



    def process_test_image(self):
        logging.info("Processing test image: {}".format(self.TEST_IMAGE_2017))
        image = cv2.imread(self.TEST_IMAGE_2017)
        score_data = self.livescore.read(image)
        return json.dumps(score_data)
