"""
Product model - Pure data structure
"""
from dataclasses import dataclass

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


