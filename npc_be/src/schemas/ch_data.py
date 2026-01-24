from pydantic import BaseModel
class ChDataResponse(BaseModel):
  id: int
  name: str
  location: str # This will hold the Church Name, not the ID
