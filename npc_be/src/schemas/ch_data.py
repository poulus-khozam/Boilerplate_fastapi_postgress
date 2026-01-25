from pydantic import BaseModel
class ChDataResponse(BaseModel):
  id: str
  name: str
  location: str # This will hold the Church Name, not the ID
