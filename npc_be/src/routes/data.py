import json
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.ch_data import ChData
from schemas.ch_data import ChDataResponse

router = APIRouter(
    prefix="/api/v1",
    tags=["Business Data"]
)

def get_church_name(location_id: str) -> str:
    """Helper to load JSON and map ID to Name"""
    try:
        # Construct path relative to this file or project root
        # Assuming churches.json is in src/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, "churches.json")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data_map = json.load(f)
            return data_map.get(str(location_id), "Unknown Location")
    except FileNotFoundError:
        return f"Location ID {location_id} (Map file not found)"

@router.get("/get_info/{doc_id}", response_model=ChDataResponse)
def get_info(doc_id: int, db: Session = Depends(get_db)):
    """
    Get user details by ID.
    - Fetches from ch_data table.
    - Hides mobile number.
    - Maps numeric location to Church Name.
    - No Token Required.
    """
    user = db.query(ChData).filter(ChData.id == doc_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching document found for that ID."
        )

    # Map the numeric location ID to the Church Name
    church_name = get_church_name(user.location)

    # Return data matching the ChDataResponse schema (automatically excludes mobile)
    return {
        "id": user.id,
        "name": user.name,
        "location": church_name
    }
