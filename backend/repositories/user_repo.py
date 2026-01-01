"""
User Repository - Data access layer for users
Later: Replace with SQLAlchemy queries
"""
from typing import Optional
from models.user import User
from data.users_data import USERS

def get_user_by_email(email: str) -> Optional[User]:
    """
    Get user by email
    Later: SELECT * FROM users WHERE email = ?
    """
    for user in USERS.values():
        if user.email.lower() == email.lower():
            return user
    return None

def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get user by ID
    Later: SELECT * FROM users WHERE id = ?
    """
    return USERS.get(user_id)

def create_user(user: User) -> Optional[User]:
    """
    Create a new user
    Later: INSERT INTO users (...) VALUES (...)
    """
    if user.id in USERS:
        return None  # User already exists
    USERS[user.id] = user
    return user


