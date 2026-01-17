"""
Dashboard Router - API endpoints for dashboard statistics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
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
    cancelled_orders: int
    total_revenue: float
    today_revenue: float
    today_orders: int
    average_order_value: float

class RestaurantInfo(BaseModel):
    id: str
    name: str
    phone: str
    address: Optional[str] = ""  # Restaurant address
    latitude: Optional[float] = 0.0
    longitude: Optional[float] = 0.0
    is_active: bool  # Restaurant open/closed status
    upi_id: Optional[str] = ""
    upi_qr_code: Optional[str] = ""  # UPI QR code image URL or base64
    delivery_available: bool = True
    delivery_radius_km: Optional[int] = None
    minimum_order_value: float = 0.0
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    fssai_number: Optional[str] = None
    operating_hours: Optional[str] = None  # JSON string or object

class SimpleUpdateUPIRequest(BaseModel):
    """Simple request model to update UPI ID without verification flow (used from Settings page)."""
    upi_id: str

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
    cancelled_orders = len([o for o in orders if o.status == "cancelled"])
    total_revenue = sum([o.total for o in orders if o.status == "delivered"])
    
    # Calculate today's orders and revenue - handle timezone properly
    # Use UTC for consistency with database
    from datetime import timezone
    today_utc = datetime.now(timezone.utc).date()
    
    today_orders = 0
    today_revenue = 0.0
    for o in orders:
        try:
            # Parse created_at - handle both string and datetime
            if isinstance(o.created_at, str):
                # Try parsing ISO format
                if 'T' in o.created_at:
                    order_date = datetime.fromisoformat(o.created_at.replace('Z', '+00:00'))
                else:
                    # Just date string
                    order_date = datetime.strptime(o.created_at.split('T')[0], '%Y-%m-%d')
            elif hasattr(o.created_at, 'date'):
                order_date = o.created_at
            else:
                continue
            
            # Convert to date - handle timezone aware datetimes
            if hasattr(order_date, 'date'):
                if order_date.tzinfo is not None:
                    # Convert to UTC then get date
                    order_date_utc = order_date.astimezone(timezone.utc)
                    order_date_only = order_date_utc.date()
                else:
                    # Naive datetime, assume UTC
                    order_date_only = order_date.date()
            else:
                order_date_only = order_date
            
            # Compare dates
            if order_date_only == today_utc:
                today_orders += 1
                if o.status == "delivered":
                    today_revenue += o.total
        except Exception as e:
            # Log error but continue processing
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error parsing order date for order {getattr(o, 'id', 'unknown')}: {e}")
            continue
    
    # Calculate average order value
    average_order_value = 0.0
    if delivered_orders > 0:
        average_order_value = total_revenue / delivered_orders
    
    return DashboardStats(
        total_orders=total_orders,
        pending_orders=pending_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        delivered_orders=delivered_orders,
        cancelled_orders=cancelled_orders,
        total_revenue=total_revenue,
        today_revenue=today_revenue,
        today_orders=today_orders,
        average_order_value=round(average_order_value, 2)
    )

@router.get("/restaurant", response_model=RestaurantInfo)
async def get_restaurant_info(restaurant_id: str = Depends(auth.get_current_restaurant_id)):
    """Get restaurant information for current restaurant"""
    from repositories.settings_repo import get_settings_by_restaurant_id
    
    restaurant = get_restaurant_by_id(restaurant_id)
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Get settings for additional fields
    settings = get_settings_by_restaurant_id(restaurant_id)
    
    return RestaurantInfo(
        id=restaurant.id,
        name=restaurant.name,
        phone=restaurant.phone,
        address=restaurant.address or "",
        latitude=float(restaurant.latitude) if restaurant.latitude else 0.0,
        longitude=float(restaurant.longitude) if restaurant.longitude else 0.0,
        is_active=restaurant.is_active,
        upi_id=restaurant.upi_id or "",
        upi_qr_code=restaurant.upi_qr_code or "",
        delivery_available=getattr(settings, 'delivery_available', True) if settings else True,
        delivery_radius_km=getattr(settings, 'delivery_radius_km', None) if settings else None,
        minimum_order_value=float(getattr(settings, 'minimum_order_value', 0.0)) if settings else 0.0,
        gst_number=getattr(settings, 'gst_number', None) if settings else None,
        pan_number=getattr(settings, 'pan_number', None) if settings else None,
        fssai_number=getattr(settings, 'fssai_number', None) if settings else None,
        operating_hours=getattr(settings, 'operating_hours', None) if settings else None
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

@router.put("/restaurant/upi-id", response_model=RestaurantInfo)
async def update_upi_id_simple(
    request: SimpleUpdateUPIRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """
    Simple endpoint to directly update the restaurant UPI ID.
    Used from the Settings → Payments tab for manual entry or override.
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
        raise HTTPException(status_code=403, detail="You don't have permission to update this restaurant's UPI ID")

    # Validate UPI ID format
    upi_id_clean = request.upi_id.strip()
    is_valid, error_message = validate_upi_id(upi_id_clean)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Update UPI ID
    restaurant.upi_id = upi_id_clean
    updated_restaurant = update_restaurant(restaurant)

    if not updated_restaurant:
        raise HTTPException(status_code=500, detail="Failed to update UPI ID")

    # Extract Twilio number
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()

    return RestaurantInfo(
        id=updated_restaurant.id,
        name=updated_restaurant.name,
        phone=updated_restaurant.phone,
        address=updated_restaurant.address or "",
        latitude=float(updated_restaurant.latitude) if updated_restaurant.latitude else 0.0,
        longitude=float(updated_restaurant.longitude) if updated_restaurant.longitude else 0.0,
        delivery_fee=float(updated_restaurant.delivery_fee) if updated_restaurant.delivery_fee else 40.0,
        cuisine_type=updated_restaurant.cuisine_type or "both",
        upi_id=updated_restaurant.upi_id or "",
        upi_qr_code=updated_restaurant.upi_qr_code or "",
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )

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
        upi_qr_code=updated_restaurant.upi_qr_code or "",
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
    
    # Password requirement removed - any authenticated restaurant user can verify UPI
    # No password check needed - authentication is already verified via restaurant_id dependency
    
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

