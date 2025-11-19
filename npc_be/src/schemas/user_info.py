from pydantic import BaseModel
from typing import List


class UserInfoUpdate(BaseModel):
    std_code: int
    code: int
    data: str  # The new value you want to save

# This class defines a list of updates


class BulkInfoUpdate(BaseModel):
    updates: List[UserInfoUpdate]
