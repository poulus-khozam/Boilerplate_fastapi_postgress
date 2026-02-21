from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  
from sqlalchemy.orm import Session, aliased  
from database import get_db
from models.ch_data import ChData
from models.profile_details import ChProfileDetails  
from models.profile import ChProfile  
from models.ch_res_code import ChResCode 
from schemas.ch_data import ChDataResponse
from schemas.token import Token 
from schemas.password import ChangePassword 
from schemas.profile import MemberWithDegreesResponse, DegreeItem
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
@router.get("/profile-members", response_model=List[MemberWithDegreesResponse])
def get_profile_members(
    location: int,
    profile_id: int,
    year: int = 2026,
    db: Session = Depends(get_db),
    current_user: ChData = Depends(get_current_ch_user)
):
    # 1. Permission Check (Keep your existing ch_profile check here)
    user_perm = db.query(ChProfile).filter(
        ChProfile.id == current_user.id,
        ChProfile.location == location,
        ChProfile.profile_id == profile_id
    ).first()

    if not user_perm:
        raise HTTPException(status_code=403, detail="Forbidden")

    # 2. Execute the query with the join for degree names (std_code=3)
    # Note: dmonth=0 filter is removed because we want all months
    query = db.query(
        ChData.id, 
        ChData.name, 
        ChResCode.name.label("month_name"), 
        ChProfileDetails.degree
    ).join(ChProfileDetails, ChData.id == ChProfileDetails.id)\
     .join(ChResCode, (ChProfileDetails.dmonth == ChResCode.code) & (ChResCode.std_code == 3))\
     .filter(ChProfileDetails.location == location)\
     .filter(ChProfileDetails.profile_id == profile_id)\
     .filter(ChProfileDetails.dyear == year)

    # Apply rule=0 restriction if necessary
    if user_perm.rule == 0:
        query = query.filter(ChData.id == current_user.id)

    rows = query.all()

    # 3. Group flat results into Master-Detail structure
    members_map = {}
    for row in rows:
        if row.id not in members_map:
            members_map[row.id] = {
                "id": row.id,
                "name": row.name,
                "degrees": []
            }
        members_map[row.id]["degrees"].append({
            "month_name": row.month_name,
            "degree": row.degree
        })

    return list(members_map.values())
    
 
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
def get_dynamic_menu(
    db: Session = Depends(get_db),
    current_user: ChData = Depends(get_current_ch_user)
):
    print(f"DEBUG: Fetching menu for User ID: {current_user.id}")
    # 1. Start with the Welcome Item
    menu = [
        MenuItem(
            id="profile",
            label=f"أهلاً، {current_user.name}",
            icon="mdi-account",
            action_type="INFO",
            destination="",
            color="grey"
        )
    ]

    # 2. Setup Aliases for the double join
    # b for Location Name (std_code=1)
    # c for Profile Name (std_code=2)
    LocationName = aliased(ChResCode)
    ProfileName = aliased(ChResCode)

    # 3. Execute the SQL Logic
    # select a.*, b.name, c.name from ch_profile a ...
    user_assignments = db.query(ChProfile, LocationName.name, ProfileName.name)\
        .join(LocationName, (LocationName.std_code == 1) & (ChProfile.location == LocationName.code))\
        .join(ProfileName, (ProfileName.std_code == 2) & (ChProfile.profile_id == ProfileName.code))\
        .filter(ChProfile.id == current_user.id)\
        .all()

    # 4. Loop through results and create menu items
    for assignment, loc_name, prof_name in user_assignments:
        # Combine b.name || ' ' || c.name
        combined_label = f"{loc_name} {prof_name}"
        
        menu.append(
            MenuItem(
                id=f"item_{assignment.location}_{assignment.profile_id}",
                label=combined_label,
                icon="mdi-view-list", # You can customize this
                action_type="NAVIGATE",
                # destination passes loc and pid as query params
                destination=f"/profile-members?location={assignment.location}&profile_id={assignment.profile_id}",
                color="primary"
            )
        )

    # 5. Add static items (Change Password & Logout)
    menu.append(
        MenuItem(
            id="change_pwd",
            label="تغيير كلمة المرور",
            icon="mdi-key-variant",
            action_type="NAVIGATE",
            destination="/change-password",
            color="blue"
        )
    )
    menu.append(
        MenuItem(
            id="logout",
            label="تسجيل خروج",
            icon="mdi-logout",
            action_type="LOGOUT",
            destination="/login",
            color="red"
        )
    )
    
    return menu 
