# src/routes/user.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.password import ChangePassword
from controllers import user as user_controller
from models.user import NPCUser
from core.dependencies import get_current_user

router = APIRouter()


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    passwords: ChangePassword,
    db: Session = Depends(get_db),
    current_user: NPCUser = Depends(get_current_user),
):
    """
    Changes the password for the currently authenticated user.

    - **Authentication**: Requires a valid JWT access token in the Authorization header.
    - **Request Body**: Expects a JSON object with "old_password" and "new_password".
    - **Responses**:
        - `200 OK`: If the password was changed successfully.
        - `400 Bad Request`: If the provided "old_password" is incorrect.
        - `401 Unauthorized`: If the access token is missing or invalid.
    """
    return user_controller.change_user_password(db=db, user=current_user, passwords=passwords)
