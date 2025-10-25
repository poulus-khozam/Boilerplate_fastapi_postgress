# src/controllers/totp.py
import pyotp
from sqlalchemy.orm import Session
from models.user import NPCUser
from core.security import create_access_token
from jose import jwt, JWTError
from core.config import settings
from datetime import timedelta


def verify_totp(db: Session, token: str, totp_code: str):
    try:
        # CORRECTED LINE: Use settings.ALGORITHM instead of importing ALGORITHM
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        company_number: str = payload.get("sub")
        if company_number is None:
            return None
    except JWTError:
        return None

    user = db.query(NPCUser).filter(
        NPCUser.company_number == company_number).first()
    if not user or not user.totp_secret:
        return None

    totp = pyotp.TOTP(user.totp_secret)
    if totp.verify(totp_code):
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        additional_claims = {"2fa": "OK"}
        access_token = create_access_token(
            subject=user.company_number, expires_delta=access_token_expires, additional_claims=additional_claims
        )
        return {"access_token": access_token, "token_type": "bearer"}

    return None
