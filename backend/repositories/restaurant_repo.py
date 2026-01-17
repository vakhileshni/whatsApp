"""
Restaurant Repository - Data access layer for restaurants
Now using SQLAlchemy with PostgreSQL database
"""
from typing import Optional, List
from models.restaurant import Restaurant
from database import SessionLocal, get_db
from models_db import RestaurantDB
from model_converters import restaurant_db_to_model, restaurant_model_to_db
from id_generator import generate_restaurant_id
from sqlalchemy import and_
import math


def get_restaurant_by_id(restaurant_id: str) -> Optional[Restaurant]:
    """
    Get restaurant by ID from database
    """
    db = SessionLocal()
    try:
        db_restaurant = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant_id).first()
        if db_restaurant:
            return restaurant_db_to_model(db_restaurant)
        return None
    finally:
        db.close()


def get_all_restaurants() -> List[Restaurant]:
    """
    Get all restaurants from database
    """
    db = SessionLocal()
    try:
        db_restaurants = db.query(RestaurantDB).filter(RestaurantDB.is_active == True).all()
        return [restaurant_db_to_model(r) for r in db_restaurants]
    finally:
        db.close()


def create_restaurant(restaurant: Restaurant) -> Optional[Restaurant]:
    """
    Create a new restaurant in database
    Automatically generates 9-digit ID if not provided
    """
    db = SessionLocal()
    try:
        # Generate ID if not provided or if restaurant with that ID exists
        if not restaurant.id or db.query(RestaurantDB).filter(RestaurantDB.id == restaurant.id).first():
            restaurant.id = generate_restaurant_id()
        
        # Check if restaurant already exists
        existing = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant.id).first()
        if existing:
            return None  # Restaurant already exists
        
        # Create new restaurant
        db_restaurant = RestaurantDB(**restaurant_model_to_db(restaurant))
        db.add(db_restaurant)
        db.commit()
        db.refresh(db_restaurant)
        return restaurant_db_to_model(db_restaurant)
    except Exception as e:
        db.rollback()
        print(f"Error creating restaurant: {e}")
        return None
    finally:
        db.close()


def update_restaurant(restaurant: Restaurant) -> Optional[Restaurant]:
    """
    Update restaurant data in database
    """
    db = SessionLocal()
    try:
        db_restaurant = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant.id).first()
        if not db_restaurant:
            return None
        
        # Update fields
        for key, value in restaurant_model_to_db(restaurant).items():
            setattr(db_restaurant, key, value)
        
        db.commit()
        db.refresh(db_restaurant)
        return restaurant_db_to_model(db_restaurant)
    except Exception as e:
        db.rollback()
        print(f"Error updating restaurant: {e}")
        return None
    finally:
        db.close()


def find_restaurants_by_location(latitude: float, longitude: float, radius_km: float = 50.0) -> List[dict]:
    """
    Find restaurants near a location sorted by combined score (rating + distance)
    Sorting priority:
    1. Overall rating (higher is better) - 60% weight
    2. Distance (closer is better) - 40% weight
    """
    db = SessionLocal()
    try:
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
        
        # Get all active restaurants
        db_restaurants = db.query(RestaurantDB).filter(RestaurantDB.is_active == True).all()
        
        nearby_restaurants = []
        for db_restaurant in db_restaurants:
            restaurant = restaurant_db_to_model(db_restaurant)
            
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
    finally:
        db.close()


def get_restaurant_by_phone(phone: str) -> Optional[Restaurant]:
    """
    Get restaurant by phone number from database
    """
    db = SessionLocal()
    try:
        # Normalize phone number (remove whatsapp: prefix, handle different formats)
        normalized_phone = phone.replace("whatsapp:", "").replace("+", "").strip()
        
        # Query database
        db_restaurants = db.query(RestaurantDB).all()
        
        for db_restaurant in db_restaurants:
            # Normalize restaurant phone (remove + and spaces)
            restaurant_phone = db_restaurant.phone.replace("+", "").replace(" ", "").strip()
            
            # Compare normalized numbers
            if restaurant_phone == normalized_phone:
                return restaurant_db_to_model(db_restaurant)
            
            # Also try matching last 10 digits (in case of country code differences)
            if len(restaurant_phone) >= 10 and len(normalized_phone) >= 10:
                if restaurant_phone[-10:] == normalized_phone[-10:]:
                    return restaurant_db_to_model(db_restaurant)
        
        return None
    finally:
        db.close()
