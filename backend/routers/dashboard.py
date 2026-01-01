"""
Dashboard Router - API endpoints for dashboard statistics
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime, timedelta
import uuid
from repositories.order_repo import get_orders_by_restaurant
from repositories.restaurant_repo import get_restaurant_by_id, update_restaurant
import auth
import re

# In-memory storage for UPI verification codes (in production, use Redis or database)
_upi_verification_codes: Dict[str, Dict] = {}

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
    is_active: bool  # Restaurant open/closed status

class UpdateUPIRequest(BaseModel):
    upi_id: str
    password: str  # UPI management password (separate from login password)
    new_password: Optional[str] = None  # Optional: set new UPI password

class VerifyPaymentRequest(BaseModel):
    customer_upi_name: str

class VerifyUPIRequest(BaseModel):
    upi_id: str
    password: str

class ConfirmUPIVerificationRequest(BaseModel):
    verification_code: str
    upi_id: str
    password: str
    new_password: Optional[str] = None

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
        twilio_number=twilio_number,
        is_active=restaurant.is_active
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

@router.post("/restaurant/upi/confirm-verification")
async def confirm_upi_verification(
    confirm_request: ConfirmUPIVerificationRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """Confirm UPI verification and update UPI ID after successful verification"""
    from repositories.user_repo import get_user_by_id
    
    # Get current user
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Verify user owns this restaurant
    if restaurant.id != user.restaurant_id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this restaurant's UPI")
    
    # Verify UPI password (separate from login password)
    if not restaurant.upi_password:
        if user.password != confirm_request.password:
            raise HTTPException(status_code=401, detail="Invalid password. Please use your login password for first-time setup.")
    else:
        if restaurant.upi_password != confirm_request.password:
            raise HTTPException(status_code=401, detail="Invalid UPI password. Please enter the correct UPI management password.")
    
    # Validate UPI ID format
    upi_id_clean = confirm_request.upi_id.strip()
    is_valid, error_message = validate_upi_id(upi_id_clean)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Check verification code
    verification_key = f"{restaurant_id}:{upi_id_clean}"
    verification_data = _upi_verification_codes.get(verification_key)
    
    if not verification_data:
        raise HTTPException(status_code=400, detail="Verification code not found. Please verify UPI first.")
    
    # Check if expired
    if datetime.now() > verification_data["expires_at"]:
        del _upi_verification_codes[verification_key]
        raise HTTPException(status_code=400, detail="Verification code has expired. Please verify UPI again.")
    
    # Verify the code matches
    if verification_data["verification_code"] != confirm_request.verification_code:
        raise HTTPException(status_code=400, detail="Invalid verification code. Please check the code from your payment transaction.")
    
    # Mark as verified and update UPI ID
    restaurant.upi_id = upi_id_clean
    
    # Update UPI password if new_password is provided
    if confirm_request.new_password:
        restaurant.upi_password = confirm_request.new_password
    
    updated_restaurant = update_restaurant(restaurant)
    
    if not updated_restaurant:
        raise HTTPException(status_code=500, detail="Failed to update UPI ID")
    
    # Clean up verification code
    del _upi_verification_codes[verification_key]
    
    # Extract Twilio number
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    return RestaurantInfo(
        id=updated_restaurant.id,
        name=updated_restaurant.name,
        phone=updated_restaurant.phone,
        upi_id=updated_restaurant.upi_id,
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )
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
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )

def generate_upi_payment_qr_data(upi_id: str, amount: float = 1.0, merchant_name: str = "Test Payment", transaction_note: str = "UPI Verification Test") -> str:
    """
    Generate UPI payment QR code data string
    Format: upi://pay?pa=<UPI_ID>&pn=<MerchantName>&am=<Amount>&cu=INR&tn=<TransactionNote>
    """
    import urllib.parse
    encoded_name = urllib.parse.quote(merchant_name)
    encoded_note = urllib.parse.quote(transaction_note)
    
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
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Verify user owns this restaurant
    if restaurant.id != user.restaurant_id:
        raise HTTPException(status_code=403, detail="You don't have permission to verify this restaurant's UPI")
    
    # Verify UPI password (separate from login password)
    # If no UPI password is set yet, use login password for first-time setup
    if not restaurant.upi_password:
        # First time setup - use login password
        if user.password != verify_request.password:
            raise HTTPException(status_code=401, detail="Invalid password. Please use your login password for first-time setup.")
    else:
        # UPI password is set - use UPI password
        if restaurant.upi_password != verify_request.password:
            raise HTTPException(status_code=401, detail="Invalid UPI password. Please enter the correct UPI management password.")
    
    # Validate UPI ID format first
    upi_id_clean = verify_request.upi_id.strip()
    is_valid, error_message = validate_upi_id(upi_id_clean)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Generate unique verification code (6-digit number)
    verification_code = str(uuid.uuid4().int % 1000000).zfill(6)
    
    # Store verification attempt (expires in 10 minutes)
    verification_key = f"{restaurant_id}:{upi_id_clean}"
    _upi_verification_codes[verification_key] = {
        "verification_code": verification_code,
        "upi_id": upi_id_clean,
        "restaurant_id": restaurant_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(minutes=10),
        "verified": False
    }
    
    # Generate UPI payment QR code data with verification code in transaction note
    transaction_note = f"UPI Verification Code: {verification_code}"
    qr_data = generate_upi_payment_qr_data(upi_id_clean, amount=1.0, merchant_name=restaurant.name, transaction_note=transaction_note)
    
    return {
        "status": "success",
        "message": "UPI QR code generated for verification",
        "upi_id": upi_id_clean,
        "qr_data": qr_data,
        "verification_code": verification_code,
        "verification_amount": 1.0,
        "instructions": f"Scan this QR code with any UPI app (PhonePe, Google Pay, Paytm) and send ₹1.00 to verify this UPI ID. After payment, enter verification code: {verification_code}"
    }

class UpdateRestaurantStatusRequest(BaseModel):
    is_active: bool

@router.patch("/restaurant/status", response_model=RestaurantInfo)
async def update_restaurant_status(
    status_request: UpdateRestaurantStatusRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update restaurant open/closed status"""
    restaurant = get_restaurant_by_id(restaurant_id)
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Update restaurant status
    restaurant.is_active = status_request.is_active
    updated_restaurant = update_restaurant(restaurant)
    
    if not updated_restaurant:
        raise HTTPException(status_code=500, detail="Failed to update restaurant status")
    
    # Extract Twilio number from format "whatsapp:+14155238886" to "14155238886"
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    return RestaurantInfo(
        id=updated_restaurant.id,
        name=updated_restaurant.name,
        phone=updated_restaurant.phone,
        upi_id=updated_restaurant.upi_id or "",
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )

