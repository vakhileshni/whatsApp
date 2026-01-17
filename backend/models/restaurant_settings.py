"""
Restaurant Settings Model
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class RestaurantSettings:
    """Restaurant settings entity"""
    id: str
    restaurant_id: str
    
    # Notification Settings
    whatsapp_notifications_enabled: bool = True
    whatsapp_number: Optional[str] = None
    email_notifications_enabled: bool = False
    email_address: Optional[str] = None
    sms_notifications_enabled: bool = False
    sms_number: Optional[str] = None
    
    # Notification Preferences
    notify_new_order: bool = True
    notify_preparing: bool = True
    notify_ready: bool = True
    notify_delivered: bool = True
    notify_cancelled: bool = True
    notify_payment: bool = True
    
    # UI Preferences
    sound_enabled: bool = True
    blink_enabled: bool = True
    
    # Order Settings
    auto_accept_orders: bool = False
    default_preparation_time: int = 30  # minutes
    minimum_order_value: float = 0.0
    maximum_order_value: Optional[float] = None
    allow_order_modifications: bool = True
    cancellation_policy: Optional[str] = None
    delivery_available: bool = True  # Whether delivery option is available for customers

    # Profile / Business Settings (stored in settings table)
    delivery_radius_km: Optional[int] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    fssai_number: Optional[str] = None
    # JSON string or structured object of weekly schedule
    operating_hours: Optional[str] = None
