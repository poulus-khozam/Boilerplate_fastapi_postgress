# src/models/res_code.py
from sqlalchemy import Column, String, Integer
from database import Base

class NPCResCode(Base):
    __tablename__ = "npc_res_code"

    std_code = Column(Integer, primary_key=True)
    code = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
