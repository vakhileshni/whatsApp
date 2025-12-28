"""
Restaurant Repository - Data access layer for restaurants
Later: Replace with SQLAlchemy queries
"""
from typing import Optional
from models.restaurant import Restaurant
from data.restaurants_data import RESTAURANTS

def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    """
    Get restaurant by ID
    Later: SELECT * FROM restaurants WHERE id = ?
    """
    return RESTAURANTS.get(restaurant_id)

def get_all_restaurants():
    """
    Get all restaurants
    Later: SELECT * FROM restaurants WHERE is_active = TRUE
    """
    return list(RESTAURANTS.values())

def update_restaurant(restaurant: Restaurant) -> Optional[Restaurant]:
    """
    Update restaurant data
    Later: UPDATE restaurants SET ... WHERE id = ?
    """
    if restaurant.id in RESTAURANTS:
        RESTAURANTS[restaurant.id] = restaurant
        return restaurant
    return None

def find_restaurants_by_location(latitude: float, longitude: float, radius_km: float = 5.0):
    """
    Find restaurants near a location (for future WhatsApp routing)
    Later: SELECT * FROM restaurants WHERE ST_Distance_Sphere(point(longitude, latitude), point(?, ?)) <= ?
    """
    # For now, return all restaurants
    # Later: Implement geolocation calculation
    return list(RESTAURANTS.values())

def get_restaurant_by_phone(phone: str) -> Optional[Restaurant]:
    """
    Get restaurant by phone number
    Later: SELECT * FROM restaurants WHERE phone = ?
    """
    # Normalize phone number (remove whatsapp: prefix, handle different formats)
    normalized_phone = phone.replace("whatsapp:", "").replace("+", "").strip()
    
    # Try to match with each restaurant
    for restaurant in RESTAURANTS.values():
        # Normalize restaurant phone (remove + and spaces)
        restaurant_phone = restaurant.phone.replace("+", "").replace(" ", "").strip()
        
        # Compare normalized numbers
        if restaurant_phone == normalized_phone:
            return restaurant
        
        # Also try matching last 10 digits (in case of country code differences)
        if len(restaurant_phone) >= 10 and len(normalized_phone) >= 10:
            if restaurant_phone[-10:] == normalized_phone[-10:]:
                return restaurant
    
    return None

