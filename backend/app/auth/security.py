import bcrypt
from typing import List, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from .jwt_handler import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise exc
    email = payload.get("sub")
    if not email:
        raise exc
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise exc
    return user

def require_role(allowed_roles: List[str]) -> Callable:
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = str(current_user.role.value if hasattr(current_user.role, 'value') else current_user.role)
        # Normalize comparison
        allowed_normalized = [r.upper() for r in allowed_roles]
        if user_role.upper() not in allowed_normalized and "ADMIN" not in user_role.upper():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for current user role",
            )
        return current_user
    return role_checker
