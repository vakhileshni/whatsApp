"""
Helper functions to convert between dataclass models and database models
"""
from models.restaurant import Restaurant
from models.user import User
from models.product import Product
from models.order import Order, OrderItem
from models.customer import Customer
from models.session import CustomerSession
from models_db import (
    RestaurantDB, UserDB, ProductDB, OrderDB, OrderItemDB,
    CustomerDB, CustomerSessionDB
)
import json
from datetime import datetime

# Restaurant conversions
def restaurant_db_to_model(db_restaurant: RestaurantDB) -> Restaurant:
    """Convert RestaurantDB to Restaurant model"""
    return Restaurant(
        id=db_restaurant.id,
        name=db_restaurant.name,
        phone=db_restaurant.phone,
        address=db_restaurant.address,
        latitude=float(db_restaurant.latitude),
        longitude=float(db_restaurant.longitude),
        delivery_fee=float(db_restaurant.delivery_fee),
        is_active=db_restaurant.is_active,
        upi_id=db_restaurant.upi_id or "",
        upi_password=db_restaurant.upi_password or "",
        upi_qr_code=db_restaurant.upi_qr_code or "",
        cuisine_type=db_restaurant.cuisine_type or "both",
    )

def restaurant_model_to_db(model: Restaurant) -> dict:
    """Convert Restaurant model to dict for DB insertion"""
    return {
        'id': model.id,
        'name': model.name,
        'phone': model.phone,
        'address': model.address,
        'latitude': model.latitude,
        'longitude': model.longitude,
        'delivery_fee': model.delivery_fee,
        'is_active': model.is_active,
        'upi_id': model.upi_id or '',
        'upi_password': model.upi_password or '',
        'upi_qr_code': model.upi_qr_code or '',
        'cuisine_type': model.cuisine_type or 'both',
    }

# User conversions
def user_db_to_model(db_user: UserDB) -> User:
    """Convert UserDB to User model"""
    return User(
        id=db_user.id,
        email=db_user.email,
        password=db_user.password,
        restaurant_id=db_user.restaurant_id,
        name=db_user.name,
        two_factor_enabled=db_user.two_factor_enabled if hasattr(db_user, 'two_factor_enabled') else False,
        two_factor_secret=db_user.two_factor_secret or "" if hasattr(db_user, 'two_factor_secret') else "",
        two_factor_backup_codes=db_user.two_factor_backup_codes or "" if hasattr(db_user, 'two_factor_backup_codes') else "",
    )

def user_model_to_db(model: User) -> dict:
    """Convert User model to dict for DB insertion"""
    return {
        'id': model.id,
        'email': model.email,
        'password': model.password,
        'restaurant_id': model.restaurant_id,
        'name': model.name,
        'two_factor_enabled': getattr(model, 'two_factor_enabled', False),
        'two_factor_secret': getattr(model, 'two_factor_secret', None),
        'two_factor_backup_codes': getattr(model, 'two_factor_backup_codes', None),
    }

# Product conversions
def product_db_to_model(db_product: ProductDB) -> Product:
    """Convert ProductDB to Product model"""
    return Product(
        id=db_product.id,
        restaurant_id=db_product.restaurant_id,
        name=db_product.name,
        description=db_product.description or "",
        price=float(db_product.price),
        category=db_product.category,
        is_available=db_product.is_available,
        discounted_price=float(db_product.discounted_price) if db_product.discounted_price else None,
        discount_percentage=float(db_product.discount_percentage) if db_product.discount_percentage else None,
    )

def product_model_to_db(model: Product) -> dict:
    """Convert Product model to dict for DB insertion"""
    return {
        'id': model.id,
        'restaurant_id': model.restaurant_id,
        'name': model.name,
        'description': model.description,
        'price': model.price,
        'category': model.category,
        'is_available': model.is_available,
        'discounted_price': model.discounted_price,
        'discount_percentage': model.discount_percentage,
    }

# Order conversions
def order_db_to_model(db_order: OrderDB, db_items: list[OrderItemDB]) -> Order:
    """Convert OrderDB and OrderItemDB to Order model"""
    items = [
        OrderItem(
            product_id=item.product_id,
            product_name=item.product_name,
            quantity=item.quantity,
            price=float(item.price),
        )
        for item in db_items
    ]
    
    return Order(
        id=db_order.id,
        restaurant_id=db_order.restaurant_id,
        customer_id=db_order.customer_id,
        customer_phone=db_order.customer_phone,
        customer_name=db_order.customer_name,
        items=items,
        order_type=db_order.order_type,
        delivery_fee=float(db_order.delivery_fee),
        total_amount=float(db_order.total_amount),
        status=db_order.status,
        created_at=db_order.created_at.isoformat() if db_order.created_at else datetime.now().isoformat(),
        updated_at=db_order.updated_at.isoformat() if db_order.updated_at else datetime.now().isoformat(),
        delivery_address=db_order.delivery_address,
        payment_status=db_order.payment_status,
        payment_method=db_order.payment_method,
        customer_upi_name=db_order.customer_upi_name,
        customer_rating=float(db_order.customer_rating) if db_order.customer_rating else None,
    )

