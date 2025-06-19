from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

from .models import User, RefreshToken, UserRole
from .schemas import UserCreate, UserCreateBulk
from .auth import get_password_hash, generate_username, generate_random_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email."""
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users."""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_bulk_users(db: Session, user_bulk: UserCreateBulk) -> List[dict]:
    """Create multiple users with auto-generated credentials."""
    created_users = []
    
    for i in range(user_bulk.count):
        # Generate unique username and password
        username = generate_username(user_bulk.role, user_bulk.prefix, i + 1)
        password = generate_random_password()
        
        # Create user
        user_create = UserCreate(
            username=username,
            password=password,
            role=user_bulk.role,
            is_active=True
        )
        
        db_user = create_user(db, user_create)
        
        # Store credentials for response (password won't be stored in DB)
        created_users.append({
            "id": db_user.id,
            "username": username,
            "password": password,  # Only returned once!
            "role": user_bulk.role.value
        })
    
    return created_users


def get_refresh_token(db: Session, token: str) -> Optional[RefreshToken]:
    """Get refresh token from database."""
    return db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()


def revoke_refresh_token(db: Session, token: str) -> bool:
    """Revoke a refresh token."""
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db_token.is_revoked = True
        db.commit()
        return True
    return False


def revoke_user_refresh_tokens(db: Session, user_id: int) -> int:
    """Revoke all refresh tokens for a user."""
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    ).update({"is_revoked": True})
    db.commit()
    return count
