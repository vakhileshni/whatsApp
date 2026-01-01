"""
Authentication Router - API endpoints for authentication
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.auth_service import authenticate_user, get_user_restaurant
from repositories.restaurant_repo import get_restaurant_by_id, create_restaurant
from repositories.user_repo import get_user_by_email, create_user
from models.restaurant import Restaurant
from models.user import User
import auth
import uuid

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

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    restaurant_id: str
    restaurant_name: str
    restaurant_phone: str
    user_name: str

class SignUpResponse(BaseModel):
    message: str
    restaurant_id: str
    user_id: str

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
        access_token=access_token,
        user_id=user.id,
        restaurant_id=user.restaurant_id,
        restaurant_name=restaurant.name,
        restaurant_phone=restaurant.phone,
        user_name=user.name
    )

@router.post("/signup", response_model=SignUpResponse)
async def signup(signup_data: SignUpRequest):
    """Restaurant registration/signup"""
    # Check if email already exists
    existing_user = get_user_by_email(signup_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate IDs
    restaurant_id = f"rest_{str(uuid.uuid4())[:8]}"
    user_id = f"user_{str(uuid.uuid4())[:8]}"
    
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
    
    return SignUpResponse(
        message="Account created successfully. Please login.",
        restaurant_id=restaurant_id,
        user_id=user_id
    )

