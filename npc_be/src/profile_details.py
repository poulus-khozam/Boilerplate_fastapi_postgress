# npc_be/src/models/profile_details.py
from sqlalchemy import Column, String, Integer, ForeignKey
from database import Base

class ChProfileDetails(Base):
    __tablename__ = "ch_profile_details"

    # Define columns based on your query requirements
    # Assuming id + profile_id + dyear + dmonth forms a composite key or just indices
    id = Column(String, primary_key=True) 
    location = Column(Integer)
    profile_id = Column(Integer, primary_key=True)
    dyear = Column(Integer, primary_key=True)
    dmonth = Column(Integer, primary_key=True)
  
