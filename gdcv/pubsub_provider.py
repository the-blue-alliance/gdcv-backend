import datetime
import logging
import queue
import socket

from google.cloud import pubsub
from google.api_core.exceptions import AlreadyExists

class PubSubProvider(object):

    def __init__(self):
        self.msg_queue = queue.Queue()
        self.current_message = None

    def push(self, message):
        logging.info("Pusing message: {} to work queue".format(message))
        return self.msg_queue.put(message)

    def getNextMessage(self):
        if self.current_message:
            logging.warning(
                "Already processing message {}, can't get another!".format(
                    self.current_message))
            return None
        logging.info("Blocking for next pubsub message...")
        message = self.msg_queue.get()
        logging.info("Got message {}".format(message))
        self.current_message = message
        return message

    def completeProcessing(self, action='ack'):
        if not self.current_message:
            logging.warning("No current message to complete!")
        message = self.current_message
        self.current_message = None
        if action == 'nack':
            # We need to do more processing, put the message back in the queue
            self.push(message)
