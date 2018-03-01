import datetime
import logging
import queue

from google.cloud import pubsub

class PubSubProvider(object):

    def __init__(self, project_id, topic_id):
        self.project_id = project_id.decode('utf-8')
        self.topic_id = topic_id.decode('utf-8')
        self.msg_queue = queue.Queue()
        self.subscriber = None
        self.current_message = None

    def init(self):
        self._create()
        self._subscribe()

    def push(self, message):
        publisher = pubsub.PublisherClient()
        full_topic = publisher.topic_path(self.project_id, self.topic_id)
        logging.info("Pusing message: {} to topic {}".format(
            message, full_topic))
        return publisher.publish(full_topic, message.encode('utf-8'))

    def pull(self):
        logging.info("Blocking local thread to stream messages from pubsub")
        sub_name = self.subscriber.subscription_path(self.project_id,
                                                     self.topic_id)
        subscription = self.subscriber.subscribe(sub_name)
        return subscription.open(self._callback)

    def getNextMessage(self):
        if self.current_message:
            logging.warning(
                "Already processing message {}, can't get another!".format(
                    self.current_message.message_id))
            return None
        logging.info("Blocking for next pubsub message...")
        message = self.msg_queue.get()
        now = datetime.datetime.now()
        message_data = message.data.decode('utf-8')
        logging.info("Got message {} published at {} with data: {}".format(
            message.message_id, message.publish_time, message_data))
        self.current_message = message
        return message.message_id, message_data

    def completeProcessing(self, message_id):
        if message_id != self.current_message.message_id:
            logging.warning("Message {} is not the current message!".format(message_id))
            return
        self.current_message.ack()
        self.current_message = None

    def _create(self):
        publisher = pubsub.PublisherClient()
        full_topic = publisher.topic_path(self.project_id, self.topic_id)
        project_path = publisher.project_path(self.project_id)
        current_topics = publisher.list_topics(project_path)
        if full_topic in current_topics:
            logger.info("Pub/Sub topic {} already exists".format(full_topic))
        else:
            logging.info("Creating pubsub topic {}".format(full_topic))
            publisher.create_topic(full_topic)

    def _subscribe(self):
        self.subscriber = pubsub.SubscriberClient()
        topic_name = self.subscriber.topic_path(self.project_id, self.topic_id)
        sub_name = self.subscriber.subscription_path(self.project_id,
                                                     self.topic_id)
        logging.info("Pulling messages from subscription {}".format(sub_name))

        self.subscriber.create_subscription(sub_name, topic_name)

    def _callback(self, message):
        # If we're already processing a message, nack and send it back
        if self.current_message:
            logging.info("Refusing to accept new message, already busy")
            message.nack()
            return
        self.msg_queue.put(message)
