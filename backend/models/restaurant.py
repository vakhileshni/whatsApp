"""
Restaurant model - Pure data structure
"""
from dataclasses import dataclass

@dataclass
class Restaurant:
    """Restaurant entity"""
    id: str
    name: str
    phone: str
    address: str
    latitude: float
    longitude: float
    delivery_fee: float = 40.0
    is_active: bool = True
    upi_id: str = ""  # UPI payment ID (e.g., restaurant@paytm or 1234567890@upi)
    upi_password: str = ""  # Separate password for UPI management (different from login password)
    upi_qr_code: str = ""  # UPI QR code image URL or base64 data
    cuisine_type: str = "both"  # "veg", "non-veg", "both", "snack", "full-meal", etc.

