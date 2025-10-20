# src/models/user.py
from pydantic import BaseModel
from sqlalchemy import Column, String, Integer
from database import Base


class NPCUser(Base):
    __tablename__ = "npc_users"

    id = Column(Integer, primary_key=True, index=True)
    company_number = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    totp_secret = Column(String)
    id_number = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
