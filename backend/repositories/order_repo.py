"""
Order Repository - Data access layer for orders
Now using SQLAlchemy with PostgreSQL database
"""
from typing import List, Optional
from models.order import Order
from database import SessionLocal
from models_db import OrderDB, OrderItemDB
from model_converters import order_db_to_model, order_model_to_db
from id_generator import generate_order_id, generate_order_item_id
from datetime import datetime


def get_order_by_id(order_id: str) -> Optional[Order]:
    """
    Get order by ID from database
    """
    db = SessionLocal()
    try:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if not db_order:
            return None
        
        # Get order items
        db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order_id).all()
        
        return order_db_to_model(db_order, db_items)
    finally:
        db.close()


def get_orders_by_restaurant(restaurant_id: str) -> List[Order]:
    """
    Get all orders for a restaurant from database
    """
    db = SessionLocal()
    try:
        db_orders = db.query(OrderDB).filter(
            OrderDB.restaurant_id == restaurant_id
        ).order_by(OrderDB.created_at.desc()).all()
        
        orders = []
        for db_order in db_orders:
            db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == db_order.id).all()
            orders.append(order_db_to_model(db_order, db_items))
        
        return orders
    finally:
        db.close()


def create_order(order: Order) -> Order:
    """
    Create a new order in database
    Automatically generates 9-digit ID if not provided
    """
    db = SessionLocal()
    try:
        # Generate ID if not provided
        if not order.id:
            order.id = generate_order_id()
        
        # Check if order already exists
        existing = db.query(OrderDB).filter(OrderDB.id == order.id).first()
        if existing:
            # Update instead
            return update_order(order)
        
        # Convert order to DB format
        order_dict, items_dict = order_model_to_db(order)
        
        # Generate IDs for order items if not provided
        for item_dict in items_dict:
            if not item_dict.get('id'):
                item_dict['id'] = generate_order_item_id()
        
        # Create order
        db_order = OrderDB(**order_dict)
        db.add(db_order)
        
        # Create order items
        for item_dict in items_dict:
            db_item = OrderItemDB(**item_dict)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        
        # Get created items
        db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order.id).all()
        
        # Invalidate rating cache
        from repositories.rating_repo import invalidate_rating_cache
        invalidate_rating_cache(order.restaurant_id)
        
        return order_db_to_model(db_order, db_items)
    except Exception as e:
        db.rollback()
        print(f"Error creating order: {e}")
        raise
    finally:
        db.close()


def update_order(order: Order) -> Order:
    """
    Update an order in database
    """
    db = SessionLocal()
    try:
        db_order = db.query(OrderDB).filter(OrderDB.id == order.id).first()
        if not db_order:
            raise ValueError(f"Order {order.id} not found")
        
        # Update order fields
        order_dict, items_dict = order_model_to_db(order)
        for key, value in order_dict.items():
            if key != 'id':  # Don't update ID
                setattr(db_order, key, value)
        
        # Delete existing items and recreate
        db.query(OrderItemDB).filter(OrderItemDB.order_id == order.id).delete()
        
        # Create new items (generate IDs if not provided)
        for item_dict in items_dict:
            if not item_dict.get('id'):
                item_dict['id'] = generate_order_item_id()
            db_item = OrderItemDB(**item_dict)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        
        # Get updated items
        db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order.id).all()
        
        # Invalidate rating cache
        from repositories.rating_repo import invalidate_rating_cache
        invalidate_rating_cache(order.restaurant_id)
        
        return order_db_to_model(db_order, db_items)
    except Exception as e:
        db.rollback()
        print(f"Error updating order: {e}")
        raise
    finally:
        db.close()


def update_order_status(order_id: str, status: str) -> Optional[Order]:
    """
    Update order status in database
    """
    db = SessionLocal()
    try:
        db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if not db_order:
            return None
        
        db_order.status = status
        db_order.updated_at = datetime.now()
        db.commit()
        db.refresh(db_order)
        
        # Get order items
        db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == order_id).all()
        
        # Invalidate rating cache
        from repositories.rating_repo import invalidate_rating_cache
        invalidate_rating_cache(db_order.restaurant_id)
        
        return order_db_to_model(db_order, db_items)
    except Exception as e:
        db.rollback()
        print(f"Error updating order status: {e}")
        return None
    finally:
        db.close()


def get_order_by_customer_id(customer_id: str) -> List[Order]:
    """
    Get orders by customer ID from database
    """
    db = SessionLocal()
    try:
        db_orders = db.query(OrderDB).filter(
            OrderDB.customer_id == customer_id
        ).order_by(OrderDB.created_at.desc()).all()
        
        orders = []
        for db_order in db_orders:
            db_items = db.query(OrderItemDB).filter(OrderItemDB.order_id == db_order.id).all()
            orders.append(order_db_to_model(db_order, db_items))
        
        return orders
    finally:
        db.close()
