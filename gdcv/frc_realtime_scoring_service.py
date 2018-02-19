import logging
import thriftpy

from apiv3_provider import ApiV3Provider
from cv_provider import CvProvider
from db_provider import DbProvider
from frc_realtime_scoring_service_handler import FrcRealtimeScoringServiceHandler
from media.media_provider import MediaProvider
from metadata_provider import MetadataProvider
from pubsub_provider import PubSubProvider
from thriftpy.rpc import make_server

class FrcRealtimeScoringService(object):

    VERSION = '0.1'
    BIND_ADDR = '0.0.0.0'
    BIND_PORT = 6000

    def __init__(self, metadata: MetadataProvider, pubsub: PubSubProvider,
                 db: DbProvider, cv: CvProvider, media: MediaProvider,
                 apiv3: ApiV3Provider):
        logging.info("Creating gdcv thrift handler...")
        gdcv_thrift = thriftpy.load(
            'if/gdcv.thrift', module_name='gdcv_thrift')
        dispatch = FrcRealtimeScoringServiceHandler(
            version=self.VERSION,
            thrift=gdcv_thrift,
            metadata=metadata,
            pubsub=pubsub,
            db=db,
            cv=cv,
            media=media,
            apiv3=apiv3,
        )
        self.server = make_server(
            gdcv_thrift.FrcRealtimeScoringService,
            dispatch,
            self.BIND_ADDR,
            self.BIND_PORT
        )


    def serve(self):
        logging.info("Starting gdcv thrift server...")
        self.server.serve()
