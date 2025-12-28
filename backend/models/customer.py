"""
Customer model - Pure data structure
"""
from dataclasses import dataclass

@dataclass
class Customer:
    """Customer entity"""
    id: str
    restaurant_id: str
    phone: str
    latitude: float = 0.0  # For location-based routing
    longitude: float = 0.0  # For location-based routing


