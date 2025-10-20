from sqlalchemy.orm import Session
from models.user import NPCUser
from core.security import verify_password


def authenticate_user(db: Session, id_number: str, password: str) -> NPCUser | None:
    user = db.query(NPCUser).filter(NPCUser.id_number == id_number).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user
