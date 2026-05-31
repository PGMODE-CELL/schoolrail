from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[str] = None
    school_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    hashed_password: str
    created_at: Optional[datetime] = None
    school_id: Optional[int] = None


MOCK_USERS_DB = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@schoolrail.com",
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True,
        "hashed_password": "$2b$12$zET9gW5PWnwSzzLIQlyx5u6yegwpKuTJWTChwSyTIYmGM7CSNT0XW",
        "created_at": datetime.now(),
    },
    "driver1": {
        "id": 2,
        "username": "driver1",
        "email": "driver1@schoolrail.com",
        "full_name": "Rajesh Kumar",
        "role": "driver",
        "is_active": True,
        "hashed_password": "$2b$12$zET9gW5PWnwSzzLIQlyx5u6yegwpKuTJWTChwSyTIYmGM7CSNT0XW",
        "created_at": datetime.now(),
    },
    "parent1": {
        "id": 3,
        "username": "parent1",
        "email": "parent1@schoolrail.com",
        "full_name": "Priya Sharma",
        "role": "parent",
        "is_active": True,
        "hashed_password": "$2b$12$zET9gW5PWnwSzzLIQlyx5u6yegwpKuTJWTChwSyTIYmGM7CSNT0XW",
        "created_at": datetime.now(),
    },
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("$2b$"):
        return pwd_context.verify(plain_password, hashed_password)
    return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(username_or_email: str) -> Optional[UserInDB]:
    try:
        from app.core.database import SessionLocal
        from app.models.models import User as UserModel
        db = SessionLocal()
        db_user = db.query(UserModel).filter(
            (UserModel.username == username_or_email) |
            (UserModel.email == username_or_email)
        ).first()
        db.close()
        if db_user:
            return UserInDB(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email or "",
                full_name=db_user.full_name or db_user.username,
                role=db_user.role,
                is_active=db_user.is_active,
                hashed_password=db_user.password_hash,
                created_at=db_user.created_at,
                school_id=getattr(db_user, 'school_id', None),
            )
    except Exception:
        pass
    if username_or_email in MOCK_USERS_DB:
        user_dict = MOCK_USERS_DB[username_or_email]
        user_dict.setdefault('school_id', None)
        return UserInDB(**user_dict)
    return None


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub", 0))
        username: str = payload.get("username")
        role: str = payload.get("role")
        if not user_id and not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return TokenData(user_id=user_id, username=username, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInDB:
    token = credentials.credentials
    token_data = decode_token(token)
    
    if token_data.username:
        user = get_user(token_data.username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(allowed_roles: list):
    """Dependency to require specific roles"""
    async def role_checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    def __call__(self, user: UserInDB = Depends(get_current_user)) -> UserInDB:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return user


def require_admin(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


def require_driver_or_admin(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if user.role not in ["admin", "driver"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Driver or Admin access required"
        )
    return user


def require_parent_or_admin(user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if user.role not in ["admin", "parent"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Parent or Admin access required"
        )
    return user
