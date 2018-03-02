import json
import logging
import urlfetch

from db.match_state_2018 import MatchState2018
from metadata_provider import MetadataProvider

class FirebaseProvider(object):

    URLFORMAT = 'https://{}.firebaseio.com/{}.json?print=silent&auth={}'
    URLKEY = 'le/{}'  # format with event key

    def __init__(self, metadata: MetadataProvider):
        self.last_data = {}
        self.project_id = metadata.get('project-id').decode('utf-8')
        self.firebase_secret = metadata.get('firebase_secret').decode('utf-8')

    def clear_data_in_firebase(self, event_key):
        firebase_path = self.URLKEY.format(event_key)
        url = self.URLFORMAT.format(firebase_path, self.firebase_secret)
        result = urlfetch.patch(url, data=json.dumps(None))
        if result.status_code not in {200, 204}:
            logging.warning(
                "Error with PATCH data to Firebase: {}; {}. ERROR {}: {}".
                format(url, updated_data_json, result.status_code,
                       result.content))

    def push_data_to_firebase(self, details: MatchState2018):
        logging.info("Processing frame details: {}".format(details))
        data = {
            'mk': details.match_id,
            'm': details.mode,
            't': details.time_remaining,
            'rs': details.red_score,
            'rfc': details.red_force_count,
            'rfp': details.red_force_played,
            'rlc': details.red_levitate_count,
            'rlp': details.red_levitate_played,
            'rbc': details.red_boost_count,
            'rbp': details.red_boost_played,
            'rsco': details.red_scale_owned,
            'rswo': details.red_switch_owned,
            'rcp': details.red_current_powerup,
            'rpt': details.red_powerup_time_remaining,
            'raq': details.red_auto_quest,
            'rfb': details.red_face_the_boss,
            'bs': details.blue_score,
            'bfc': details.blue_force_count,
            'bfp': details.blue_force_played,
            'blc': details.blue_levitate_count,
            'blp': details.blue_levitate_played,
            'bbc': details.blue_boost_count,
            'bbp': details.blue_boost_played,
            'bsco': details.blue_scale_owned,
            'bswo': details.blue_switch_owned,
            'bcp': details.blue_current_powerup,
            'bpt': details.blue_powerup_time_remaining,
            'baq': details.blue_auto_quest,
            'bfb': details.blue_face_the_boss,
        }

        updated_data = {}
        for key, value in data.items():
            if self.last_data.get(key) != value:
                updated_data[key] = value
        self.last_data = data

        updated_data_json = json.dumps(updated_data)
        firebase_path = self.URLKEY.format(details.event_key)
        url = self.URLFORMAT.format(self.project_id, firebase_path,
                                    self.firebase_secret)
        logging.info("Pushing to firebase: {}".format(url))
        result = urlfetch.patch(url, data=updated_data_json)
        if result.status_code not in {200, 204}:
            logging.warning(
                "Error with PATCH data to Firebase: {}; {}. ERROR {}: {}".
                format(url, updated_data_json, result.status_code,
                       result.content))
