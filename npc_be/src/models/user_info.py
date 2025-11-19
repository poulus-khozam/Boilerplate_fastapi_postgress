from sqlalchemy import Column, String, Integer
from database import Base


class NPCUserInfo(Base):
    __tablename__ = "npc_user_info"

    # Assuming the combination of these three fields is unique
    company_number = Column(String, primary_key=True, index=True)
    std_code = Column(Integer, primary_key=True)
    code = Column(Integer, primary_key=True)

    # This holds the actual value (e.g., the phone number string)
    data = Column(String, nullable=True)
