"""
Rating Repository - Handles restaurant ratings and calculations
Calculates ratings based on:
1. Customer ratings (average of all customer ratings)
2. Order completion rate (delivered orders / total orders)
3. Processing speed (time from pending to delivered)
"""
from typing import Dict, Optional
from repositories.order_repo import get_orders_by_restaurant

# In-memory cache for restaurant ratings (for performance)
_rating_cache: Dict[str, Dict] = {}

def calculate_restaurant_rating(restaurant_id: str) -> Dict:
    """
    Calculate restaurant rating based on:
    - Customer ratings (average of all ratings) - 70% weight
    - Order completion rate (delivered/cancelled ratio) - 20% weight  
    - Order volume (more orders = better reliability) - 10% weight
    
    Returns: {
        'overall_rating': float (1-5),
        'customer_rating': float (average of customer ratings),
        'completion_rate': float (0-1),
        'total_orders': int,
        'rated_orders': int,
        'delivered_orders': int,
        'cancelled_orders': int
    }
    """
    orders = get_orders_by_restaurant(restaurant_id)
    
    if not orders:
        return {
            'overall_rating': 4.0,  # Default rating for new restaurants
            'customer_rating': None,
            'completion_rate': 1.0,
            'total_orders': 0,
            'rated_orders': 0,
            'delivered_orders': 0,
            'cancelled_orders': 0
        }
    
    # Calculate customer rating (average of all ratings)
    ratings = [order.customer_rating for order in orders if order.customer_rating is not None]
    customer_rating = sum(ratings) / len(ratings) if ratings else None
    
    # Calculate completion rate
    delivered_orders = len([o for o in orders if o.status == "delivered"])
    cancelled_orders = len([o for o in orders if o.status == "cancelled"])
    total_completed = delivered_orders + cancelled_orders
    completion_rate = delivered_orders / total_completed if total_completed > 0 else 1.0
    
    # Calculate overall rating
    if customer_rating is not None:
        # Weighted formula: 70% customer rating, 20% completion rate, 10% volume bonus
        volume_bonus = min(len(orders) / 100, 0.5)  # Up to 0.5 bonus for volume
        overall_rating = (
            customer_rating * 0.7 +  # Customer satisfaction (70%)
            (completion_rate * 5) * 0.2 +  # Completion rate as 1-5 scale (20%)
            volume_bonus * 0.1  # Volume bonus (10%)
        )
        overall_rating = min(5.0, max(1.0, overall_rating))  # Clamp between 1-5
    else:
        # If no customer ratings yet, use completion rate and volume
        volume_bonus = min(len(orders) / 100, 0.5)
        overall_rating = (completion_rate * 5) * 0.8 + volume_bonus * 0.2
        overall_rating = min(5.0, max(3.0, overall_rating))  # Clamp between 3-5 for new restaurants
    
    result = {
        'overall_rating': round(overall_rating, 2),
        'customer_rating': round(customer_rating, 2) if customer_rating else None,
        'completion_rate': round(completion_rate, 2),
        'total_orders': len(orders),
        'rated_orders': len(ratings),
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders
    }
    
    # Cache the result
    _rating_cache[restaurant_id] = result
    return result

def get_restaurant_rating(restaurant_id: str) -> Dict:
    """Get restaurant rating (from cache if available, else calculate)"""
    if restaurant_id in _rating_cache:
        return _rating_cache[restaurant_id]
    return calculate_restaurant_rating(restaurant_id)

def invalidate_rating_cache(restaurant_id: str):
    """Invalidate rating cache when orders are updated"""
    if restaurant_id in _rating_cache:
        del _rating_cache[restaurant_id]




