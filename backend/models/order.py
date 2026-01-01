"""
Order models - Pure data structures
"""
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class OrderItem:
    """Order line item"""
    product_id: str
    product_name: str
    quantity: int
    price: float

@dataclass
class Order:
    """Order entity"""
    id: str
    restaurant_id: str
    customer_id: str
    customer_phone: str
    customer_name: str
    items: List[OrderItem]
    order_type: str  # "pickup" or "delivery"
    delivery_fee: float
    total_amount: float  # Renamed from 'total' to match user's schema
    status: str  # "pending", "preparing", "ready", "delivered", "cancelled"
    created_at: str
    updated_at: str
    delivery_address: Optional[str] = None
    payment_status: str = "pending"  # "pending", "verified", "failed"
    payment_method: str = "cod"  # "cod" or "online"
    customer_upi_name: Optional[str] = None  # UPI name shown when payment is verified
    customer_rating: Optional[float] = None  # Rating given by customer after delivery (1-5)
    # For backward compatibility
    @property
    def subtotal(self) -> float:
        """Calculate subtotal from items"""
        return sum(item.price * item.quantity for item in self.items)
    
    @property
    def total(self) -> float:
        """Alias for total_amount for backward compatibility"""
        return self.total_amount

