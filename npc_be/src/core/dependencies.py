# src/core/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models.user import NPCUser
from models.ch_data import ChData
from controllers.auth import get_user_from_token, get_ch_data_user_from_token
  
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> NPCUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = get_user_from_token(db, token)

    if user is None:
        raise credentials_exception
    return user

def get_current_ch_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ChData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user = get_ch_data_user_from_token(db, token)
    if user is None:
        raise credentials_exception
    return user
    
