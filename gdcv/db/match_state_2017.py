from db_provider import DbBase
from db.base_match_state import BaseMatchState
from sqlalchemy import Column, Integer


class MatchState2017(DbBase, BaseMatchState):

    __tablename__ = "2017_matches"

    red_fuel_score = Column(Integer)
    red_rotor_count = Column(Integer)
    red_touchpad_count = Column(Integer)

    blue_fuel_score = Column(Integer)
    blue_rotor_count = Column(Integer)
    blue_touchpad_count = Column(Integer)
