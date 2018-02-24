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
        sql_host = self.metadata.get('sql_host').decode('utf-8')
        sql_user = self.metadata.get('sql_user').decode('utf-8')
        sql_pass = self.metadata.get('sql_pass').decode('utf-8')
        sql_db = self.metadata.get('sql_db').decode('utf-8')

        connect_str = 'mysql://{}:{}@{}/{}'.format(sql_user, sql_pass, sql_host, sql_db)
        logging.debug("Connecting to db: {}".format(connect_str))

        self.engine = create_engine(connect_str)
        self.session_factory = sessionmaker(bind=self.engine)

    def generateSchema(self):
        DbBase.metadata.create_all(self.engine)

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
