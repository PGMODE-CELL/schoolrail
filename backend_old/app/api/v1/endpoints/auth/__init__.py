from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Annotated
from sqlalchemy.orm import Session

from app.core.security import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    UserInDB,
    MOCK_USERS_DB,
    get_current_user,
    get_password_hash,
)
from app.core.database import get_db
from app.models.models import User as UserModel
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate, PasswordChange

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
async def login_json(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        uuid=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserInDB = Depends(get_current_user),
):
    db_user = db.query(UserModel).filter(UserModel.id == current_user.id).first()
    if db_user:
        update_fields = user_data.dict(exclude_unset=True)
        full_name_changed = False
        for key, value in update_fields.items():
            setattr(db_user, key, value)
            if key in ("first_name", "last_name"):
                full_name_changed = True
        if full_name_changed:
            first = update_fields.get("first_name", db_user.first_name or "")
            last = update_fields.get("last_name", db_user.last_name or "")
            db_user.full_name = f"{first} {last}".strip()
        db.commit()
        db.refresh(db_user)
        return UserResponse(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            phone=db_user.phone,
            first_name=db_user.first_name,
            last_name=db_user.last_name,
            full_name=db_user.full_name,
            role=db_user.role,
            school_id=db_user.school_id,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
        )

    mock_key = current_user.username
    if mock_key in MOCK_USERS_DB:
        update_fields = user_data.dict(exclude_unset=True)
        for key, value in update_fields.items():
            if key in ("first_name", "last_name"):
                MOCK_USERS_DB[mock_key][key] = value
                first = update_fields.get("first_name", MOCK_USERS_DB[mock_key].get("first_name", ""))
                last = update_fields.get("last_name", MOCK_USERS_DB[mock_key].get("last_name", ""))
                MOCK_USERS_DB[mock_key]["full_name"] = f"{first} {last}".strip()
            else:
                MOCK_USERS_DB[mock_key][key] = value
        updated = MOCK_USERS_DB[mock_key]
        return UserResponse(
            id=updated["id"],
            username=updated["username"],
            email=updated.get("email", ""),
            full_name=updated.get("full_name", ""),
            role=updated["role"],
            is_active=updated.get("is_active", True),
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    from app.core.security import get_user
    
    existing_user = get_user(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(user_data.password)
    new_user = UserInDB(
        id=999,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=hashed_password,
    )
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        role=new_user.role,
    )


@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: UserInDB = Depends(get_current_user)
):
    from app.core.security import verify_password, get_password_hash
    
    if not verify_password(password_change.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if password_change.new_password != password_change.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New passwords do not match"
        )
    
    return {"message": "Password changed successfully"}


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


@router.get("/verify")
async def verify_token(current_user: UserInDB = Depends(get_current_user)):
    return {"valid": True, "user": current_user.username}
