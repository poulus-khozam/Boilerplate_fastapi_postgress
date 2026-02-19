from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm 
from sqlalchemy.orm import Session
from database import get_db
from models.ch_data import ChData
from models.profile_details import ChProfileDetails  # Ensure this file exists
from schemas.ch_data import ChDataResponse
from schemas.token import Token 
from schemas.password import ChangePassword 
from controllers import auth as auth_controller 
from controllers import user as user_controller 
from core.config import settings 
from core.security import create_access_token 
from core.dependencies import get_current_ch_user 
from pydantic import BaseModel
from typing import List 
import json
import os

# 1. Define the Router FIRST
router = APIRouter(
    prefix="/api/v1",
    tags=["Business Data"]
)

# 2. Define your Schemas
class MenuItem(BaseModel):
    id: str
    label: str
    icon: str
    action_type: str
    destination: str
    color: str = "primary"

class ProfileMemberResponse(BaseModel):
    id: str
    name: str

# 3. Define Helper functions
def get_church_name(location_id: str) -> str:
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        json_path = os.path.join(base_path, "churches.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            data_map = json.load(f)
            return data_map.get(str(location_id), "Unknown Location")
    except FileNotFoundError:
        return f"Location ID {location_id} (Map file not found)"

# 4. Define Endpoints
@router.get("/profile-members", response_model=List[ProfileMemberResponse])
def get_profile_members(
    location: int = 5,
    profile_id: int = 1,
    year: int = 2026,
    month: int = 0,
    db: Session = Depends(get_db),
    current_user: ChData = Depends(get_current_ch_user)
):
    """
    Retrieves distinct members based on profile details.
    Requires a valid Church User Token.
    """
    results = db.query(ChData.id, ChData.name)\
        .join(ChProfileDetails, ChData.id == ChProfileDetails.id)\
        .filter(ChProfileDetails.location == location)\
        .filter(ChProfileDetails.profile_id == profile_id)\
        .filter(ChProfileDetails.dyear == year)\
        .filter(ChProfileDetails.dmonth == month)\
        .distinct().all()
    
    # Convert result tuples to dictionaries
    return [{"id": r.id, "name": r.name} for r in results]

@router.get("/get_info/{doc_id}", response_model=ChDataResponse)
def get_info(doc_id: str, db: Session = Depends(get_db)):
    user = db.query(ChData).filter(ChData.id == doc_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="No matching document found.")
    church_name = get_church_name(user.location)
    return {"id": user.id, "name": user.name, "location": church_name}

@router.post("/login", response_model=Token)
def login_ch_data(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth_controller.authenticate_ch_data_user(db, user_id=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect ID or password")
    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_ch_password(passwords: ChangePassword, db: Session = Depends(get_db), current_user: ChData = Depends(get_current_ch_user)):
    return user_controller.change_ch_data_password(db=db, user=current_user, passwords=passwords)

@router.get("/menu", response_model=List[MenuItem])
def get_dynamic_menu(current_user: ChData = Depends(get_current_ch_user)):
    return [
        MenuItem(id="profile", label=f"Welcome, {current_user.name}", icon="mdi-account", action_type="INFO", destination="", color="grey"),
        MenuItem(id="change_pwd", label="تغيير كلمة المرور", icon="mdi-key-variant", action_type="NAVIGATE", destination="/change-password", color="blue"),
        MenuItem(id="logout", label="تسجيل خروج", icon="mdi-logout", action_type="LOGOUT", destination="/login", color="red")
    ]
