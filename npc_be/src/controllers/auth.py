# src/controllers/auth.py
from sqlalchemy.orm import Session
from models.user import NPCUser
from models.ch_data import ChData
from core.security import verify_password
from jose import jwt, JWTError
from core.config import settings

def authenticate_user(db: Session, company_number: str, password: str) -> NPCUser | None:
    # Find the user by company_number
    user = db.query(NPCUser).filter(
        NPCUser.company_number == company_number).first()

    # If no user is found, or the password in the database is empty, authentication fails.
    if not user or not user.password:
        return None

    # --- THIS IS THE CRITICAL LOGIC BLOCK ---
    # 1. First, try to verify the input as a plain-text password.
    try:
        if verify_password(password, user.password):
            # If verification is successful, we are done. Return the user.
            return user
    except ValueError:
        # This block will run if verify_password fails, for example,
        # because the provided password string is >72 characters.
        # We can safely ignore this error and proceed to the next check.
        pass

    # 2. If the first check failed, try a direct string comparison.
    # This allows logging in by providing the already-hashed password.
    if password == user.password:
        return user
    # --- END OF CRITICAL LOGIC ---

    # If both checks have failed, authentication fails.
    return None


def get_user_from_token(db: Session, token: str) -> NPCUser | None:
    """
    Decodes a JWT, extracts the company_number, and retrieves the user from the database.
    Returns the user object or None if the token is invalid or the user doesn't exist.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[settings.ALGORITHM])
        company_number: str = payload.get("sub")
        if company_number is None:
            return None
    except JWTError:
        return None

    user = db.query(NPCUser).filter(
        NPCUser.company_number == company_number).first()
    return user

def authenticate_ch_data_user(db: Session, user_id: str, password: str) -> ChData | None:
    # Find the user by id in ch_data table
    user = db.query(ChData).filter(ChData.id == user_id).first()

    # If no user or no password set
    if not user or not user.password:
        return None

     # PLAIN TEXT CHECK: Direct string comparison
    if password == user.password:
        return user
 
    return None
 
def get_ch_data_user_from_token(db: Session, token: str) -> ChData | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    return db.query(ChData).filter(ChData.id == user_id).first()
