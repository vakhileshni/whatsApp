"""
Customer Repository - Data access layer for customers
Now using SQLAlchemy with PostgreSQL database
"""
from typing import List, Optional
from models.customer import Customer
from database import SessionLocal
from models_db import CustomerDB
from model_converters import customer_db_to_model, customer_model_to_db
from id_generator import generate_customer_id


def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    """
    Get customer by ID from database
    """
    db = SessionLocal()
    try:
        db_customer = db.query(CustomerDB).filter(CustomerDB.id == customer_id).first()
        if db_customer:
            return customer_db_to_model(db_customer)
        return None
    finally:
        db.close()


def get_customer_by_phone(phone: str) -> Optional[Customer]:
    """
    Get customer by phone number from database
    """
    db = SessionLocal()
    try:
        db_customer = db.query(CustomerDB).filter(CustomerDB.phone == phone).first()
        if db_customer:
            return customer_db_to_model(db_customer)
        return None
    finally:
        db.close()


def get_customers_by_restaurant(restaurant_id: str) -> List[Customer]:
    """
    Get all customers for a restaurant from database
    """
    db = SessionLocal()
    try:
        db_customers = db.query(CustomerDB).filter(CustomerDB.restaurant_id == restaurant_id).all()
        return [customer_db_to_model(c) for c in db_customers]
    finally:
        db.close()


def create_customer(customer: Customer) -> Customer:
    """
    Create a new customer in database
    Automatically generates 9-digit ID if not provided
    """
    db = SessionLocal()
    try:
        # Check if customer already exists (by phone)
        existing = db.query(CustomerDB).filter(CustomerDB.phone == customer.phone).first()
        if existing:
            # Update existing customer
            for key, value in customer_model_to_db(customer).items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return customer_db_to_model(existing)
        
        # Generate ID if not provided
        if not customer.id:
            customer.id = generate_customer_id()
        
        # Create new customer
        db_customer = CustomerDB(**customer_model_to_db(customer))
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return customer_db_to_model(db_customer)
    except Exception as e:
        db.rollback()
        print(f"Error creating customer: {e}")
        raise
    finally:
        db.close()


def find_nearest_restaurant(customer_latitude: float, customer_longitude: float):
    """
    Find nearest restaurant based on customer location
    """
    from repositories.restaurant_repo import get_all_restaurants
    import math
    
    restaurants = get_all_restaurants()
    if not restaurants:
        return None
    
    nearest_restaurant = None
    min_distance = float('inf')
    
    # Calculate distance using Haversine formula
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers"""
        R = 6371  # Earth radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    for restaurant in restaurants:
        if not restaurant.is_active:
            continue
        
        distance = haversine_distance(
            customer_latitude, customer_longitude,
            restaurant.latitude, restaurant.longitude
        )
        
        if distance < min_distance:
            min_distance = distance
            nearest_restaurant = restaurant
    
    return nearest_restaurant
