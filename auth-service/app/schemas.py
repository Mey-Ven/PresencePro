from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .models import UserRole


class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserCreateBulk(BaseModel):
    role: UserRole
    count: int
    prefix: Optional[str] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[UserRole] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RoleCheck(BaseModel):
    required_roles: list[UserRole]
