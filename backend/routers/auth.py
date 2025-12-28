"""
Authentication Router - API endpoints for authentication
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from services.auth_service import authenticate_user, get_user_restaurant
from repositories.restaurant_repo import get_restaurant_by_id
import auth

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    restaurant_id: str
    restaurant_name: str
    restaurant_phone: str
    user_name: str

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

