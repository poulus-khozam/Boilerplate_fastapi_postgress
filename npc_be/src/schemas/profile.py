# npc_be/src/schemas/profile.py
from pydantic import BaseModel
from typing import List

class DegreeItem(BaseModel):
    month_name: str
    degree: int

class MemberWithDegreesResponse(BaseModel):
    id: str
    name: str
    degrees: List[DegreeItem]
