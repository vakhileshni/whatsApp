"""
Restaurant Settings Repository
"""
from typing import Optional
from database import SessionLocal
from models_db import RestaurantSettingsDB
from models.restaurant_settings import RestaurantSettings
from id_generator import generate_settings_id


def get_settings_by_restaurant_id(restaurant_id: str) -> Optional[RestaurantSettings]:
    """Get restaurant settings by restaurant ID"""
    db = SessionLocal()
    try:
        db_settings = db.query(RestaurantSettingsDB).filter(
            RestaurantSettingsDB.restaurant_id == restaurant_id
        ).first()
        
        if not db_settings:
            return None
        
        return RestaurantSettings(
            id=db_settings.id,
            restaurant_id=db_settings.restaurant_id,
            whatsapp_notifications_enabled=db_settings.whatsapp_notifications_enabled,
            whatsapp_number=db_settings.whatsapp_number,
            email_notifications_enabled=db_settings.email_notifications_enabled,
            email_address=db_settings.email_address,
            sms_notifications_enabled=db_settings.sms_notifications_enabled,
            sms_number=db_settings.sms_number,
            notify_new_order=db_settings.notify_new_order,
            notify_preparing=db_settings.notify_preparing,
            notify_ready=db_settings.notify_ready,
            notify_delivered=db_settings.notify_delivered,
            notify_cancelled=db_settings.notify_cancelled,
            notify_payment=db_settings.notify_payment,
            sound_enabled=db_settings.sound_enabled,
            blink_enabled=db_settings.blink_enabled,
            auto_accept_orders=db_settings.auto_accept_orders,
            default_preparation_time=db_settings.default_preparation_time,
            minimum_order_value=float(db_settings.minimum_order_value) if db_settings.minimum_order_value else 0.0,
            maximum_order_value=float(db_settings.maximum_order_value) if db_settings.maximum_order_value else None,
            allow_order_modifications=db_settings.allow_order_modifications,
            cancellation_policy=db_settings.cancellation_policy,
            delivery_available=getattr(db_settings, 'delivery_available', True),  # Default to True if column doesn't exist
            delivery_radius_km=db_settings.delivery_radius_km,
            gst_number=db_settings.gst_number,
            pan_number=db_settings.pan_number,
            fssai_number=db_settings.fssai_number,
            operating_hours=db_settings.operating_hours
        )
    finally:
        db.close()


def create_or_update_settings(settings: RestaurantSettings) -> RestaurantSettings:
    """Create or update restaurant settings"""
    db = SessionLocal()
    try:
        # Check if settings exist
        db_settings = db.query(RestaurantSettingsDB).filter(
            RestaurantSettingsDB.restaurant_id == settings.restaurant_id
        ).first()
        
        if db_settings:
            # Update existing
            db_settings.whatsapp_notifications_enabled = settings.whatsapp_notifications_enabled
            db_settings.whatsapp_number = settings.whatsapp_number
            db_settings.email_notifications_enabled = settings.email_notifications_enabled
            db_settings.email_address = settings.email_address
            db_settings.sms_notifications_enabled = settings.sms_notifications_enabled
            db_settings.sms_number = settings.sms_number
            db_settings.notify_new_order = settings.notify_new_order
            db_settings.notify_preparing = settings.notify_preparing
            db_settings.notify_ready = settings.notify_ready
            db_settings.notify_delivered = settings.notify_delivered
            db_settings.notify_cancelled = settings.notify_cancelled
            db_settings.notify_payment = settings.notify_payment
            db_settings.sound_enabled = settings.sound_enabled
            db_settings.blink_enabled = settings.blink_enabled
            db_settings.auto_accept_orders = settings.auto_accept_orders
            db_settings.default_preparation_time = settings.default_preparation_time
            db_settings.minimum_order_value = settings.minimum_order_value
            db_settings.maximum_order_value = settings.maximum_order_value
            db_settings.allow_order_modifications = settings.allow_order_modifications
            db_settings.cancellation_policy = settings.cancellation_policy
            db_settings.delivery_available = settings.delivery_available
            db_settings.delivery_radius_km = settings.delivery_radius_km
            db_settings.gst_number = settings.gst_number
            db_settings.pan_number = settings.pan_number
            db_settings.fssai_number = settings.fssai_number
            db_settings.operating_hours = settings.operating_hours
        else:
            # Create new
            if not settings.id:
                settings.id = generate_settings_id()
            
            db_settings = RestaurantSettingsDB(
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
            db.add(db_settings)
        
        db.commit()
        db.refresh(db_settings)
        
        # Return updated settings
        return RestaurantSettings(
            id=db_settings.id,
            restaurant_id=db_settings.restaurant_id,
            whatsapp_notifications_enabled=db_settings.whatsapp_notifications_enabled,
            whatsapp_number=db_settings.whatsapp_number,
            email_notifications_enabled=db_settings.email_notifications_enabled,
            email_address=db_settings.email_address,
            sms_notifications_enabled=db_settings.sms_notifications_enabled,
            sms_number=db_settings.sms_number,
            notify_new_order=db_settings.notify_new_order,
            notify_preparing=db_settings.notify_preparing,
            notify_ready=db_settings.notify_ready,
            notify_delivered=db_settings.notify_delivered,
            notify_cancelled=db_settings.notify_cancelled,
            notify_payment=db_settings.notify_payment,
            sound_enabled=db_settings.sound_enabled,
            blink_enabled=db_settings.blink_enabled,
            auto_accept_orders=db_settings.auto_accept_orders,
            default_preparation_time=db_settings.default_preparation_time,
            minimum_order_value=float(db_settings.minimum_order_value) if db_settings.minimum_order_value else 0.0,
            maximum_order_value=float(db_settings.maximum_order_value) if db_settings.maximum_order_value else None,
            allow_order_modifications=db_settings.allow_order_modifications,
            cancellation_policy=db_settings.cancellation_policy,
            delivery_available=getattr(db_settings, 'delivery_available', True),  # Default to True if column doesn't exist
            delivery_radius_km=db_settings.delivery_radius_km,
            gst_number=db_settings.gst_number,
            pan_number=db_settings.pan_number,
            fssai_number=db_settings.fssai_number,
            operating_hours=db_settings.operating_hours
        )
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()
