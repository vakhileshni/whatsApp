"""
Customer session model - Pure data structure
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderItem

@dataclass
class CustomerSession:
    """Customer WhatsApp session"""
    phone_number: str
    customer_name: Optional[str] = None  # Customer name from WhatsApp
    restaurant_id: Optional[str] = None  # Selected restaurant ID
    current_step: str = "location_request"  # "location_request", "location_confirm", "restaurant_selection", "menu", "cart", "checkout", "none", "restaurant_closed_confirm", "qr_location_request", "qr_location_confirm", "qr_restaurant_selected"
    cart: List['OrderItem'] = field(default_factory=list)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_timestamp: Optional[str] = None  # ISO format timestamp when location was saved
    nearby_restaurants: Optional[List[Dict]] = None  # List of restaurants with serial numbers

