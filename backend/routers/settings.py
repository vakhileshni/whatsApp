"""
Settings Router - API endpoints for restaurant settings
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from repositories.settings_repo import get_settings_by_restaurant_id, create_or_update_settings
from repositories.restaurant_repo import get_restaurant_by_id
from models.restaurant_settings import RestaurantSettings
from id_generator import generate_settings_id
from database import SessionLocal
from models_db import RestaurantDB
from services.whatsapp_service import send_whatsapp_message, format_phone_number
import auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


class NotificationSettingsRequest(BaseModel):
    whatsapp_notifications_enabled: bool = True
    whatsapp_number: Optional[str] = None
    email_notifications_enabled: bool = False
    email_address: Optional[EmailStr] = None
    sms_notifications_enabled: bool = False
    sms_number: Optional[str] = None
    notify_new_order: bool = True
    notify_preparing: bool = True
    notify_ready: bool = True
    notify_delivered: bool = True
    notify_cancelled: bool = True
    notify_payment: bool = True
    sound_enabled: bool = True
    blink_enabled: bool = True


class OrderSettingsRequest(BaseModel):
    auto_accept_orders: bool = False
    default_preparation_time: int = 30
    minimum_order_value: float = 0.0
    maximum_order_value: Optional[float] = None
    allow_order_modifications: bool = True
    cancellation_policy: Optional[str] = None
    delivery_available: bool = True


class ProfileSettingsRequest(BaseModel):
    restaurant_name: str
    phone: str
    address: str
    latitude: float
    longitude: float
    delivery_radius_km: Optional[int] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    fssai_number: Optional[str] = None
    # Frontend sends JSON; we store as string in settings
    operating_hours: Optional[Dict[str, Any]] = None


class SettingsResponse(BaseModel):
    id: str
    restaurant_id: str
    whatsapp_notifications_enabled: bool
    whatsapp_number: Optional[str]
    email_notifications_enabled: bool
    email_address: Optional[str]
    sms_notifications_enabled: bool
    sms_number: Optional[str]
    notify_new_order: bool
    notify_preparing: bool
    notify_ready: bool
    notify_delivered: bool
    notify_cancelled: bool
    notify_payment: bool
    sound_enabled: bool
    blink_enabled: bool
    auto_accept_orders: bool
    default_preparation_time: int
    minimum_order_value: float
    maximum_order_value: Optional[float]
    allow_order_modifications: bool
    cancellation_policy: Optional[str]
    delivery_available: bool

    # Profile / Business Settings
    delivery_radius_km: Optional[int] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    fssai_number: Optional[str] = None
    operating_hours: Optional[str] = None


@router.get("", response_model=SettingsResponse)
async def get_settings(
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get restaurant settings"""
    settings = get_settings_by_restaurant_id(restaurant_id)
    
    if not settings:
        # Return default settings if none exist
        return SettingsResponse(
            id="",
            restaurant_id=restaurant_id,
            whatsapp_notifications_enabled=True,
            whatsapp_number=None,
            email_notifications_enabled=False,
            email_address=None,
            sms_notifications_enabled=False,
            sms_number=None,
            notify_new_order=True,
            notify_preparing=True,
            notify_ready=True,
            notify_delivered=True,
            notify_cancelled=True,
            notify_payment=True,
            sound_enabled=True,
            blink_enabled=True,
            auto_accept_orders=False,
            default_preparation_time=30,
            minimum_order_value=0.0,
            maximum_order_value=None,
            allow_order_modifications=True,
            cancellation_policy=None,
            delivery_available=True,
            delivery_radius_km=None,
            gst_number=None,
            pan_number=None,
            fssai_number=None,
            operating_hours=None
        )
    
    return SettingsResponse(
        id=settings.id,
        restaurant_id=settings.restaurant_id,
        whatsapp_notifications_enabled=settings.whatsapp_notifications_enabled,
        whatsapp_number=settings.whatsapp_number,
        email_notifications_enabled=settings.email_notifications_enabled,
        email_address=settings.email_address,
        sms_notifications_enabled=settings.sms_notifications_enabled,
        sms_number=settings.sms_number,
        notify_new_order=settings.notify_new_order,
        notify_preparing=settings.notify_preparing,
        notify_ready=settings.notify_ready,
        notify_delivered=settings.notify_delivered,
        notify_cancelled=settings.notify_cancelled,
        notify_payment=settings.notify_payment,
        sound_enabled=settings.sound_enabled,
        blink_enabled=settings.blink_enabled,
        auto_accept_orders=settings.auto_accept_orders,
        default_preparation_time=settings.default_preparation_time,
        minimum_order_value=settings.minimum_order_value,
        maximum_order_value=settings.maximum_order_value,
        allow_order_modifications=settings.allow_order_modifications,
        cancellation_policy=settings.cancellation_policy,
        delivery_available=settings.delivery_available,
        delivery_radius_km=settings.delivery_radius_km,
        gst_number=settings.gst_number,
        pan_number=settings.pan_number,
        fssai_number=settings.fssai_number,
        operating_hours=settings.operating_hours
    )


