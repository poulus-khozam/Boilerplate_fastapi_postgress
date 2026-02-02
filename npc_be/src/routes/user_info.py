from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import NPCUser
from models.user_info import NPCUserInfo
from models.res_code import NPCResCode
from schemas.user_info import UserInfoUpdate, BulkInfoUpdate
from core.dependencies import get_current_user
from typing import List, Optional

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

@router.get("/user_info", status_code=status.HTTP_200_OK)
def get_single_user_info(
    std_code: int,
    code: int,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user),
):
    """
    Retrieves a single piece of info for the logged-in user.
    Usage: /user_info?std_code=10&code=1
    """
    record = db.query(NPCUserInfo).filter(
        NPCUserInfo.company_number == current_user.company_number,
        NPCUserInfo.std_code == std_code,
        NPCUserInfo.code == code
    ).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Information not found"
        )

    return {
        "std_code": record.std_code,
        "code": record.code,
        "data": record.data
    }


@router.get("/user_info/bulk", status_code=status.HTTP_200_OK)
def get_all_user_info(
    std_code: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user),
):
    """
    Retrieves all info records for the logged-in user.
    Optional: Filter by std_code.
    Usage: /user_info/bulk  OR  /user_info/bulk?std_code=10
    """
    query = db.query(NPCUserInfo).filter(
        NPCUserInfo.company_number == current_user.company_number
    )

    # Optional filter if std_code is provided in query params
    if std_code is not None:
        query = query.filter(NPCUserInfo.std_code == std_code)

    records = query.all()

    return {
        "company_number": current_user.company_number,
        "count": len(records),
        "updates": [
            {"std_code": r.std_code, "code": r.code, "data": r.data} 
            for r in records
        ]
    }

@router.get("/info_name", status_code=status.HTTP_200_OK)
def get_info_name(
    std_code: int,
    code: int,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user), # JWT Required
):
    """
    Returns the label/name for a specific std_code and code.
    Example: /info_name?std_code=2&code=1 -> "رقم الموبيل"
    """
    result = db.query(NPCResCode).filter(
        NPCResCode.std_code == std_code,
        NPCResCode.code == code
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="Code definition not found")

    return {
        "std_code": result.std_code,
        "code": result.code,
        "name": result.name
    }


@router.get("/info_name/bulk", status_code=status.HTTP_200_OK)
def get_info_name_bulk(
    std_code: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user), # JWT Required
):
    """
    Returns a list of all labels/names.
    Optional: Filter by std_code.
    Example: /info_name/bulk?std_code=2
    """
    query = db.query(NPCResCode)
    
    if std_code is not None:
        query = query.filter(NPCResCode.std_code == std_code)
    
    results = query.all()
    
    return [
        {"std_code": r.std_code, "code": r.code, "name": r.name}
        for r in results
    ]