class SaveUPIQRCodeRequest(BaseModel):
    qr_code_data: str  # Base64 encoded QR code image or data

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
        upi_qr_code=updated_restaurant.upi_qr_code or "",
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )

@router.post("/restaurant/upi/qr-code", response_model=RestaurantInfo)
async def save_upi_qr_code(
    qr_request: SaveUPIQRCodeRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """Save UPI QR code for restaurant"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"🔍 QR Code Save Request - Restaurant: {restaurant_id}, User: {user_id}")
    
    from repositories.user_repo import get_user_by_id
    
    try:
        # Get current user
        user = get_user_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get restaurant
        restaurant = get_restaurant_by_id(restaurant_id)
        if not restaurant:
            logger.error(f"Restaurant not found: {restaurant_id}")
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Verify user owns this restaurant
        if restaurant.id != user.restaurant_id:
            logger.warning(f"User {user_id} attempted to update restaurant {restaurant_id} but owns {user.restaurant_id}")
            raise HTTPException(status_code=403, detail="You don't have permission to update this restaurant's QR code")
        
        # Validate QR code data
        qr_code_data = qr_request.qr_code_data.strip()
        if not qr_code_data:
            raise HTTPException(status_code=400, detail="QR code data cannot be empty")
        
        # Check if it's a valid format (base64 data URL or URL)
        if not (qr_code_data.startswith('data:image/') or qr_code_data.startswith('http://') or qr_code_data.startswith('https://')):
            logger.warning(f"QR code format may be invalid for restaurant {restaurant_id}")
        
        # Try to decode QR code and extract UPI ID automatically
        extracted_upi_id = None
        logger.info(f"🔍 Checking QR code format - starts with 'data:image/': {qr_code_data.startswith('data:image/')}")
        
        if qr_code_data.startswith('data:image/'):
            logger.info("📸 QR code is base64 image, attempting to decode and extract UPI ID...")
            try:
                from services.qr_decoder import decode_qr_and_extract_upi_id
                logger.info("✅ QR decoder module imported successfully")
                
                qr_string, extracted_upi_id = decode_qr_and_extract_upi_id(qr_code_data)
                logger.info(f"🔍 Decoder returned - QR string: {qr_string[:100] if qr_string else 'None'}, UPI ID: {extracted_upi_id}")
                
                if extracted_upi_id:
                    logger.info(f"✅ Automatically extracted UPI ID from QR code: {extracted_upi_id}")
                    # Update UPI ID automatically
                    restaurant.upi_id = extracted_upi_id
                    logger.info(f"✅ Set restaurant.upi_id to: {restaurant.upi_id}")
                else:
                    logger.warning(f"⚠️ Could not extract UPI ID from QR code. QR string: {qr_string[:100] if qr_string else 'None'}")
            except ImportError as ie:
                logger.error(f"❌ Failed to import QR decoder: {ie}")
                logger.error("💡 Make sure Pillow, pyzbar, and opencv-python-headless are installed in venv")
            except Exception as e:
                logger.error(f"❌ Error decoding QR code: {e}", exc_info=True)
                # Continue anyway - save QR code even if extraction fails
        else:
            logger.info(f"ℹ️ QR code is not base64 image (format: {qr_code_data[:50]}...), skipping UPI ID extraction")
        
        # Update QR code
        logger.info(f"Saving QR code for restaurant {restaurant_id}, length: {len(qr_code_data)}")
        restaurant.upi_qr_code = qr_code_data
        
        # Update restaurant (includes UPI ID if extracted)
        updated_restaurant = update_restaurant(restaurant)
        
        if not updated_restaurant:
            logger.error(f"Failed to update restaurant {restaurant_id} in database")
            raise HTTPException(status_code=500, detail="Failed to save QR code to database")
        
        # Verify it was saved
        if updated_restaurant.upi_qr_code != qr_code_data:
            logger.error(f"QR code mismatch after save for restaurant {restaurant_id}")
            raise HTTPException(status_code=500, detail="QR code was not saved correctly")
        
        logger.info(f"Successfully saved QR code for restaurant {restaurant_id}")
        
        # Log UPI ID extraction result
        if extracted_upi_id:
            logger.info(f"✅ UPI ID '{extracted_upi_id}' automatically extracted and saved from QR code")
        else:
            logger.info(f"ℹ️ UPI ID was not extracted from QR code. Current UPI ID: {updated_restaurant.upi_id or 'Not set'}")
        
        # Extract Twilio number
        from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
        twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
        
        return RestaurantInfo(
            id=updated_restaurant.id,
            name=updated_restaurant.name,
            phone=updated_restaurant.phone,
            upi_id=updated_restaurant.upi_id or "",
            upi_qr_code=updated_restaurant.upi_qr_code or "",
            twilio_number=twilio_number,
            is_active=updated_restaurant.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving QR code: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/restaurant/upi/qr-code/history")
async def get_qr_code_history(
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id),
    limit: int = Query(default=10, ge=1, le=50)
):
    """Get QR code change history (SCD Type 2)"""
    from repositories.user_repo import get_user_by_id
    from repositories.qr_code_history_repo import get_qr_code_history
    
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
        raise HTTPException(status_code=403, detail="You don't have permission to view this restaurant's QR code history")
    
    # Get history
    history = get_qr_code_history(restaurant_id, limit)
    
    return {
        "restaurant_id": restaurant_id,
        "total_versions": len(history),
        "history": history
    }

@router.post("/restaurant/upi/qr-code/revert/{version_number}")
async def revert_qr_code_version(
    version_number: int,
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    user_id: str = Depends(auth.get_current_user_id)
):
    """Revert QR code to a previous version"""
    from repositories.user_repo import get_user_by_id
    from repositories.qr_code_history_repo import revert_to_version, get_qr_code_by_version
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    
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
        raise HTTPException(status_code=403, detail="You don't have permission to revert this restaurant's QR code")
    
    # Check if version exists
    version_data = get_qr_code_by_version(restaurant_id, version_number)
    if not version_data:
        raise HTTPException(status_code=404, detail=f"Version {version_number} not found")
    
    # Revert to version
    success = revert_to_version(restaurant_id, version_number)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to revert QR code")
    
    # Get updated restaurant
    updated_restaurant = get_restaurant_by_id(restaurant_id)
    if not updated_restaurant:
        raise HTTPException(status_code=500, detail="Failed to retrieve updated restaurant")
    
    # Extract Twilio number
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    return RestaurantInfo(
        id=updated_restaurant.id,
        name=updated_restaurant.name,
        phone=updated_restaurant.phone,
        upi_id=updated_restaurant.upi_id or "",
        upi_qr_code=updated_restaurant.upi_qr_code or "",
        twilio_number=twilio_number,
        is_active=updated_restaurant.is_active
    )