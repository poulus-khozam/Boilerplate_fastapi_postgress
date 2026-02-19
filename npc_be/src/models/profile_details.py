# npc_be/src/models/profile_details.py
from sqlalchemy import Column, String, Integer
from database import Base

class ChProfileDetails(Base):
    __tablename__ = "ch_profile_details"

    # In SQLAlchemy, we need to mark columns as primary_key 
    # if they form a unique combination (Composite Key)
    id = Column(String, primary_key=True)
    location = Column(Integer, primary_key=True)
    profile_id = Column(Integer, primary_key=True)
    dyear = Column(Integer, primary_key=True)
    dmonth = Column(Integer, primary_key=True)
