"""
Notification Model
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class RestaurantNotification:
    """Restaurant notification entity"""
    id: str
    restaurant_id: str
    order_id: Optional[str] = None
    notification_type: str = "whatsapp"  # 'whatsapp', 'email', 'sms'
    notification_event: str = ""  # 'new_order', 'order_status_changed', 'payment_received', etc.
    recipient: str = ""  # phone number, email, etc.
    message_body: str = ""
    status: str = "sent"  # 'sent', 'delivered', 'failed', 'clicked'
    button_clicked: Optional[str] = None  # 'accept', 'preparing', 'ready', 'cancel', etc.
    clicked_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
