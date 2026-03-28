# npc_be/src/models/ch_res_code.py
from sqlalchemy import Column, String, Integer
from database import Base

class ChResCode(Base):
    __tablename__ = "ch_res_code"
    std_code = Column(Integer, primary_key=True)
    code = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
