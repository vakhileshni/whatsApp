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
    payment_method: str = "cod"  # "cod" or "online"
    customer_upi_name: Optional[str] = None
    customer_rating: Optional[float] = None  # Rating given by customer (1-5)

class OrderStatusUpdate(BaseModel):
    status: str

class VerifyPaymentRequest(BaseModel):
    customer_upi_name: str

class RateOrderRequest(BaseModel):
    rating: float  # Rating from 1-5

class OrderCreate(BaseModel):
    customer_phone: str
    customer_name: str
    items: List[dict]
    order_type: str
    delivery_address: Optional[str] = None
    customer_latitude: Optional[float] = None  # For location-based routing
    customer_longitude: Optional[float] = None  # For location-based routing
    restaurant_id: Optional[str] = None  # Restaurant ID if known (from menu page)
    alternate_phone: Optional[str] = None  # Alternate contact number
    payment_method: Optional[str] = "cod"  # "cod" or "online"

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
        payment_method=getattr(order, 'payment_method', 'cod'),
        customer_upi_name=getattr(order, 'customer_upi_name', None),
        customer_rating=getattr(order, 'customer_rating', None)
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
    
    # Option 1: Use restaurant_id if provided (from menu page)
    if order_data.restaurant_id:
        from repositories.restaurant_repo import get_restaurant_by_id
        restaurant = get_restaurant_by_id(order_data.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail=f"Restaurant {order_data.restaurant_id} not found")
    
    # Option 2: Find nearest restaurant if location provided
    if not restaurant and order_data.customer_latitude and order_data.customer_longitude:
        restaurant = find_nearest_restaurant(
            order_data.customer_latitude,
            order_data.customer_longitude
        )
    
    # Option 3: Check if customer exists and use their restaurant
    if not restaurant:
        existing_customer = get_customer_by_phone(order_data.customer_phone)
        if existing_customer:
            from repositories.restaurant_repo import get_restaurant_by_id
            restaurant = get_restaurant_by_id(existing_customer.restaurant_id)
    
    # Option 4: Fallback to first restaurant
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
    
    # Prepare delivery address with alternate phone if provided
    final_delivery_address = order_data.delivery_address
    if order_data.alternate_phone and final_delivery_address:
        final_delivery_address = f"{final_delivery_address}\n\n📱 Alternate Contact: {order_data.alternate_phone}"
    elif order_data.alternate_phone:
        final_delivery_address = f"📱 Alternate Contact: {order_data.alternate_phone}"
    
    # Determine payment method
    payment_method = order_data.payment_method or "cod"
    
    try:
        # For Cash on Delivery: Create order immediately
        if payment_method.lower() == "cod":
            new_order = create_new_order(
                restaurant_id=restaurant.id,
                customer_id=customer.id,
                customer_phone=order_data.customer_phone,
                customer_name=order_data.customer_name,
                items_data=order_data.items,
                order_type=order_data.order_type,
                delivery_address=final_delivery_address,
                payment_status="pending",  # COD payment is pending (will be collected on delivery)
                payment_method="cod"
            )
            
            # Send WhatsApp notification to customer about order confirmation
            try:
                from services.whatsapp_service import send_order_status_notification
                await send_order_status_notification(new_order, "pending", None)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send WhatsApp notification for order {new_order.id}: {e}")
            
            return order_to_response(new_order)
        
        # For Online Payment: Create order, then send UPI payment link
        elif payment_method.lower() == "online":
            # Create order with payment_status="pending"
            new_order = create_new_order(
                restaurant_id=restaurant.id,
                customer_id=customer.id,
                customer_phone=order_data.customer_phone,
                customer_name=order_data.customer_name,
                items_data=order_data.items,
                order_type=order_data.order_type,
                delivery_address=final_delivery_address,
                payment_status="pending",  # Payment pending until confirmed
                payment_method="online"
            )
            
            # Generate and send UPI payment link via WhatsApp
            try:
                from services.whatsapp_service import send_upi_payment_link
                await send_upi_payment_link(
                    customer_phone=order_data.customer_phone,
                    restaurant=restaurant,
                    order=new_order,
                    amount=new_order.total_amount
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to send UPI payment link for order {new_order.id}: {e}")
                # Still return the order, but log the error
            
            return order_to_response(new_order)
        
        else:
            raise HTTPException(status_code=400, detail=f"Invalid payment method: {payment_method}")
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

@router.post("/{order_id}/rate", response_model=OrderResponse)
async def rate_order(
    order_id: str,
    rating_data: RateOrderRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """
    Rate an order after delivery (called by customer)
    Rating must be between 1-5
    Note: This endpoint can be called without auth for public access
    """
    from repositories.order_repo import update_order
    
    order = get_order_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to rate this order")
    
    # Validate rating
    if rating_data.rating < 1 or rating_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    # Only allow rating delivered orders
    if order.status != "delivered":
        raise HTTPException(status_code=400, detail="Can only rate delivered orders")
    
    # Update order rating
    order.customer_rating = round(rating_data.rating, 2)
    updated_order = update_order(order)
    
    # Invalidate rating cache for this restaurant
    from repositories.rating_repo import invalidate_rating_cache
    invalidate_rating_cache(order.restaurant_id)
    
    return order_to_response(updated_order)

