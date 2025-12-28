"""
Orders Router - API endpoints for orders
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from services.order_service import (
    create_new_order,
    get_restaurant_orders,
    update_order_status_safe
)
from repositories.order_repo import get_order_by_id
import auth

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    id: str
    restaurant_id: str
    customer_id: str
    customer_phone: str
    customer_name: str
    items: List[OrderItemResponse]
    order_type: str
    subtotal: float
    delivery_fee: float
    total_amount: float
    total: float  # Alias for backward compatibility
    status: str
    created_at: str
    updated_at: str
    delivery_address: Optional[str] = None
    payment_status: str = "pending"
    customer_upi_name: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str

class VerifyPaymentRequest(BaseModel):
    customer_upi_name: str

class OrderCreate(BaseModel):
    customer_phone: str
    customer_name: str
    items: List[dict]
    order_type: str
    delivery_address: Optional[str] = None
    customer_latitude: Optional[float] = None  # For location-based routing
    customer_longitude: Optional[float] = None  # For location-based routing

def order_to_response(order) -> OrderResponse:
    """Convert Order model to OrderResponse"""
    return OrderResponse(
        id=order.id,
        restaurant_id=order.restaurant_id,
        customer_id=order.customer_id,
        customer_phone=order.customer_phone,
        customer_name=order.customer_name,
        items=[OrderItemResponse(**{
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price
        }) for item in order.items],
        order_type=order.order_type,
        subtotal=order.subtotal,
        delivery_fee=order.delivery_fee,
        total_amount=order.total_amount,
        total=order.total,  # Backward compatibility
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        delivery_address=order.delivery_address,
        payment_status=getattr(order, 'payment_status', 'pending'),
        customer_upi_name=getattr(order, 'customer_upi_name', None)
    )

@router.get("", response_model=List[OrderResponse])
async def get_orders(restaurant_id: str = Depends(auth.get_current_restaurant_id)):
    """Get all orders for current restaurant"""
    orders = get_restaurant_orders(restaurant_id)
    return [order_to_response(o) for o in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get a specific order"""
    order = get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order_to_response(order)

@router.post("", response_model=OrderResponse)
async def create_order(order_data: OrderCreate):
    """
    Create a new order (can be called without auth for WhatsApp webhook)
    Automatically routes to nearest restaurant if location provided
    """
    from repositories.restaurant_repo import get_all_restaurants
    from repositories.customer_repo import get_customer_by_phone, find_nearest_restaurant, create_customer
    from models.customer import Customer
    import uuid
    
    # Determine restaurant_id
    restaurant = None
    
    # Option 1: Find nearest restaurant if location provided
    if order_data.customer_latitude and order_data.customer_longitude:
        restaurant = find_nearest_restaurant(
            order_data.customer_latitude,
            order_data.customer_longitude
        )
    
    # Option 2: Check if customer exists and use their restaurant
    if not restaurant:
        existing_customer = get_customer_by_phone(order_data.customer_phone)
        if existing_customer:
            from repositories.restaurant_repo import get_restaurant_by_id
            restaurant = get_restaurant_by_id(existing_customer.restaurant_id)
    
    # Option 3: Fallback to first restaurant
    if not restaurant:
        restaurants = get_all_restaurants()
        if not restaurants:
            raise HTTPException(status_code=400, detail="No restaurant available")
        restaurant = restaurants[0]
    
    # Get or create customer
    customer = get_customer_by_phone(order_data.customer_phone)
    if not customer:
        customer_id = str(uuid.uuid4().int % 1000000)  # Generate simple ID
        customer = create_customer(Customer(
            id=customer_id,
            restaurant_id=restaurant.id,
            phone=order_data.customer_phone,
            latitude=order_data.customer_latitude or 0.0,
            longitude=order_data.customer_longitude or 0.0
        ))
    
    try:
        new_order = create_new_order(
            restaurant_id=restaurant.id,
            customer_id=customer.id,
            customer_phone=order_data.customer_phone,
            customer_name=order_data.customer_name,
            items_data=order_data.items,
            order_type=order_data.order_type,
            delivery_address=order_data.delivery_address
        )
        return order_to_response(new_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update order status and send WhatsApp notification to customer"""
    try:
        updated_order, old_status = update_order_status_safe(order_id, status_update.status, restaurant_id)
        
        # Send WhatsApp notification to customer (fire and forget - don't wait for it)
        from services.whatsapp_service import send_order_status_notification
        try:
            # Send notification asynchronously without blocking the response
            await send_order_status_notification(updated_order, status_update.status, old_status)
        except Exception as e:
            # Log error but don't fail the status update
            import logging
            logging.error(f"Failed to send WhatsApp notification: {e}")
        
        return order_to_response(updated_order)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{order_id}/verify-payment", response_model=OrderResponse)
async def verify_payment(
    order_id: str,
    payment_data: VerifyPaymentRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Verify payment for an order"""
    from repositories.order_repo import get_order_by_id, update_order
    from datetime import datetime
    
    order = get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify payment for this order")
    
    # Update payment status
    order.payment_status = "verified"
    order.customer_upi_name = payment_data.customer_upi_name.strip()
    order.updated_at = datetime.now().isoformat()
    
    # Save updated order
    updated_order = update_order(order)
    
    return order_to_response(updated_order)

