"""
Order Service - Business logic for orders
"""
from datetime import datetime
from typing import List, Optional
from models.order import Order, OrderItem
from models.restaurant import Restaurant
from repositories.order_repo import create_order, get_orders_by_restaurant, update_order_status, get_order_by_id
from repositories.product_repo import get_product_by_id
from repositories.restaurant_repo import get_restaurant_by_id
from id_generator import generate_order_id, generate_order_item_id

def create_new_order(
    restaurant_id: str,
    customer_id: str,
    customer_phone: str,
    customer_name: str,
    items_data: List[dict],
    order_type: str,
    delivery_address: str = None,
    payment_status: str = "pending",
    payment_method: str = "cod"
) -> Order:
    """
    Create a new order with business logic validation
    """
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise ValueError("Restaurant not found")
    
    # Build order items
    order_items = []
    subtotal = 0.0
    
    for item_data in items_data:
        product_id = item_data.get("product_id")
        quantity = item_data.get("quantity", 1)
        
        product = get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        if product.restaurant_id != restaurant_id:
            raise ValueError(f"Product does not belong to restaurant")
        
        if not product.is_available:
            raise ValueError(f"Product {product.name} is not available")
        
        # Use discounted price if available and valid, otherwise use regular price
        effective_price = product.discounted_price if (
            product.discounted_price is not None and 
            product.discounted_price < product.price and
            product.discounted_price > 0
        ) else product.price
        
        item_total = effective_price * quantity
        subtotal += item_total
        
        order_items.append(OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=quantity,
            price=effective_price  # Store the effective price (discounted or regular)
        ))
    
    # Calculate delivery fee
    delivery_fee = restaurant.delivery_fee if order_type == "delivery" else 0.0
    total = subtotal + delivery_fee
    
    # Generate 9-digit order ID
    order_id = generate_order_id()
    now = datetime.now().isoformat()
    
    new_order = Order(
        id=order_id,
        restaurant_id=restaurant_id,
        customer_id=customer_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
        items=order_items,
        order_type=order_type,
        delivery_fee=delivery_fee,
        total_amount=total,
        status="pending",
        created_at=now,
        updated_at=now,
        delivery_address=delivery_address,
        payment_status=payment_status,
        payment_method=payment_method
    )
    
    return create_order(new_order)

def get_restaurant_orders(restaurant_id: str) -> List[Order]:
    """
    Get all orders for a restaurant
    """
    return get_orders_by_restaurant(restaurant_id)

def update_order_status_safe(order_id: str, new_status: str, restaurant_id: str) -> tuple[Order, str]:
    """
    Update order status with authorization check
    Returns: (updated_order, old_status) - old_status is returned so router can send notification
    """
    valid_statuses = ["pending", "preparing", "ready", "delivered", "cancelled"]
    if new_status not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")
    
    # Get current order to check old status
    current_order = get_order_by_id(order_id)
    if not current_order:
        raise ValueError("Order not found")
    
    # Verify order belongs to restaurant
    orders = get_orders_by_restaurant(restaurant_id)
    order = next((o for o in orders if o.id == order_id), None)
    
    if not order:
        raise ValueError("Order not found or access denied")
    
    old_status = current_order.status
    
    # Update order status
    updated_order = update_order_status(order_id, new_status)
    
    return updated_order, old_status

