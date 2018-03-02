import datetime
import json
import logging
import threading
import time

from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from firebase_provider import FirebaseProvider
from db_provider import DbProvider
from frc_realtime_scoring_service import FrcRealtimeScoringService
from frc_realtime_worker import FrcRealtimeWorker
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider


def run_thrift_server(service: FrcRealtimeScoringService):
    service.serve()


def run_cv_worker(worker: FrcRealtimeWorker, pubsub: PubSubProvider):
    while True:
        message_id, message_data = pubsub.getNextMessage()
        should_ack = True
        try:
            should_exit, should_ack = worker.process_message(message_data)
        except Exception as ex:
            logging.exception("Unable to process message")
        pubsub.completeProcessing(message_id, should_ack)

        if should_exit:
            logging.info("Exiting worker thread!")
            break


def run_pubsub_subscriber(pubsub: PubSubProvider):
    try:
        pubsub.init()
        message_stream = pubsub.pull()

        # Block forever and receive messages
        message_stream.result()
    except Exception as ex:
        logging.exception("Pubsub error")

def main():
    logging.info("Starting gdcv application...")
    metadata_provider = MetadataProvider()
    apiv3_provider = ApiV3Provider(metadata_provider)
    media_provider = MediaProvider()
    project_id = metadata_provider.get('project-id')
    pubsub_topic = metadata_provider.get('pubsub-topic-id')
    pubsub_provider = PubSubProvider(project_id, pubsub_topic)
    cv_provider = CvProvider()
    firebase_provider = FirebaseProvider(metadata_provider)
    db_provider = DbProvider(metadata_provider)
    db_provider.connect()
    db_provider.generateSchema()
    thrift_service = FrcRealtimeScoringService(
        metadata_provider, pubsub_provider, db_provider, cv_provider,
        media_provider, apiv3_provider)
    cv_worker = FrcRealtimeWorker(metadata_provider, cv_provider,
                                  apiv3_provider, media_provider, db_provider,
                                  pubsub_provider, firebase_provider)

    # Kick off threads
    thrift_thread = threading.Thread(
        name="thrift_servre", target=run_thrift_server, args=(thrift_service,))

    worker_thread = threading.Thread(
        name="cv_worker", target=run_cv_worker, args=(cv_worker, pubsub_provider))

    pubsub_thread = threading.Thread(
        name="pubsub_subscriber",
        target=run_pubsub_subscriber,
        args=(pubsub_provider, ))

    thrift_thread.start()
    worker_thread.start()
    pubsub_thread.start()

    # TODO ensure the worker is happy and deal with restarting it on failure

    thrift_thread.join()
    worker_thread.join()
    pubsub_thread.join()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
