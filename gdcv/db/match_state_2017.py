from db_provider import DbBase
from sqlalchemy import Column, String, Integer, BigInteger, PrimaryKeyConstraint

class MatchState2017(DbBase):

    __tablename__ = "2017_matches"
    __table_args__ = (
        PrimaryKeyConstraint('event_key', 'match_id', 'wall_time'),
    )
    event_key = Column(String(16), nullable=False)  # Like 2017nyny
    match_id = Column(String(16), nullable=False)  # Like qm1
    play = Column(Integer, nullable=False)  # Accounts for replays
    wall_time = Column(BigInteger, nullable=False)
    match_time = Column(Integer)  # Number of seconds remaining

    red_score = Column(Integer)
    red_fuel_score = Column(Integer)
    red_rotor_count = Column(Integer)
    red_touchpad_count = Column(Integer)

    blue_score = Column(Integer)
    blue_fuel_score = Column(Integer)
    blue_rotor_count = Column(Integer)
    blue_touchpad_count = Column(Integer)
