"""
Delivery Person model - Pure data structure
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class DeliveryPerson:
    """Delivery person model"""
    id: str
    name: str
    phone: str
    email: str
    password_hash: str  # Hashed password
    vehicle_type: str = "bike"
    license_number: Optional[str] = None
    is_available: bool = False
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
