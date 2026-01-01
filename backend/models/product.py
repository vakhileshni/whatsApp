"""
Product model - Pure data structure
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class Product:
    """Menu item/product"""
    id: str
    restaurant_id: str
    name: str
    description: str
    price: float
    category: str
    is_available: bool = True
    discounted_price: Optional[float] = None  # Discounted price (if any)
    discount_percentage: Optional[float] = None  # Discount percentage (calculated)


