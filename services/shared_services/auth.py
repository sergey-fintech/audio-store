import sys
import os
from datetime import timedelta
from sqlalchemy.orm import Session
from typing import Optional

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from database.models import User
from services.auth.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token

class AuthService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email: str, password: str) -> User:
        hashed_password = get_password_hash(password)
        new_user = User(email=email, hashed_password=hashed_password)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_token(self, email: str) -> str:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        return access_token

    def get_current_user_from_token(self, token: str) -> Optional[User]:
        payload = verify_token(token)
        if payload is None:
            return None
        email: str = payload.get("sub")
        if email is None:
            return None
        return self.get_user_by_email(email)

