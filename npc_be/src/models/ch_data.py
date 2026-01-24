
from sqlalchemy import Column, String, Integer
from database import Base
class ChData(Base):
tablename = "ch_data"
 
id = Column(Integer, primary_key=True, index=True)
name = Column(String)
location = Column(String) # Stored as ID string (e.g. "1")
mobile = Column(String)   # This will be fetched but excluded from API response
