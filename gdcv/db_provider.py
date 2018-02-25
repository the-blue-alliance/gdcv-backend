import logging

from contextlib import contextmanager
from metadata_provider import MetadataProvider
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DbBase = declarative_base()

class DbProvider(object):

    def __init__(self, metadata: MetadataProvider):
        self.metadata = metadata

    def connect(self):
        logging.info("Connecting to mysql...")
        sql_host = self.metadata.get('sql_host').decode('utf-8')
        sql_user = self.metadata.get('sql_user').decode('utf-8')
        sql_pass = self.metadata.get('sql_pass').decode('utf-8')
        sql_db = self.metadata.get('sql_db').decode('utf-8')

        connect_str = 'mysql://{}:{}@{}/{}'.format(sql_user, sql_pass, sql_host, sql_db)
        logging.debug("Connecting to db: {}".format(connect_str))

        self.engine = create_engine(connect_str)
        self.session_factory = sessionmaker(bind=self.engine)

    def generateSchema(self):
        logging.info("Generating mysql schema")
        DbBase.metadata.create_all(self.engine)

    def deleteMatchData(self, match_key):
        year = int(match_key[:4])
        event_key = match_key.split("_")[0]
        match_id = match_key.split("_")[1]
        if year == 2017:
            from db.match_state_2017 import MatchState2017 as MatchState
        elif year == 2018:
            from db.match_state_2018 import MatchState2018 as MatchState
        with self.session() as session:
            logging.info("clearing all match data for {}".format(match_key))
            session.query(MatchState).filter(
                MatchState.event_key == event_key).filter(
                    MatchState.match_id == match_id).delete()


    def deleteEventData(self, event_key):
        year = int(event_key[:4])
        if year == 2017:
            from db.match_state_2017 import MatchState2017 as MatchState
        elif year == 2018:
            from db.match_state_2018 import MatchState2018 as MatchState
        with self.session() as session:
            logging.info("clearing all event data for {}".format(event_key))
            session.query(MatchState).filter(
                MatchState.event_key == event_key).delete()

    @contextmanager
    def session(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
