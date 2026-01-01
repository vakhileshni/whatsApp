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

def create_restaurant(restaurant: Restaurant) -> Optional[Restaurant]:
    """
    Create a new restaurant
    Later: INSERT INTO restaurants (...) VALUES (...)
    """
    if restaurant.id in RESTAURANTS:
        return None  # Restaurant already exists
    RESTAURANTS[restaurant.id] = restaurant
    return restaurant

def update_restaurant(restaurant: Restaurant) -> Optional[Restaurant]:
    """
    Update restaurant data
    Later: UPDATE restaurants SET ... WHERE id = ?
    """
    if restaurant.id in RESTAURANTS:
        RESTAURANTS[restaurant.id] = restaurant
        return restaurant
    return None

def find_restaurants_by_location(latitude: float, longitude: float, radius_km: float = 50.0):
    """
    Find restaurants near a location sorted by combined score (rating + distance)
    Sorting priority:
    1. Overall rating (higher is better) - 60% weight
    2. Distance (closer is better) - 40% weight
    
    Later: SELECT * FROM restaurants WHERE ST_Distance_Sphere(point(longitude, latitude), point(?, ?)) <= ? 
           ORDER BY (rating * 0.6 - distance * 0.4) DESC
    """
    import math
    from repositories.rating_repo import get_restaurant_rating
    
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
    
    nearby_restaurants = []
    for restaurant in RESTAURANTS.values():
        if not restaurant.is_active:
            continue
        
        distance = haversine_distance(
            latitude, longitude,
            restaurant.latitude, restaurant.longitude
        )
        
        if distance <= radius_km:
            # Get restaurant rating
            rating_data = get_restaurant_rating(restaurant.id)
            overall_rating = rating_data['overall_rating']
            
            # Calculate combined score (higher is better)
            # Normalize distance (inverse, max 15km = 1.0, min = 0)
            normalized_distance = max(0, 1 - (distance / 15.0))  # 15km max normalization
            # Combined score: 60% rating (1-5 scale normalized), 40% distance (normalized)
            rating_score = (overall_rating / 5.0) * 0.6  # Normalize rating to 0-1
            distance_score = normalized_distance * 0.4
            combined_score = rating_score + distance_score
            
            nearby_restaurants.append({
                'restaurant': restaurant,
                'distance': round(distance, 2),
                'rating': overall_rating,
                'customer_rating': rating_data['customer_rating'],
                'total_orders': rating_data['total_orders'],
                'combined_score': combined_score  # For sorting
            })
    
    # Sort by combined score (higher is better), then by distance as tiebreaker
    nearby_restaurants.sort(key=lambda x: (-x['combined_score'], x['distance']))
    
    return nearby_restaurants

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

