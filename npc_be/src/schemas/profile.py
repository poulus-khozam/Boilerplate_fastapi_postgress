# npc_be/src/schemas/profile.py
from pydantic import BaseModel

class ProfileMemberResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True
