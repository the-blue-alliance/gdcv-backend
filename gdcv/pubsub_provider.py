import logging
import queue

from google.cloud import pubsub

class PubSubProvider(object):

    def __init__(self, project_id, topic_id):
        self.project_id = project_id.decode('utf-8')
        self.topic_id = topic_id.decode('utf-8')
        self.msg_queue = queue.Queue()
        self.subscriber = None

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
        return self.msg_queue.get()

    def _create(self):
        publisher = pubsub.PublisherClient()
        full_topic = publisher.topic_path(self.project_id, self.topic_id)
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
        data = message.data.decode('utf-8')
        logging.info("Received pubsub message: {}".format(data))
        message.ack()
        self.msg_queue.put(data)
