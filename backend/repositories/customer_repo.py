"""
Customer Repository - Data access layer for customers
Later: Replace with SQLAlchemy queries
"""
from typing import List, Optional
from models.customer import Customer
from data.customers_data import CUSTOMERS

def get_customer_by_id(customer_id: str) -> Optional[Customer]:
    """
    Get customer by ID
    Later: SELECT * FROM customers WHERE id = ?
    """
    return CUSTOMERS.get(customer_id)

def get_customer_by_phone(phone: str) -> Optional[Customer]:
    """
    Get customer by phone number
    Later: SELECT * FROM customers WHERE phone = ?
    """
    for customer in CUSTOMERS.values():
        if customer.phone == phone:
            return customer
    return None

def get_customers_by_restaurant(restaurant_id: str) -> List[Customer]:
    """
    Get all customers for a restaurant
    Later: SELECT * FROM customers WHERE restaurant_id = ?
    """
    return [c for c in CUSTOMERS.values() if c.restaurant_id == restaurant_id]

def create_customer(customer: Customer) -> Customer:
    """
    Create a new customer
    Later: INSERT INTO customers (...) VALUES (...)
    """
    CUSTOMERS[customer.id] = customer
    return customer

def find_nearest_restaurant(customer_latitude: float, customer_longitude: float):
    """
    Find nearest restaurant based on customer location
    Later: SELECT * FROM restaurants ORDER BY ST_Distance_Sphere(point(longitude, latitude), point(?, ?)) LIMIT 1
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


