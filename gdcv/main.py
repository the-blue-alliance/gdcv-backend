import datetime
import json
import logging
import os
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
        message_data = pubsub.getNextMessage()
        should_ack = True
        try:
            should_exit, should_ack = worker.process_message(message_data)
        except Exception as ex:
            logging.exception("Unable to process message")
        pubsub.completeProcessing(should_ack)

        if should_exit:
            logging.info("Exiting worker thread!")
            break

def main():
    logging.info("Starting gdcv application...")
    metadata_provider = MetadataProvider()
    apiv3_provider = ApiV3Provider(metadata_provider)
    media_provider = MediaProvider()
    pubsub_provider = PubSubProvider()
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

    # GDCV may have been started with a specific message
    starting_message = metadata_provider.getInstance('starting_message', None)
    if starting_message:
        logging.info("Using startup message {}".format(starting_message))
        pubsub_provider.push(starting_message)

    # Write a PID file
    with open('/var/run/gdcv', 'w') as f:
        pid = os.getpid()
        f.write (str(pid))

    # Kick off threads
    thrift_thread = threading.Thread(
        name="thrift_servre", target=run_thrift_server, args=(thrift_service,))

    worker_thread = threading.Thread(
        name="cv_worker", target=run_cv_worker, args=(cv_worker, pubsub_provider))

    thrift_thread.start()
    worker_thread.start()

    # TODO ensure the worker is happy and deal with restarting it on failure

    thrift_thread.join()
    worker_thread.join()


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    main()
