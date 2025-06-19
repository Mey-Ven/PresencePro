from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta

from .database import get_db
from .schemas import (
    UserCreate, UserCreateBulk, UserResponse, UserLogin, 
    Token, RefreshTokenRequest, RoleCheck, TokenData
)
from .models import User, UserRole
from .auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_current_user, require_roles, verify_token
)
from .crud import (
    create_user, create_bulk_users, get_user_by_username, 
    get_refresh_token, revoke_refresh_token, get_user
)
from .config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Register a new user (Admin only)."""
    # Check if username already exists
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Create user
    db_user = create_user(db, user)
    return db_user


@router.post("/register/bulk", status_code=status.HTTP_201_CREATED)
async def register_bulk_users(
    user_bulk: UserCreateBulk,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    """Generate multiple users with auto-generated credentials (Admin only)."""
    if user_bulk.count <= 0 or user_bulk.count > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count must be between 1 and 100"
        )
    
    created_users = create_bulk_users(db, user_bulk)
    
    return {
        "message": f"Successfully created {len(created_users)} users",
        "users": created_users,
        "warning": "Save these credentials! Passwords won't be shown again."
    }


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token = create_refresh_token(user.id, db)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    # Verify refresh token
    db_token = get_refresh_token(db, refresh_request.refresh_token)
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = get_user(db, db_token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        },
        expires_delta=access_token_expires
    )
    
    # Create new refresh token and revoke old one
    revoke_refresh_token(db, refresh_request.refresh_token)
    new_refresh_token = create_refresh_token(user.id, db)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }


@router.post("/roles/check")
async def check_user_roles(
    role_check: RoleCheck,
    current_user: User = Depends(get_current_user)
):
    """Check if current user has required roles."""
    has_permission = current_user.role in role_check.required_roles
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "current_role": current_user.role.value,
        "required_roles": [role.value for role in role_check.required_roles],
        "has_permission": has_permission
    }


@router.get("/roles/me")
async def get_my_role(current_user: User = Depends(get_current_user)):
    """Get current user's role and information."""
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "is_active": current_user.is_active
    }


@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout user by revoking refresh token."""
    revoked = revoke_refresh_token(db, refresh_request.refresh_token)
    
    return {
        "message": "Successfully logged out" if revoked else "Token already invalid"
    }
