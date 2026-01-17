"""
Authentication Router - API endpoints for authentication
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from services.auth_service import authenticate_user, get_user_restaurant
from repositories.restaurant_repo import get_restaurant_by_id, create_restaurant
from repositories.user_repo import get_user_by_email, create_user, get_user_by_id
from models.restaurant import Restaurant
from models.user import User
from id_generator import generate_restaurant_id, generate_user_id
import auth

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignUpRequest(BaseModel):
    restaurant_name: str
    owner_name: str
    email: EmailStr
    password: str
    phone: str
    address: str
    latitude: float
    longitude: float

class UserInfo(BaseModel):
    user_id: str
    restaurant_id: str
    owner_name: str
    owner_email: EmailStr
    restaurant_name: str
    restaurant_phone: str

class LoginResponse(BaseModel):
    token: str  # JWT token
    user: UserInfo

class SignUpResponse(BaseModel):
    token: str  # JWT token
    user: UserInfo


class CurrentUserInfo(BaseModel):
    user_id: str
    restaurant_id: str
    owner_name: str
    owner_email: EmailStr
    restaurant_name: str
    restaurant_phone: str


@router.get("/me", response_model=CurrentUserInfo)
async def get_current_user_info(
    user_id: str = Depends(auth.get_current_user_id),
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get current logged-in user and restaurant info for account settings"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    return CurrentUserInfo(
        user_id=user.id,
        restaurant_id=restaurant.id,
        owner_name=user.name,
        owner_email=user.email,
        restaurant_name=restaurant.name,
        restaurant_phone=restaurant.phone,
    )

@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """Restaurant admin login"""
    user = authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    restaurant = get_restaurant_by_id(user.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=500, detail="Restaurant not found")
    
    access_token = auth.create_access_token(user.id, user.restaurant_id)
    
    return LoginResponse(
        token=access_token,
        user=UserInfo(
            user_id=user.id,
            restaurant_id=user.restaurant_id,
            owner_name=user.name,
            owner_email=user.email,
            restaurant_name=restaurant.name,
            restaurant_phone=restaurant.phone
        )
    )

@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(signup_data: SignUpRequest):
    """Restaurant registration/signup"""
    # Check if email already exists
    existing_user = get_user_by_email(signup_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    
    # Generate IDs using ID generator (9-digit format)
    restaurant_id = generate_restaurant_id()
    user_id = generate_user_id()
    
    # Create restaurant
    restaurant = Restaurant(
        id=restaurant_id,
        name=signup_data.restaurant_name,
        phone=signup_data.phone,
        address=signup_data.address,
        latitude=signup_data.latitude,
        longitude=signup_data.longitude,
        delivery_fee=40.0,  # Default delivery fee
        is_active=True,
        upi_id="",  # Can be set later
        cuisine_type="both"  # Default cuisine type
    )
    
    created_restaurant = create_restaurant(restaurant)
    if not created_restaurant:
        raise HTTPException(status_code=500, detail="Failed to create restaurant")
    
    # Create user
    user = User(
        id=user_id,
        email=signup_data.email,
        password=signup_data.password,  # In production, hash this
        restaurant_id=restaurant_id,
        name=signup_data.owner_name
    )
    
    created_user = create_user(user)
    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")
    
    # Create JWT token for immediate login
    access_token = auth.create_access_token(user_id, restaurant_id)
    
    return SignUpResponse(
        token=access_token,
        user=UserInfo(
            user_id=user_id,
            restaurant_id=restaurant_id,
            owner_name=signup_data.owner_name,
            owner_email=signup_data.email,
            restaurant_name=signup_data.restaurant_name,
            restaurant_phone=signup_data.phone
        )
    )


class UpdateAccountRequest(BaseModel):
    owner_name: Optional[str] = None
    owner_email: Optional[EmailStr] = None
    restaurant_phone: Optional[str] = None
    current_password: Optional[str] = None  # Required if changing password
    new_password: Optional[str] = None  # Optional: only if changing password
    two_factor_enabled: Optional[bool] = None


class UpdateAccountResponse(BaseModel):
    message: str


@router.put("/account", response_model=UpdateAccountResponse)
async def update_account(
    account_data: UpdateAccountRequest,
    user_id: str = Depends(auth.get_current_user_id),
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update account details (name, email, phone, password)"""
    from repositories.user_repo import update_user
    from repositories.restaurant_repo import get_restaurant_by_id, update_restaurant
    from services.auth_service import authenticate_user
    
    # Get current user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Update owner name if provided
    if account_data.owner_name is not None:
        user.name = account_data.owner_name
    
    # Update email if provided
    if account_data.owner_email is not None:
        # Check if email is being changed and if new email already exists
        if account_data.owner_email != user.email:
            existing_user = get_user_by_email(account_data.owner_email)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
        user.email = account_data.owner_email
    
    # Update restaurant phone if provided
    if account_data.restaurant_phone is not None:
        restaurant.phone = account_data.restaurant_phone
        update_restaurant(restaurant)
    
    # If changing password, verify current password
    if account_data.new_password:
        if not account_data.current_password:
            raise HTTPException(status_code=400, detail="Current password is required to change password")
        
        # Verify current password
        authenticated_user = authenticate_user(user.email, account_data.current_password)
        if not authenticated_user:
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        # Update password (in production, hash this)
        user.password = account_data.new_password
    
    # Update two-factor if provided
    if account_data.two_factor_enabled is not None:
        user.two_factor_enabled = account_data.two_factor_enabled
        
        # If enabling MFA for the first time, generate secret (simplified - in production use proper TOTP)
        if account_data.two_factor_enabled and not getattr(user, 'two_factor_enabled', False):
            import secrets
            user.two_factor_secret = secrets.token_hex(16)  # Simplified - use proper TOTP in production
            # Generate backup codes
            import json
            backup_codes = [secrets.token_hex(4) for _ in range(10)]
            user.two_factor_backup_codes = json.dumps(backup_codes)
        
        # If disabling MFA, clear secret and backup codes
        if not account_data.two_factor_enabled and getattr(user, 'two_factor_enabled', False):
            user.two_factor_secret = ""
            user.two_factor_backup_codes = ""
    
    # Update user in database
    updated_user = update_user(user)
    if not updated_user:
        raise HTTPException(status_code=500, detail="Failed to update account")
    
    return UpdateAccountResponse(
        message="Account updated successfully"
    )