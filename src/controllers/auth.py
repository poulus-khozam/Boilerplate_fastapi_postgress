# src/controllers/auth.py
from sqlalchemy.orm import Session
from models.user import NPCUser
from core.security import verify_password

def authenticate_user(db: Session, company_number: str, password: str) -> NPCUser | None:
    # Find the user by company_number (no change here)
    user = db.query(NPCUser).filter(NPCUser.company_number == company_number).first()

    # If no user is found, or the password in the database is empty, authentication fails.
    if not user or not user.password:
        return None

    # --- MODIFIED LOGIC START ---
    # The login is successful if:
    # 1. The provided password, when hashed, matches the stored password (secure method)
    # OR
    # 2. The provided password is a direct match to the stored hash (insecure fallback)
    if verify_password(password, user.password) or (password == user.password):
        return user
    # --- MODIFIED LOGIC END ---

    # If both checks fail, authentication fails.
    return None