@router.put("/notifications", response_model=SettingsResponse)
async def update_notification_settings(
    notification_settings: NotificationSettingsRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update notification settings"""
    # Get existing settings or create new
    existing_settings = get_settings_by_restaurant_id(restaurant_id)
    
    if existing_settings:
        # Update existing
        existing_settings.whatsapp_notifications_enabled = notification_settings.whatsapp_notifications_enabled
        existing_settings.whatsapp_number = notification_settings.whatsapp_number
        existing_settings.email_notifications_enabled = notification_settings.email_notifications_enabled
        existing_settings.email_address = notification_settings.email_address
        existing_settings.sms_notifications_enabled = notification_settings.sms_notifications_enabled
        existing_settings.sms_number = notification_settings.sms_number
        existing_settings.notify_new_order = notification_settings.notify_new_order
        existing_settings.notify_preparing = notification_settings.notify_preparing
        existing_settings.notify_ready = notification_settings.notify_ready
        existing_settings.notify_delivered = notification_settings.notify_delivered
        existing_settings.notify_cancelled = notification_settings.notify_cancelled
        existing_settings.notify_payment = notification_settings.notify_payment
        existing_settings.sound_enabled = notification_settings.sound_enabled
        existing_settings.blink_enabled = notification_settings.blink_enabled
        updated_settings = create_or_update_settings(existing_settings)
    else:
        # Create new
        new_settings = RestaurantSettings(
            id=generate_settings_id(),
            restaurant_id=restaurant_id,
            whatsapp_notifications_enabled=notification_settings.whatsapp_notifications_enabled,
            whatsapp_number=notification_settings.whatsapp_number,
            email_notifications_enabled=notification_settings.email_notifications_enabled,
            email_address=notification_settings.email_address,
            sms_notifications_enabled=notification_settings.sms_notifications_enabled,
            sms_number=notification_settings.sms_number,
            notify_new_order=notification_settings.notify_new_order,
            notify_preparing=notification_settings.notify_preparing,
            notify_ready=notification_settings.notify_ready,
            notify_delivered=notification_settings.notify_delivered,
            notify_cancelled=notification_settings.notify_cancelled,
            notify_payment=notification_settings.notify_payment,
            sound_enabled=notification_settings.sound_enabled,
            blink_enabled=notification_settings.blink_enabled
        )
        updated_settings = create_or_update_settings(new_settings)
    
    return SettingsResponse(
        id=updated_settings.id,
        restaurant_id=updated_settings.restaurant_id,
        whatsapp_notifications_enabled=updated_settings.whatsapp_notifications_enabled,
        whatsapp_number=updated_settings.whatsapp_number,
        email_notifications_enabled=updated_settings.email_notifications_enabled,
        email_address=updated_settings.email_address,
        sms_notifications_enabled=updated_settings.sms_notifications_enabled,
        sms_number=updated_settings.sms_number,
        notify_new_order=updated_settings.notify_new_order,
        notify_preparing=updated_settings.notify_preparing,
        notify_ready=updated_settings.notify_ready,
        notify_delivered=updated_settings.notify_delivered,
        notify_cancelled=updated_settings.notify_cancelled,
        notify_payment=updated_settings.notify_payment,
        sound_enabled=updated_settings.sound_enabled,
        blink_enabled=updated_settings.blink_enabled,
        auto_accept_orders=updated_settings.auto_accept_orders,
        default_preparation_time=updated_settings.default_preparation_time,
        minimum_order_value=updated_settings.minimum_order_value,
        maximum_order_value=updated_settings.maximum_order_value,
        allow_order_modifications=updated_settings.allow_order_modifications,
        cancellation_policy=updated_settings.cancellation_policy
    )


@router.put("/orders", response_model=SettingsResponse)
async def update_order_settings(
    order_settings: OrderSettingsRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update order settings"""
    # Get existing settings or create new
    existing_settings = get_settings_by_restaurant_id(restaurant_id)
    
    if existing_settings:
        # Update existing
        existing_settings.auto_accept_orders = order_settings.auto_accept_orders
        existing_settings.default_preparation_time = order_settings.default_preparation_time
        existing_settings.minimum_order_value = order_settings.minimum_order_value
        existing_settings.maximum_order_value = order_settings.maximum_order_value
        existing_settings.allow_order_modifications = order_settings.allow_order_modifications
        existing_settings.cancellation_policy = order_settings.cancellation_policy
        existing_settings.delivery_available = order_settings.delivery_available
        updated_settings = create_or_update_settings(existing_settings)
    else:
        # Create new with defaults
        new_settings = RestaurantSettings(
            id=generate_settings_id(),
            restaurant_id=restaurant_id,
            auto_accept_orders=order_settings.auto_accept_orders,
            default_preparation_time=order_settings.default_preparation_time,
            minimum_order_value=order_settings.minimum_order_value,
            maximum_order_value=order_settings.maximum_order_value,
            allow_order_modifications=order_settings.allow_order_modifications,
            cancellation_policy=order_settings.cancellation_policy,
            delivery_available=order_settings.delivery_available
        )
        updated_settings = create_or_update_settings(new_settings)
    
    return SettingsResponse(
        id=updated_settings.id,
        restaurant_id=updated_settings.restaurant_id,
        whatsapp_notifications_enabled=updated_settings.whatsapp_notifications_enabled,
        whatsapp_number=updated_settings.whatsapp_number,
        email_notifications_enabled=updated_settings.email_notifications_enabled,
        email_address=updated_settings.email_address,
        sms_notifications_enabled=updated_settings.sms_notifications_enabled,
        sms_number=updated_settings.sms_number,
        notify_new_order=updated_settings.notify_new_order,
        notify_preparing=updated_settings.notify_preparing,
        notify_ready=updated_settings.notify_ready,
        notify_delivered=updated_settings.notify_delivered,
        notify_cancelled=updated_settings.notify_cancelled,
        notify_payment=updated_settings.notify_payment,
        sound_enabled=updated_settings.sound_enabled,
        blink_enabled=updated_settings.blink_enabled,
        auto_accept_orders=updated_settings.auto_accept_orders,
        default_preparation_time=updated_settings.default_preparation_time,
        minimum_order_value=updated_settings.minimum_order_value,
        maximum_order_value=updated_settings.maximum_order_value,
        allow_order_modifications=updated_settings.allow_order_modifications,
        cancellation_policy=updated_settings.cancellation_policy,
        delivery_radius_km=updated_settings.delivery_radius_km,
        gst_number=updated_settings.gst_number,
        pan_number=updated_settings.pan_number,
        fssai_number=updated_settings.fssai_number,
        operating_hours=updated_settings.operating_hours
    )


@router.post("/test-notification")
async def send_test_notification(
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Send a test WhatsApp notification to the restaurant owner"""
    from repositories.restaurant_repo import get_restaurant_by_id
    
    try:
        # Get restaurant settings
        settings = get_settings_by_restaurant_id(restaurant_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        
        # Check if WhatsApp notifications are enabled
        if not settings.whatsapp_notifications_enabled:
            raise HTTPException(
                status_code=400, 
                detail="WhatsApp notifications are disabled. Please enable them in settings first."
            )
        
        # Get WhatsApp number
        whatsapp_number = None
        if settings.whatsapp_number:
            whatsapp_number = settings.whatsapp_number
        else:
            # Fallback to restaurant phone
            restaurant = get_restaurant_by_id(restaurant_id)
            if restaurant:
                whatsapp_number = restaurant.phone
            else:
                raise HTTPException(status_code=404, detail="Restaurant not found")
        
        if not whatsapp_number:
            raise HTTPException(
                status_code=400,
                detail="No WhatsApp number configured. Please set a WhatsApp number in settings."
            )
        
        # Format phone number
        formatted_number = format_phone_number(whatsapp_number)
        
        # Create test message
        test_message = (
            "🧪 *Test Notification*\n\n"
            "This is a test notification from your restaurant dashboard.\n\n"
            "✅ If you received this message, your WhatsApp notifications are working correctly!\n\n"
            "You will receive notifications for:\n"
            "• New orders\n"
            "• Order status updates\n"
            "• Payment confirmations\n\n"
            "Thank you for using our service! 🙏"
        )
        
        # Send WhatsApp message
        await send_whatsapp_message(formatted_number, test_message)
        
        logger.info(f"✅ Test notification sent to {formatted_number} for restaurant {restaurant_id}")
        
        return {
            "success": True,
            "message": "Test notification sent successfully! Check your WhatsApp.",
            "recipient": formatted_number
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send test notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test notification: {str(e)}")


@router.put("/profile", response_model=SettingsResponse)
async def update_profile_settings(
    profile: ProfileSettingsRequest,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """
    Update restaurant profile information.
    - Basic details (name, phone, address, location) are stored in restaurants table
    - Business details (delivery radius, GST/PAN/FSSAI, operating hours) are stored in restaurant_settings
    """
    db = SessionLocal()
    try:
        # Update Restaurant basic info
        restaurant = db.query(RestaurantDB).filter(RestaurantDB.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        restaurant.name = profile.restaurant_name
        restaurant.phone = profile.phone
        restaurant.address = profile.address
        restaurant.latitude = profile.latitude
        restaurant.longitude = profile.longitude

        db.commit()
        db.refresh(restaurant)
    finally:
        db.close()

    # Update settings (business details)
    existing_settings = get_settings_by_restaurant_id(restaurant_id)
    if existing_settings:
        existing_settings.delivery_radius_km = profile.delivery_radius_km
        existing_settings.gst_number = profile.gst_number
        existing_settings.pan_number = profile.pan_number
        existing_settings.fssai_number = profile.fssai_number
        existing_settings.operating_hours = (
            None if profile.operating_hours is None else __import__("json").dumps(profile.operating_hours)
        )
        updated_settings = create_or_update_settings(existing_settings)
    else:
        new_settings = RestaurantSettings(
            id=generate_settings_id(),
            restaurant_id=restaurant_id,
            delivery_radius_km=profile.delivery_radius_km,
            gst_number=profile.gst_number,
            pan_number=profile.pan_number,
            fssai_number=profile.fssai_number,
            operating_hours=None if profile.operating_hours is None else __import__("json").dumps(profile.operating_hours),
        )
        updated_settings = create_or_update_settings(new_settings)

    return SettingsResponse(
        id=updated_settings.id,
        restaurant_id=updated_settings.restaurant_id,
        whatsapp_notifications_enabled=updated_settings.whatsapp_notifications_enabled,
        whatsapp_number=updated_settings.whatsapp_number,
        email_notifications_enabled=updated_settings.email_notifications_enabled,
        email_address=updated_settings.email_address,
        sms_notifications_enabled=updated_settings.sms_notifications_enabled,
        sms_number=updated_settings.sms_number,
        notify_new_order=updated_settings.notify_new_order,
        notify_preparing=updated_settings.notify_preparing,
        notify_ready=updated_settings.notify_ready,
        notify_delivered=updated_settings.notify_delivered,
        notify_cancelled=updated_settings.notify_cancelled,
        notify_payment=updated_settings.notify_payment,
        sound_enabled=updated_settings.sound_enabled,
        blink_enabled=updated_settings.blink_enabled,
        auto_accept_orders=updated_settings.auto_accept_orders,
        default_preparation_time=updated_settings.default_preparation_time,
        minimum_order_value=updated_settings.minimum_order_value,
        maximum_order_value=updated_settings.maximum_order_value,
        allow_order_modifications=updated_settings.allow_order_modifications,
        cancellation_policy=updated_settings.cancellation_policy,
        delivery_radius_km=updated_settings.delivery_radius_km,
        gst_number=updated_settings.gst_number,
        pan_number=updated_settings.pan_number,
        fssai_number=updated_settings.fssai_number,
        operating_hours=updated_settings.operating_hours
    )
