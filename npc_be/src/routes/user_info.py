from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import NPCUser
from models.user_info import NPCUserInfo
from schemas.user_info import UserInfoUpdate, BulkInfoUpdate
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/user_info", status_code=status.HTTP_200_OK)
def update_user_info(
    info_data: UserInfoUpdate,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user),
):
    """
    Inserts or Updates (Upsert) user info based on std_code and code.
    The company_number is taken automatically from the logged-in user.
    """

    # 1. Check if the record already exists
    existing_record = db.query(NPCUserInfo).filter(
        NPCUserInfo.company_number == current_user.company_number,
        NPCUserInfo.std_code == info_data.std_code,
        NPCUserInfo.code == info_data.code
    ).first()

    if existing_record:
        # 2. Update existing record
        existing_record.data = info_data.data
        db.add(existing_record)
        action = "updated"
    else:
        # 3. Insert new record
        new_record = NPCUserInfo(
            company_number=current_user.company_number,
            std_code=info_data.std_code,
            code=info_data.code,
            data=info_data.data
        )
        db.add(new_record)
        action = "created"

    db.commit()

    # Return success message
    return {
        "status": "success",
        "action": action,
        "data": {
            "std_code": info_data.std_code,
            "code": info_data.code,
            "value": info_data.data
        }
    }


@router.post("/user_info/bulk")
def bulk_update_user_info(
    bulk_data: BulkInfoUpdate,  # <--- Uses the new class here
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user),
):
    # Loop through the list
    for item in bulk_data.updates:
        # Logic to find and update/insert each item...
        pass

    db.commit()
    return {"message": "Bulk update successful"}
