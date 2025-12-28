"""
Customer session model - Pure data structure
"""
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from models.order import OrderItem

@dataclass
class CustomerSession:
    """Customer WhatsApp session"""
    phone_number: str
    restaurant_id: str
    current_step: str  # "menu", "cart", "checkout", "none"
    cart: List['OrderItem'] = field(default_factory=list)

