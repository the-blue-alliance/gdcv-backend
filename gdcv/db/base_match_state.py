from sqlalchemy import Column, String, Integer, BigInteger, PrimaryKeyConstraint

class BaseMatchState(object):

    __table_args__ = (
        PrimaryKeyConstraint('event_key', 'match_id', 'wall_time'),
    )
    event_key = Column(String(16), nullable=False)  # Like 2017nyny
    match_id = Column(String(16), nullable=False)  # Like qm1
    play = Column(Integer, nullable=False)  # Accounts for replays
    wall_time = Column(BigInteger, nullable=False)
    mode = Column(String(16))  # pre_match, auto, teleop, post_match
    time_remaining = Column(Integer)  # Number of seconds remaining in mode

    red_score = Column(Integer)
    blue_score = Column(Integer)