from typing import Tuple
def order_model_to_db(model: Order) -> Tuple[dict, list]:
    """Convert Order model to dicts for DB insertion"""
    order_dict = {
        'id': model.id,
        'restaurant_id': model.restaurant_id,
        'customer_id': model.customer_id,
        'customer_phone': model.customer_phone,
        'customer_name': model.customer_name,
        'order_type': model.order_type,
        'status': model.status,
        'delivery_fee': model.delivery_fee,
        'subtotal': model.subtotal,
        'total_amount': model.total_amount,
        'payment_method': model.payment_method,
        'payment_status': model.payment_status,
        'customer_upi_name': model.customer_upi_name,
        'delivery_address': model.delivery_address,
        'customer_rating': model.customer_rating,
    }
    
    items_dict = [
        {
            'id': "",  # Will be auto-generated by repository
            'order_id': model.id,
            'product_id': item.product_id,
            'product_name': item.product_name,
            'quantity': item.quantity,
            'price': item.price,
        }
        for i, item in enumerate(model.items)
    ]
    
    return order_dict, items_dict

# Customer conversions
def customer_db_to_model(db_customer: CustomerDB) -> Customer:
    """Convert CustomerDB to Customer model"""
    return Customer(
        id=db_customer.id,
        restaurant_id=db_customer.restaurant_id or "",
        phone=db_customer.phone,
        latitude=float(db_customer.latitude) if db_customer.latitude else 0.0,
        longitude=float(db_customer.longitude) if db_customer.longitude else 0.0,
    )

def customer_model_to_db(model: Customer) -> dict:
    """Convert Customer model to dict for DB insertion"""
    return {
        'id': model.id,
        'restaurant_id': model.restaurant_id if model.restaurant_id else None,
        'phone': model.phone,
        'latitude': model.latitude,
        'longitude': model.longitude,
    }

# Session conversions
def session_db_to_model(db_session: CustomerSessionDB) -> CustomerSession:
    """Convert CustomerSessionDB to CustomerSession model"""
    # Parse cart JSON
    try:
        cart_data = json.loads(db_session.cart) if db_session.cart else []
        cart = [
            OrderItem(
                product_id=item.get('product_id', ''),
                product_name=item.get('product_name', ''),
                quantity=item.get('quantity', 1),
                price=item.get('price', 0.0),
            )
            for item in cart_data
        ]
    except:
        cart = []
    
    # Parse nearby_restaurants JSON
    try:
        nearby_restaurants = json.loads(db_session.nearby_restaurants) if db_session.nearby_restaurants else None
    except:
        nearby_restaurants = None
    
    return CustomerSession(
        phone_number=db_session.phone_number,
        customer_name=db_session.customer_name,
        restaurant_id=db_session.restaurant_id,
        current_step=db_session.current_step,
        cart=cart,
        latitude=float(db_session.latitude) if db_session.latitude else None,
        longitude=float(db_session.longitude) if db_session.longitude else None,
        location_timestamp=db_session.location_timestamp.isoformat() if db_session.location_timestamp else None,
        nearby_restaurants=nearby_restaurants,
    )

def session_model_to_db(model: CustomerSession) -> dict:
    """Convert CustomerSession model to dict for DB insertion"""
    # Convert cart to JSON
    cart_json = json.dumps([
        {
            'product_id': item.product_id,
            'product_name': item.product_name,
            'quantity': item.quantity,
            'price': item.price,
        }
        for item in model.cart
    ])
    
    # Convert nearby_restaurants to JSON
    nearby_json = json.dumps(model.nearby_restaurants) if model.nearby_restaurants else None
    
    return {
        'phone_number': model.phone_number,
        'customer_name': model.customer_name,
        'restaurant_id': model.restaurant_id,
        'current_step': model.current_step,
        'cart': cart_json,
        'latitude': model.latitude,
        'longitude': model.longitude,
        'location_timestamp': datetime.fromisoformat(model.location_timestamp) if model.location_timestamp else None,
        'nearby_restaurants': nearby_json,
    }
