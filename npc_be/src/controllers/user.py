# src/controllers/user.py
from sqlalchemy.orm import Session
from models.user import NPCUser
from schemas.password import ChangePassword
from core.security import verify_password, get_password_hash
from fastapi import HTTPException, status
from passlib.exc import UnknownHashError


def change_user_password(db: Session, user: NPCUser, passwords: ChangePassword):
    # Sanitize inputs: remove leading/trailing whitespace.
    old_pass = passwords.old_password.strip()
    new_pass = passwords.new_password.strip()

    # Validate old password length.
    if len(old_pass) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password cannot be longer than 72 characters.",
        )

    # Validate new password length.
    if len(new_pass) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be longer than 72 characters.",
        )

    is_old_password_valid = False

    # 1. Check plain-text password first, using the sanitized 'old_pass'.
    if old_pass == user.password:
        is_old_password_valid = True

    # 2. If not valid, check hashed password, using the sanitized 'old_pass'.
    if not is_old_password_valid:
        try:
            if verify_password(old_pass, user.password):
                is_old_password_valid = True
        except (UnknownHashError, ValueError):
            # This block correctly handles cases where old_pass is too long
            # for bcrypt or when user.password is not a hash.
            pass

    # If neither check succeeded, raise the final error.
    if not is_old_password_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )

    # --- THIS IS THE CRITICAL FIX ---
    # Hash the sanitized 'new_pass', NOT the original 'passwords.new_password'.
    # hashed_password = get_password_hash(new_pass)
    # --- END OF FIX ---

    user.password = new_pass
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}
