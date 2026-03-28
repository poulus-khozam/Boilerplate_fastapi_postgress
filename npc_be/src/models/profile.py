# npc_be/src/models/profile.py
from sqlalchemy import Column, String, Integer
from database import Base

class ChProfile(Base):
    __tablename__ = "ch_profile"

    id = Column(String, primary_key=True)
    location = Column(Integer, primary_key=True)
    profile_id = Column(Integer, primary_key=True)
    rule = Column(Integer) # 1 for all, 0 for self-only
