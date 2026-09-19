from typing import Optional
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token
from app.models.domain import User, EmployeeProfile
from app.schemas.common import LoginRequest, UserResponse, TokenResponse


class AuthService:
    @staticmethod
    def authenticate(db: Session, credentials: LoginRequest) -> Optional[TokenResponse]:
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user or not verify_password(credentials.password, user.password_hash):
            return None
        if not user.is_active:
            return None

        token = create_access_token(user.email)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: str, role: str = "employee") -> User:
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


auth_service = AuthService()
