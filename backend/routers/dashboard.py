"""
Dashboard Router - API endpoints for dashboard statistics
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from repositories.order_repo import get_orders_by_restaurant
from repositories.restaurant_repo import get_restaurant_by_id, update_restaurant
import auth
import re

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

class DashboardStats(BaseModel):
    total_orders: int
    pending_orders: int
    preparing_orders: int
    ready_orders: int
    delivered_orders: int
    total_revenue: float
    today_orders: int

class RestaurantInfo(BaseModel):
    id: str
    name: str
    phone: str
    upi_id: str
    twilio_number: str  # WhatsApp Business number for QR codes

class UpdateUPIRequest(BaseModel):
    upi_id: str
    password: str  # Owner password for security

class VerifyPaymentRequest(BaseModel):
    customer_upi_name: str

class VerifyUPIRequest(BaseModel):
    upi_id: str
    password: str

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(restaurant_id: str = Depends(auth.get_current_restaurant_id)):
    """Get dashboard statistics for current restaurant"""
    orders = get_orders_by_restaurant(restaurant_id)
    
    today = datetime.now().date()
    
    total_orders = len(orders)
    pending_orders = len([o for o in orders if o.status == "pending"])
    preparing_orders = len([o for o in orders if o.status == "preparing"])
    ready_orders = len([o for o in orders if o.status == "ready"])
    delivered_orders = len([o for o in orders if o.status == "delivered"])
    total_revenue = sum([o.total for o in orders if o.status == "delivered"])
    
    today_orders = len([
        o for o in orders 
        if datetime.fromisoformat(o.created_at).date() == today
    ])
    
    return DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        delivered_orders=delivered_orders,
        total_revenue=total_revenue,
        today_orders=today_orders
    )

@router.get("/restaurant", response_model=RestaurantInfo)
async def get_restaurant_info(restaurant_id: str = Depends(auth.get_current_restaurant_id)):
    """Get restaurant information for current restaurant"""
    import os
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    
    restaurant = get_restaurant_by_id(restaurant_id)
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Extract Twilio number from format "whatsapp:+14155238886" to "14155238886"
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    return RestaurantInfo(
        id=restaurant.id,
        name=restaurant.name,
        phone=restaurant.phone,
        upi_id=restaurant.upi_id or "",
        twilio_number=twilio_number
    )

def validate_upi_id(upi_id: str):
    """
    Validate UPI ID format
    Returns: (is_valid, error_message)
    
    Valid UPI formats:
    - username@paytm
    - username@upi
    - username@bank (e.g., username@ybl, username@okaxis, username@oksbi)
    - phone@upi (e.g., 1234567890@upi)
    - phone@paytm (e.g., 1234567890@paytm)
    """
    upi_id = upi_id.strip()
    
    # Basic checks
    if not upi_id:
        return False, "UPI ID cannot be empty"
    
    if len(upi_id) < 5 or len(upi_id) > 100:
        return False, "UPI ID must be between 5 and 100 characters"
    
    # UPI ID format: handle@provider
    # Pattern: alphanumeric characters, dots, hyphens, underscores, followed by @ and provider
    upi_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9]+$'
    
    if not re.match(upi_pattern, upi_id):
        return False, "Invalid UPI ID format. Use format: username@bank or phone@upi (e.g., restaurant@paytm or 1234567890@upi)"
    
    # Split by @ to check parts
    parts = upi_id.split('@')
    if len(parts) != 2:
        return False, "UPI ID must contain exactly one @ symbol"
    
    handle, provider = parts
    
    # Validate handle (before @)
    if not handle or len(handle) < 3:
        return False, "UPI handle (before @) must be at least 3 characters"
    
    if not re.match(r'^[a-zA-Z0-9._-]+$', handle):
        return False, "UPI handle can only contain letters, numbers, dots, hyphens, and underscores"
    
    # Validate provider (after @)
    if not provider or len(provider) < 2:
        return False, "UPI provider (after @) must be at least 2 characters"
    
    # Common valid providers
    valid_providers = ['paytm', 'upi', 'ybl', 'okaxis', 'oksbi', 'okhdfcbank', 'okicici', 'payu', 'phonepe', 'gpay', 'amazonpay']
    provider_lower = provider.lower()
    
    # Allow any alphanumeric provider (flexible), but warn about common ones
    if not re.match(r'^[a-zA-Z0-9]+$', provider):
        return False, "UPI provider can only contain letters and numbers"
    
    return True, ""

@router.put("/restaurant/upi", response_model=RestaurantInfo)
async def update_restaurant_upi(
    upi_request: UpdateUPIRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """Update restaurant UPI ID (password protected and validated)"""
    from repositories.user_repo import get_user_by_id
    
    # Get current user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if user.password != upi_request.password:
        raise HTTPException(status_code=401, detail="Invalid password. Only owner can update UPI details.")
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Verify user owns this restaurant
    if restaurant.id != user.restaurant_id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this restaurant's UPI")
    
    # Validate UPI ID format
    upi_id_clean = upi_request.upi_id.strip()
    is_valid, error_message = validate_upi_id(upi_id_clean)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Update UPI ID
    restaurant.upi_id = upi_id_clean
    updated_restaurant = update_restaurant(restaurant)
    
    if not updated_restaurant:
        raise HTTPException(status_code=500, detail="Failed to update UPI ID")
    
    # Extract Twilio number from format "whatsapp:+14155238886" to "14155238886"
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    return RestaurantInfo(
        id=updated_restaurant.id,
        name=updated_restaurant.name,
        phone=updated_restaurant.phone,
        upi_id=updated_restaurant.upi_id,
        twilio_number=twilio_number
    )

def generate_upi_payment_qr_data(upi_id: str, amount: float = 1.0, merchant_name: str = "Test Payment") -> str:
    """
    Generate UPI payment QR code data string
    Format: upi://pay?pa=<UPI_ID>&pn=<MerchantName>&am=<Amount>&cu=INR&tn=<TransactionNote>
    """
    import urllib.parse
    encoded_name = urllib.parse.quote(merchant_name)
    encoded_note = urllib.parse.quote("UPI Verification Test")
    
    # Format: upi://pay?pa=<UPI_ID>&pn=<MerchantName>&am=<Amount>&cu=INR&tn=<TransactionNote>
    qr_data = f"upi://pay?pa={upi_id}&pn={encoded_name}&am={amount:.2f}&cu=INR&tn={encoded_note}"
    return qr_data

class VerifyUPIRequest(BaseModel):
    upi_id: str
    password: str

@router.post("/restaurant/upi/verify")
async def verify_restaurant_upi(
    verify_request: VerifyUPIRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """
    Verify UPI ID by generating a test payment QR code
    Restaurant owner scans QR code and makes a test payment to verify UPI is correct
    """
    from repositories.user_repo import get_user_by_id
    
    # Get current user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify password
    if user.password != verify_request.password:
        raise HTTPException(status_code=401, detail="Invalid password. Only owner can verify UPI details.")
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Verify user owns this restaurant
    if restaurant.id != user.restaurant_id:
        raise HTTPException(status_code=403, detail="You don't have permission to verify this restaurant's UPI")
    
    # Validate UPI ID format first
    upi_id_clean = verify_request.upi_id.strip()
    is_valid, error_message = validate_upi_id(upi_id_clean)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Generate UPI payment QR code data
    qr_data = generate_upi_payment_qr_data(upi_id_clean, amount=1.0, merchant_name=restaurant.name)
    
    return {
        "status": "success",
        "message": "UPI QR code generated for verification",
        "upi_id": upi_id_clean,
        "qr_data": qr_data,
        "verification_amount": 1.0,
        "instructions": "Scan this QR code with any UPI app (PhonePe, Google Pay, Paytm) and send ₹1.00 to verify this UPI ID belongs to you."
    }

