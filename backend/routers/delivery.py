"""
Delivery Router - API endpoints for delivery persons
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from repositories.order_repo import get_orders_by_restaurant, get_order_by_id
from repositories.restaurant_repo import get_restaurant_by_id
from repositories.delivery_person_repo import (
    get_delivery_person_by_email, 
    get_delivery_person_by_phone,
    create_delivery_person
)
from services.order_service import update_order_status_safe
from models.delivery_person import DeliveryPerson
from id_generator import generate_delivery_person_id
import auth
import logging

logger = logging.getLogger(__name__)

# Try to import passlib, fallback to bcrypt directly if not available
try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    HAS_PASSLIB = True
except ImportError:
    # Fallback to bcrypt directly if passlib is not available
    try:
        import bcrypt
        pwd_context = None  # Will use bcrypt directly
        HAS_PASSLIB = False
        logger.warning("passlib not available, using bcrypt directly")
    except ImportError:
        pwd_context = None
        HAS_PASSLIB = False
        logger.error(
            "Neither passlib nor bcrypt is available. "
            "Password hashing will fail. Please install with: pip install passlib[bcrypt]"
        )
        # Don't raise here - let the server start, but password hashing will fail at runtime

router = APIRouter(prefix="/api/v1/delivery", tags=["delivery"])

class DeliveryPersonCreate(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    vehicle_type: Optional[str] = "bike"  # bike, car, scooter
    license_number: Optional[str] = None

class SignUpResponse(BaseModel):
    message: str
    delivery_person_id: str

class DeliveryPersonResponse(BaseModel):
    id: str
    name: str
    phone: str
    email: str
    vehicle_type: str
    is_available: bool
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    created_at: str

class UpdateAvailabilityRequest(BaseModel):
    is_available: bool

class UpdateLocationRequest(BaseModel):
    latitude: float
    longitude: float

class DeliveryOrderResponse(BaseModel):
    order_id: str
    restaurant_id: str
    restaurant_name: str
    restaurant_address: str
    customer_name: str
    customer_phone: str
    delivery_address: str
    customer_latitude: Optional[float] = None
    customer_longitude: Optional[float] = None
    total_amount: float
    order_items: List[dict]
    created_at: str
    status: str

@router.post("/signup", response_model=SignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup_delivery_person(person_data: DeliveryPersonCreate):
    """Register a new delivery person"""
    try:
        # Validate required fields
        if not person_data.name or not person_data.phone or not person_data.email or not person_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All required fields (name, phone, email, password) must be provided"
            )
        
        # Validate password length
        if len(person_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Validate vehicle type
        valid_vehicle_types = ["bike", "scooter", "car"]
        vehicle_type = person_data.vehicle_type.lower() if person_data.vehicle_type else "bike"
        if vehicle_type not in valid_vehicle_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vehicle type must be one of: {', '.join(valid_vehicle_types)}"
            )
        
        # Check if email already exists
        existing_email = get_delivery_person_by_email(person_data.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Check if phone already exists
        existing_phone = get_delivery_person_by_phone(person_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Phone number already registered"
            )
        
        # Hash password
        if HAS_PASSLIB and pwd_context:
            password_hash = pwd_context.hash(person_data.password)
        else:
            # Fallback to bcrypt directly
            try:
                import bcrypt
                salt = bcrypt.gensalt()
                password_hash = bcrypt.hashpw(person_data.password.encode('utf-8'), salt).decode('utf-8')
            except ImportError:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Password hashing library not available. Please install passlib[bcrypt] or bcrypt."
                )
        
        # Generate unique ID
        delivery_person_id = generate_delivery_person_id()
        
        # Create delivery person model
        delivery_person = DeliveryPerson(
            id=delivery_person_id,
            name=person_data.name.strip(),
            phone=person_data.phone.strip(),
            email=person_data.email.lower().strip(),
            password_hash=password_hash,
            vehicle_type=vehicle_type,
            license_number=person_data.license_number.strip() if person_data.license_number else None,
            is_available=False
        )
        
        # Insert into database
        created_person = create_delivery_person(delivery_person)
        if not created_person:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create delivery person account"
            )
        
        logger.info(f"Delivery person created successfully: {delivery_person_id} ({person_data.email})")
        
        return SignUpResponse(
            message="Signup successful",
            delivery_person_id=delivery_person_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating delivery person: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/login")
async def login_delivery_person(email: str, password: str):
    """Login for delivery person"""
    # TODO: Implement delivery person login
    raise HTTPException(status_code=501, detail="Delivery person login not yet implemented")

@router.get("/me", response_model=DeliveryPersonResponse)
async def get_delivery_person_info():
    """Get current delivery person info"""
    # TODO: Implement get delivery person info
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.patch("/availability")
async def update_availability(request: UpdateAvailabilityRequest):
    """Update delivery person availability status"""
    # TODO: Implement availability update
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.post("/location")
async def update_location(request: UpdateLocationRequest):
    """Update delivery person's current location"""
    # TODO: Implement location update
    raise HTTPException(status_code=501, detail="Not yet implemented")

@router.get("/orders", response_model=List[DeliveryOrderResponse])
async def get_delivery_orders():
    """Get available delivery orders (orders with delivery type and ready status)"""
    # Get all restaurants
    from repositories.restaurant_repo import get_all_restaurants
    restaurants = get_all_restaurants()
    
    delivery_orders = []
    for restaurant in restaurants:
        # Get orders for this restaurant
        orders = get_orders_by_restaurant(restaurant.id)
        
        # Filter for delivery orders that are ready
        for order in orders:
            if order.order_type == "delivery" and order.status == "ready":
                delivery_orders.append({
                    "order_id": order.id,
                    "restaurant_id": restaurant.id,
                    "restaurant_name": restaurant.name,
                    "restaurant_address": restaurant.address or "",
                    "customer_name": order.customer_name,
                    "customer_phone": order.customer_phone,
                    "delivery_address": order.delivery_address or "",
                    "customer_latitude": None,  # TODO: Get from order if stored
                    "customer_longitude": None,  # TODO: Get from order if stored
                    "total_amount": order.total_amount,
                    "order_items": [
                        {
                            "product_name": item.product_name,
                            "quantity": item.quantity,
                            "price": item.price
                        }
                        for item in order.items
                    ],
                    "created_at": order.created_at.isoformat() if hasattr(order.created_at, 'isoformat') else str(order.created_at),
                    "status": order.status
                })
    
    return delivery_orders

@router.post("/orders/{order_id}/accept")
async def accept_delivery_order(order_id: str):
    """Accept a delivery order"""
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.order_type != "delivery":
        raise HTTPException(status_code=400, detail="Order is not a delivery order")
    
    if order.status != "ready":
        raise HTTPException(status_code=400, detail="Order is not ready for delivery")
    
    # TODO: Assign order to delivery person
    # For now, just update status to "out_for_delivery" or similar
    # This would require adding a new status or delivery_person_id field
    
    return {"message": "Order accepted for delivery", "order_id": order_id}

@router.post("/orders/{order_id}/complete")
async def complete_delivery_order(order_id: str):
    """Mark delivery order as completed"""
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update order status to delivered
    restaurant = get_restaurant_by_id(order.restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    updated_order, old_status = update_order_status_safe(order_id, "delivered", restaurant.id)
    
    return {"message": "Order delivered successfully", "order_id": order_id}
