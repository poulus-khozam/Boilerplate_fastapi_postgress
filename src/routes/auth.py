# src/routes/auth.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# --- CORRECTED LINES START ---
from controllers import auth as auth_controller
from core.config import settings
from core.security import create_access_token
from database import get_db
from schemas.token import Token
# --- CORRECTED LINES END ---

router = APIRouter()


@router.post("/login", response_model=Token)
def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = auth_controller.authenticate_user(
        db, company_number=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect ID number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)     
    access_token = create_access_token(
       subject=user.company_number, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
