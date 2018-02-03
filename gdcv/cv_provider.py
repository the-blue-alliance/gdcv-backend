import cv2
import json
import logging
from livescore import Livescore as FrcLivescore

class CvProvider(object):

    TEST_IMAGE_2017 = './test-images/2017/01.png'

    def __init__(self):
        self.livescore = FrcLivescore()

    def process_test_image(self):
        logging.info("Processing test image: {}".format(self.TEST_IMAGE_2017))
        image = cv2.imread(self.TEST_IMAGE_2017)
        score_data = self.livescore.read(image)
        return json.dumps(score_data)
