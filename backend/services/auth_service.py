"""
Authentication Service - Business logic for authentication
"""
from typing import Optional
from models.user import User
from models.restaurant import Restaurant
from repositories.user_repo import get_user_by_email, get_user_by_id
from repositories.restaurant_repo import get_restaurant_by_id

def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate user with email and password
    Business logic: Validate credentials
    """
    user = get_user_by_email(email)
    
    if not user:
        return None
    
    if user.password != password:
        return None
    
    # Verify restaurant is active
    restaurant = get_restaurant_by_id(user.restaurant_id)
    if not restaurant or not restaurant.is_active:
        return None
    
    return user

def get_user_restaurant(user_id: str) -> Optional[Restaurant]:
    """
    Get restaurant for a user
    """
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    return get_restaurant_by_id(user.restaurant_id)

