from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from database import get_db
from models.ch_data import ChData
from schemas.ch_data import ChDataResponse
from schemas.token import Token 
from schemas.password import ChangePassword 
from controllers import auth as auth_controller 
from controllers import user as user_controller 
from core.config import settings 
from core.security import create_access_token 
from core.dependencies import get_current_ch_user 
import json
import os

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
def get_info(doc_id: str, db: Session = Depends(get_db)):
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

@router.post("/login", response_model=Token)
def login_ch_data(
    db: Session = Depends(get_db), 
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login specifically for users in the ch_data table.
    - Username field = ID
    - Password field = Password (plain or hashed)
    """
    user = auth_controller.authenticate_ch_data_user(
        db, user_id=form_data.username, password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)     
    
    # Create token using the ch_data ID as the subject
    access_token = create_access_token(
       subject=user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_ch_password(
    passwords: ChangePassword,
    db: Session = Depends(get_db),
    current_user: ChData = Depends(get_current_ch_user),
):
    """
    Changes password for ChData users.
    Requires Bearer Token from /api/v1/login.
    """
    return user_controller.change_ch_data_password(
        db=db, user=current_user, passwords=passwords
    )
