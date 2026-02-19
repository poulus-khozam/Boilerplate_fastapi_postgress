# Add this to a new or existing controller file
from sqlalchemy.orm import Session
from models.ch_data import ChData
from models.profile_details import ChProfileDetails

def get_distinct_profile_members(db: Session, location: int, profile_id: int, year: int, month: int):
    return db.query(ChProfileDetails.id, ChData.name)\
        .join(ChData, ChProfileDetails.id == ChData.id)\
        .filter(ChProfileDetails.location == location)\
        .filter(ChProfileDetails.profile_id == profile_id)\
        .filter(ChProfileDetails.dyear == year)\
        .filter(ChProfileDetails.dmonth == month)\
        .distinct().all()
