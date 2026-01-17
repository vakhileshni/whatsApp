"""
Orders Router - API endpoints for orders
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import List, Optional
from services.order_service import (
    create_new_order,
    get_restaurant_orders,
    update_order_status_safe
)
from repositories.order_repo import get_order_by_id
import auth
import logging

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
logger = logging.getLogger(__name__)

class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    price: float

class OrderResponse(BaseModel):
    id: str
    order_number: str  # Order number (can be same as ID or formatted)
    restaurant_id: str
    customer_id: Optional[str] = None
    customer_phone: str
    customer_name: str
    items: List[OrderItemResponse]
    order_type: Optional[str] = None
    subtotal: Optional[float] = None
    delivery_fee: Optional[float] = None
    total_amount: float
    total: float  # Alias for backward compatibility
    status: str
    created_at: str
    updated_at: str
    delivery_address: Optional[str] = None
    payment_status: Optional[str] = "pending"
    payment_method: Optional[str] = "cod"  # "cod" or "online"
    customer_upi_name: Optional[str] = None
    customer_rating: Optional[float] = None  # Rating given by customer (1-5)
    payment_link: Optional[str] = None  # UPI payment link or Razorpay payment link
    razorpay_payment_link_id: Optional[str] = None  # Razorpay payment link ID for status polling

class OrderStatusUpdate(BaseModel):
    status: str

class VerifyPaymentRequest(BaseModel):
    customer_upi_name: str
    amount_paid: Optional[float] = None  # Amount customer actually paid (optional, defaults to order total)

class RateOrderRequest(BaseModel):
    rating: float  # Rating from 1-5

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int
    price: float
    special_instructions: Optional[str] = None

class OrderCreate(BaseModel):
    restaurant_id: str
    customer_name: str
    customer_phone: str
    customer_address: Optional[str] = None  # Optional customer address
    items: List[OrderItemCreate]
    total_amount: float
    payment_method: str = "cod"  # "upi", "cash", etc.
    delivery_address: Optional[str] = None  # Delivery address for delivery orders
    # Additional fields for backward compatibility and location-based routing
    order_type: Optional[str] = None  # "pickup" or "delivery"
    customer_latitude: Optional[float] = None
    customer_longitude: Optional[float] = None
    alternate_phone: Optional[str] = None

def generate_upi_payment_link(restaurant, order) -> Optional[str]:
    """Generate UPI payment link for an order"""
    import urllib.parse
    
    if not restaurant or not restaurant.upi_id:
        return None
    
    if getattr(order, 'payment_method', 'cod') != 'online':
        return None
    
    upi_id = restaurant.upi_id.strip()
    # Keep payee name with spaces (properly encoded) - removing spaces can look suspicious
    payee_name = restaurant.name.strip()
    # Use simpler transaction note - avoid "Order" keyword which might trigger security
    transaction_note = f"Payment {order.id[:8]}"
    amount = order.total_amount
    
    # UPI amount should be in format: "100.00" (with 2 decimals)
    amount_str = f"{amount:.2f}"
    
    # Generate UPI payment link
    upi_link = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn={urllib.parse.quote(payee_name)}&am={amount_str}&cu=INR&tn={urllib.parse.quote(transaction_note)}"
    return upi_link

def order_to_response(order, restaurant=None, payment_link_override=None, razorpay_payment_link_id_override=None) -> OrderResponse:
    """Convert Order model to OrderResponse"""
    payment_link = payment_link_override
    if not payment_link and restaurant:
        payment_link = generate_upi_payment_link(restaurant, order)
    
    return OrderResponse(
        id=order.id,
        order_number=order.id,  # Use order ID as order number
        restaurant_id=order.restaurant_id,
        customer_id=getattr(order, 'customer_id', None),
        customer_phone=order.customer_phone,
        customer_name=order.customer_name,
        items=[OrderItemResponse(**{
            "product_id": item.product_id,
            "product_name": item.product_name,
            "quantity": item.quantity,
            "price": item.price
        }) for item in order.items],
        order_type=getattr(order, 'order_type', None),
        subtotal=getattr(order, 'subtotal', None),
        delivery_fee=getattr(order, 'delivery_fee', None),
        total_amount=order.total_amount,
        total=order.total,  # Backward compatibility
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at,
        delivery_address=getattr(order, 'delivery_address', None),
        payment_status=getattr(order, 'payment_status', 'pending'),
        payment_method=getattr(order, 'payment_method', 'cod'),
        customer_upi_name=getattr(order, 'customer_upi_name', None),
        customer_rating=getattr(order, 'customer_rating', None),
        payment_link=payment_link,
        razorpay_payment_link_id=razorpay_payment_link_id_override  # Will be set by caller if needed
    )

@router.get("", response_model=List[OrderResponse])
async def get_orders(
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: Optional[int] = Query(None, ge=1, description="Number of results"),
    offset: Optional[int] = Query(None, ge=0, description="Pagination offset")
):
    """Get all orders for current restaurant"""
    from repositories.restaurant_repo import get_restaurant_by_id
    orders = get_restaurant_orders(restaurant_id)
    
    # Filter by status if provided
    if status:
        orders = [o for o in orders if o.status == status]
    
    # Apply pagination if provided
    if offset is not None:
        orders = orders[offset:]
    if limit is not None:
        orders = orders[:limit]
    
    restaurant = get_restaurant_by_id(restaurant_id)
    return [order_to_response(o, restaurant) for o in orders]

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get a specific order"""
    from repositories.restaurant_repo import get_restaurant_by_id
    order = get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    restaurant = get_restaurant_by_id(restaurant_id)
    return order_to_response(order, restaurant)

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate):
    """
    Create a new order (can be called without auth for WhatsApp webhook)
    Automatically routes to nearest restaurant if location provided
    """
    from fastapi import status
    from repositories.restaurant_repo import get_all_restaurants
    from repositories.customer_repo import get_customer_by_phone, find_nearest_restaurant, create_customer
    from models.customer import Customer
    import uuid
    
    # Determine restaurant_id
    restaurant = None
    
    # Option 1: Use restaurant_id if provided (from menu page or API request)
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
    
    # Prepare delivery address - use delivery_address if provided, otherwise use customer_address
    final_delivery_address = order_data.delivery_address or order_data.customer_address
    if order_data.alternate_phone and final_delivery_address:
        final_delivery_address = f"{final_delivery_address}\n\n📱 Alternate Contact: {order_data.alternate_phone}"
    elif order_data.alternate_phone:
        final_delivery_address = f"📱 Alternate Contact: {order_data.alternate_phone}"
    
    # Determine payment method
    payment_method = order_data.payment_method or "cod"
    
    # Determine order type - if delivery_address is provided, assume delivery, otherwise pickup
    order_type = order_data.order_type or ("delivery" if final_delivery_address else "pickup")
    
    # Convert items to the format expected by create_new_order
    items_data = [{
        "product_id": item.product_id,
        "quantity": item.quantity,
        "price": item.price,
        "special_instructions": item.special_instructions
    } for item in order_data.items]
    
    try:
        # For Cash on Delivery: Create order immediately
        if payment_method.lower() == "cod":
            new_order = create_new_order(
                restaurant_id=restaurant.id,
                customer_id=customer.id,
                customer_phone=order_data.customer_phone,
                customer_name=order_data.customer_name,
                items_data=items_data,
                order_type=order_type,
                delivery_address=final_delivery_address,
                payment_status="pending",  # COD payment is pending (will be collected on delivery)
                payment_method="cod"
            )
            
            # Send WhatsApp notification to customer about order confirmation
            try:
                from services.whatsapp_service import send_order_status_notification
                await send_order_status_notification(new_order, "pending", None)
            except Exception as e:
                logger.error(f"Failed to send WhatsApp notification for order {new_order.id}: {e}")
            
            # Send WhatsApp notification to restaurant owner
            try:
                from services.whatsapp_service import send_restaurant_order_notification
                await send_restaurant_order_notification(new_order, "new_order")
            except Exception as e:
                logger.error(f"Failed to send restaurant notification for order {new_order.id}: {e}")
            
            return order_to_response(new_order, restaurant)
        
        # For Online Payment: Create order, then create payment link
        elif payment_method.lower() == "online":
            # Create order with payment_status="pending"
            new_order = create_new_order(
                restaurant_id=restaurant.id,
                customer_id=customer.id,
                customer_phone=order_data.customer_phone,
                customer_name=order_data.customer_name,
                items_data=items_data,
                order_type=order_type,
                delivery_address=final_delivery_address,
                payment_status="pending",  # Payment pending until confirmed
                payment_method="online"
            )
            
            # Try Razorpay first (automatic verification)
            payment_link = None
            razorpay_payment_link_id = None
            
            try:
                from services.payment_service import create_razorpay_payment_link, razorpay_client
                if razorpay_client:
                    logger.info(f"💳 Creating Razorpay payment link for order {new_order.id}")
                    razorpay_link = create_razorpay_payment_link(
                        order_id=new_order.id,
                        amount=new_order.total_amount,
                        customer_name=order_data.customer_name,
                        customer_phone=order_data.customer_phone,
                        description=f"Order {new_order.id[:8]} from {restaurant.name}"
                    )
                    if razorpay_link:
                        payment_link = razorpay_link.get("short_url")
                        razorpay_payment_link_id = razorpay_link.get("id")
                        logger.info(f"✅ Razorpay payment link created: {payment_link}")
            except Exception as e:
                logger.warning(f"⚠️ Razorpay not available, falling back to UPI link: {e}")
            
            # Fallback to UPI QR code/link if Razorpay not available
            if not payment_link:
                try:
                    from services.whatsapp_service import send_upi_payment_link
                    logger.info(
                        "📤 Creating UPI payment link for order %s to %s",
                        new_order.id,
                        order_data.customer_phone,
                    )
                    await send_upi_payment_link(
                        customer_phone=order_data.customer_phone,
                        restaurant=restaurant,
                        order=new_order,
                        amount=new_order.total_amount,
                    )
                    # Get UPI link for response
                    payment_link = generate_upi_payment_link(restaurant, new_order)
                    logger.info("✅ UPI payment link created for order %s", new_order.id)
                except Exception as e:
                    logger.error("❌ CRITICAL: Failed to create payment link for order %s: %s", new_order.id, e)
                    logger.error("   Customer phone: %s", order_data.customer_phone)
                    logger.error("   Restaurant UPI ID: %s", getattr(restaurant, "upi_id", None))
                    logger.error("   Error type: %s", type(e).__name__)
                    logger.error("   Error details: %s", str(e))
            
            # Send WhatsApp notification to restaurant owner
            try:
                from services.whatsapp_service import send_restaurant_order_notification
                await send_restaurant_order_notification(new_order, "new_order")
            except Exception as e:
                logger.error(f"Failed to send restaurant notification for order {new_order.id}: {e}")
            
            # Update order response with payment link
            response = order_to_response(
                new_order, 
                restaurant, 
                payment_link_override=payment_link,
                razorpay_payment_link_id_override=razorpay_payment_link_id
            )
            
            return response
        
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
        
        # Send WhatsApp notification to restaurant owner if status changed
        if old_status != status_update.status:
            try:
                from services.whatsapp_service import send_restaurant_order_notification
                await send_restaurant_order_notification(updated_order, status_update.status)
            except Exception as e:
                import logging
                logging.error(f"Failed to send restaurant notification: {e}")
        
        from repositories.restaurant_repo import get_restaurant_by_id
        restaurant = get_restaurant_by_id(restaurant_id)
        return order_to_response(updated_order, restaurant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{order_id}/verify-payment-public")
async def verify_payment_public(
    order_id: str,
    payment_data: VerifyPaymentRequest
):
    """Public endpoint for customers to verify their payment (no auth required)"""
    from repositories.order_repo import get_order_by_id, update_order
    from services.whatsapp_service import send_whatsapp_message, format_phone_number
    from repositories.restaurant_repo import get_restaurant_by_id
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    order = get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if payment amount matches order total
    expected_amount = order.total_amount
    # If amount_paid not provided, assume full payment (restaurant is verifying)
    paid_amount = payment_data.amount_paid if payment_data.amount_paid is not None else expected_amount
    
    # Allow small tolerance (₹1) for rounding differences
    if paid_amount < expected_amount - 1.0:
        # Partial payment - cancel order and notify customer about refund
        order.payment_status = "failed"
        order.status = "cancelled"
        order.customer_upi_name = payment_data.customer_upi_name.strip()
        order.updated_at = datetime.now().isoformat()
        
        # Save updated order
        updated_order = update_order(order)
        
        # Send refund notification to customer
        try:
            customer_phone = format_phone_number(order.customer_phone)
            refund_message = (
                f"❌ *Order Cancelled - Payment Issue*\n\n"
                f"Hi {order.customer_name}!\n\n"
                f"Your order *#{order.id[:8]}* has been cancelled.\n\n"
                f"*Reason:* Partial Payment Received\n\n"
                f"*Expected Amount:* ₹{expected_amount:.0f}\n"
                f"*Amount Paid:* ₹{paid_amount:.0f}\n"
                f"*Shortfall:* ₹{expected_amount - paid_amount:.0f}\n\n"
                f"━━━━━━━━━━━━━━━━\n\n"
                f"💰 *Refund Information:*\n\n"
                f"Your payment of ₹{paid_amount:.0f} will be refunded to your account within 3-5 business days.\n\n"
                f"*Why was the order cancelled?*\n"
                f"Orders can only be confirmed when the full payment amount is received. "
                f"Please place a new order and ensure you pay the complete amount.\n\n"
                f"We apologize for any inconvenience. 🙏"
            )
            await send_whatsapp_message(customer_phone, refund_message)
            logger.info(f"✅ Refund notification sent to {customer_phone} for order {order.id}")
        except Exception as e:
            logger.error(f"❌ Failed to send refund notification: {e}")
        
        restaurant = get_restaurant_by_id(order.restaurant_id)
        return {
            "success": False,
            "message": f"Partial payment received. Expected ₹{expected_amount:.0f}, received ₹{paid_amount:.0f}. Order cancelled and refund will be processed.",
            "order": order_to_response(updated_order, restaurant)
        }
    
    # Full payment received - verify order
    order.payment_status = "verified"
    order.customer_upi_name = payment_data.customer_upi_name.strip()
    order.updated_at = datetime.now().isoformat()
    
    # Save updated order
    updated_order = update_order(order)
    
    # Send payment confirmation to customer
    try:
        customer_phone = format_phone_number(order.customer_phone)
        confirmation_message = (
            f"✅ *Payment Confirmed!*\n\n"
            f"Hi {order.customer_name}!\n\n"
            f"Payment of ₹{paid_amount:.0f} for order *#{order.id[:8]}* has been confirmed.\n\n"
            f"Your order is now being processed! 🍽️\n\n"
            f"We'll notify you when we start preparing your order."
        )
        await send_whatsapp_message(customer_phone, confirmation_message)
        logger.info(f"✅ Payment confirmation sent to {customer_phone} for order {order.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send payment confirmation: {e}")
    
    restaurant = get_restaurant_by_id(order.restaurant_id)
    return {
        "success": True,
        "message": "Payment verified successfully! Your order is now being processed.",
        "order": order_to_response(updated_order, restaurant)
    }

@router.patch("/{order_id}/verify-payment", response_model=OrderResponse)
async def verify_payment(
    order_id: str,
    payment_data: VerifyPaymentRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Verify payment for an order with amount validation"""
    from repositories.order_repo import get_order_by_id, update_order
    from services.whatsapp_service import send_whatsapp_message, format_phone_number
    from datetime import datetime
    import logging
    
    logger = logging.getLogger(__name__)
    
    order = get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to verify payment for this order")
    
    # Check if payment amount matches order total
    expected_amount = order.total_amount
    # If amount_paid not provided, assume full payment (restaurant is verifying)
    paid_amount = payment_data.amount_paid if payment_data.amount_paid is not None else expected_amount
    
    # Allow small tolerance (₹1) for rounding differences
    if paid_amount < expected_amount - 1.0:
        # Partial payment - cancel order and notify customer about refund
        order.payment_status = "failed"
        order.status = "cancelled"
        order.customer_upi_name = payment_data.customer_upi_name.strip()
        order.updated_at = datetime.now().isoformat()
        
        # Save updated order
        updated_order = update_order(order)
        
        # Send refund notification to customer
        try:
            customer_phone = format_phone_number(order.customer_phone)
            refund_message = (
                f"❌ *Order Cancelled - Payment Issue*\n\n"
                f"Hi {order.customer_name}!\n\n"
                f"Your order *#{order.id[:8]}* has been cancelled.\n\n"
                f"*Reason:* Partial Payment Received\n\n"
                f"*Expected Amount:* ₹{expected_amount:.0f}\n"
                f"*Amount Paid:* ₹{paid_amount:.0f}\n"
                f"*Shortfall:* ₹{expected_amount - paid_amount:.0f}\n\n"
                f"━━━━━━━━━━━━━━━━\n\n"
                f"💰 *Refund Information:*\n\n"
                f"Your payment of ₹{paid_amount:.0f} will be refunded to your account within 3-5 business days.\n\n"
                f"*Why was the order cancelled?*\n"
                f"Orders can only be confirmed when the full payment amount is received. "
                f"Please place a new order and ensure you pay the complete amount.\n\n"
                f"We apologize for any inconvenience. 🙏"
            )
            await send_whatsapp_message(customer_phone, refund_message)
            logger.info(f"✅ Refund notification sent to {customer_phone} for order {order.id}")
        except Exception as e:
            logger.error(f"❌ Failed to send refund notification: {e}")
        
        raise HTTPException(
            status_code=400,
            detail=f"Partial payment received. Expected ₹{expected_amount:.0f}, received ₹{paid_amount:.0f}. Order cancelled and refund will be processed."
        )
    
    # Full payment received - verify order
    order.payment_status = "verified"
    order.customer_upi_name = payment_data.customer_upi_name.strip()
    order.updated_at = datetime.now().isoformat()
    
    # Save updated order
    updated_order = update_order(order)
    
    # Send payment confirmation to customer
    try:
        customer_phone = format_phone_number(order.customer_phone)
        confirmation_message = (
            f"✅ *Payment Confirmed!*\n\n"
            f"Hi {order.customer_name}!\n\n"
            f"Payment of ₹{paid_amount:.0f} for order *#{order.id[:8]}* has been confirmed.\n\n"
            f"Your order is now being processed! 🍽️\n\n"
            f"We'll notify you when we start preparing your order."
        )
        await send_whatsapp_message(customer_phone, confirmation_message)
        logger.info(f"✅ Payment confirmation sent to {customer_phone} for order {order.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send payment confirmation: {e}")
    
    from repositories.restaurant_repo import get_restaurant_by_id
    restaurant = get_restaurant_by_id(restaurant_id)
    return order_to_response(updated_order, restaurant)

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
    
    from repositories.restaurant_repo import get_restaurant_by_id
    restaurant = get_restaurant_by_id(restaurant_id)
    return order_to_response(updated_order, restaurant)