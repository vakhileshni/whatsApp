"""
User Repository - Data access layer for users
Now using SQLAlchemy with PostgreSQL database
"""
from typing import Optional
from models.user import User
from database import SessionLocal
from models_db import UserDB
from model_converters import user_db_to_model, user_model_to_db


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get user by email from database
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.email.ilike(email)).first()
        if db_user:
            return user_db_to_model(db_user)
        return None
    finally:
        db.close()


def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get user by ID from database
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            return user_db_to_model(db_user)
        return None
    finally:
        db.close()


def create_user(user: User) -> Optional[User]:
    """
    Create a new user in database
    """
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(UserDB).filter(
            (UserDB.id == user.id) | (UserDB.email.ilike(user.email))
        ).first()
        if existing:
            return None  # User already exists
        
        # Create new user
        db_user = UserDB(**user_model_to_db(user))
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return user_db_to_model(db_user)
    except Exception as e:
        db.rollback()
        print(f"Error creating user: {e}")
        return None
    finally:
        db.close()


def update_user_login(user_id: str):
    """
    Update user's last login timestamp
    """
    db = SessionLocal()
    try:
        from datetime import datetime
        db_user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if db_user:
            db_user.last_login = datetime.now()
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error updating user login: {e}")
    finally:
        db.close()


def update_user(user: User) -> Optional[User]:
    """
    Update user information in database
    """
    db = SessionLocal()
    try:
        db_user = db.query(UserDB).filter(UserDB.id == user.id).first()
        if not db_user:
            return None
        
        # Update fields
        db_user.email = user.email
        db_user.password = user.password  # Should be hashed before calling this
        db_user.name = user.name
        db_user.two_factor_enabled = user.two_factor_enabled
        db_user.two_factor_secret = user.two_factor_secret or None
        db_user.two_factor_backup_codes = user.two_factor_backup_codes or None
        
        db.commit()
        db.refresh(db_user)
        return user_db_to_model(db_user)
    except Exception as e:
        db.rollback()
        print(f"Error updating user: {e}")
        return None
    finally:
        db.close()