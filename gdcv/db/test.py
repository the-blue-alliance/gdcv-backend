from db_provider import DbBase
from sqlalchemy import Column, String, Integer


class Test(DbBase):

    __tablename__ = 'test'
    id = Column(Integer, primary_key=True)
    text = Column(String(16))

    def __init__(self, text):
        self.text = text
