from db_provider import DbBase
from db.base_match_state import BaseMatchState
from sqlalchemy import Column, String, Integer, Boolean


class MatchState2018(DbBase, BaseMatchState):

    __tablename__ = "2018_matches"

    red_boost_count= Column(Integer)
    red_boost_played = Column(Boolean)
    red_force_count = Column(Integer)
    red_force_played = Column(Boolean)
    red_levitate_count = Column(Integer)
    red_levitate_played = Column(Boolean)
    red_switch_owned = Column(Boolean)
    red_scale_owned = Column(Boolean)
    red_current_powerup = Column(String(16))
    red_powerup_time_remaining = Column(Integer)
    red_auto_quest = Column(Boolean)
    red_face_the_boss = Column(Boolean)

    blue_boost_count= Column(Integer)
    blue_boost_played = Column(Boolean)
    blue_force_count = Column(Integer)
    blue_force_played = Column(Boolean)
    blue_levitate_count = Column(Integer)
    blue_levitate_played = Column(Boolean)
    blue_switch_owned = Column(Boolean)
    blue_scale_owned = Column(Boolean)
    blue_current_powerup = Column(String(16))
    blue_powerup_time_remaining = Column(Integer)
    blue_auto_quest = Column(Boolean)
    blue_face_the_boss = Column(Boolean)
