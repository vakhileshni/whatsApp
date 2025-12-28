"""
Order Repository - Data access layer for orders
Later: Replace with SQLAlchemy queries
"""
from typing import List, Optional
from models.order import Order
from data.orders_data import ORDERS

def get_order_by_id(order_id: str) -> Optional[Order]:
    """
    Get order by ID
    Later: SELECT * FROM orders WHERE id = ?
    """
    return ORDERS.get(order_id)

def get_orders_by_restaurant(restaurant_id: str) -> List[Order]:
    """
    Get all orders for a restaurant
    Later: SELECT * FROM orders WHERE restaurant_id = ? ORDER BY created_at DESC
    """
    orders = [o for o in ORDERS.values() if o.restaurant_id == restaurant_id]
    orders.sort(key=lambda x: x.created_at, reverse=True)
    return orders

def create_order(order: Order) -> Order:
    """
    Create a new order
    Later: INSERT INTO orders (...) VALUES (...)
    """
    ORDERS[order.id] = order
    return order

def update_order(order: Order) -> Order:
    """
    Update an order
    Later: UPDATE orders SET ... WHERE id = ?
    """
    ORDERS[order.id] = order
    return order

def update_order_status(order_id: str, status: str) -> Optional[Order]:
    """
    Update order status
    Later: UPDATE orders SET status = ?, updated_at = NOW() WHERE id = ?
    """
    order = ORDERS.get(order_id)
    if order:
        order.status = status
        from datetime import datetime
        order.updated_at = datetime.now().isoformat()
    return order

def get_order_by_customer_id(customer_id: str) -> List[Order]:
    """
    Get orders by customer ID
    Later: SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC
    """
    orders = [o for o in ORDERS.values() if o.customer_id == customer_id]
    orders.sort(key=lambda x: x.created_at, reverse=True)
    return orders

