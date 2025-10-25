# src/routes/totp.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from controllers import totp as totp_controller
from database import get_db
from schemas.totp import TotpVerify
from schemas.token import Token

router = APIRouter()


@router.post("/verify-totp", response_model=Token)
def verify_totp_route(
    totp_data: TotpVerify, db: Session = Depends(get_db)
):
    tokens = totp_controller.verify_totp(
        db, token=totp_data.login_token, totp_code=totp_data.totp_code
    )
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid TOTP code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens
