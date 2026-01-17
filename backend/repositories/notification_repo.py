"""
Notification Repository
"""
from typing import Optional, List
from database import SessionLocal
from models_db import RestaurantNotificationDB
from models.notification import RestaurantNotification
from id_generator import generate_notification_id
from datetime import datetime

def create_notification(notification: RestaurantNotification) -> RestaurantNotification:
    """Create a new notification record"""
    db = SessionLocal()
    try:
        if not notification.id:
            notification.id = generate_notification_id()
        
        db_notification = RestaurantNotificationDB(
            id=notification.id,
            restaurant_id=notification.restaurant_id,
            order_id=notification.order_id,
            notification_type=notification.notification_type,
            notification_event=notification.notification_event,
            recipient=notification.recipient,
            message_body=notification.message_body,
            status=notification.status,
            button_clicked=notification.button_clicked,
            clicked_at=datetime.fromisoformat(notification.clicked_at) if notification.clicked_at else None,
            error_message=notification.error_message
        )
        
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        
        return RestaurantNotification(
            id=db_notification.id,
            restaurant_id=db_notification.restaurant_id,
            order_id=db_notification.order_id,
            notification_type=db_notification.notification_type,
            notification_event=db_notification.notification_event,
            recipient=db_notification.recipient,
            message_body=db_notification.message_body,
            status=db_notification.status,
            button_clicked=db_notification.button_clicked,
            clicked_at=db_notification.clicked_at.isoformat() if db_notification.clicked_at else None,
            error_message=db_notification.error_message,
            created_at=db_notification.created_at.isoformat() if db_notification.created_at else None,
            updated_at=db_notification.updated_at.isoformat() if db_notification.updated_at else None
        )
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def update_notification_status(notification_id: str, status: str, button_clicked: Optional[str] = None, error_message: Optional[str] = None) -> Optional[RestaurantNotification]:
    """Update notification status (e.g., when button is clicked)"""
    db = SessionLocal()
    try:
        db_notification = db.query(RestaurantNotificationDB).filter(
            RestaurantNotificationDB.id == notification_id
        ).first()
        
        if not db_notification:
            return None
        
        db_notification.status = status
        if button_clicked:
            db_notification.button_clicked = button_clicked
            db_notification.clicked_at = datetime.now()
        if error_message:
            db_notification.error_message = error_message
        
        db.commit()
        db.refresh(db_notification)
        
        return RestaurantNotification(
            id=db_notification.id,
            restaurant_id=db_notification.restaurant_id,
            order_id=db_notification.order_id,
            notification_type=db_notification.notification_type,
            notification_event=db_notification.notification_event,
            recipient=db_notification.recipient,
            message_body=db_notification.message_body,
            status=db_notification.status,
            button_clicked=db_notification.button_clicked,
            clicked_at=db_notification.clicked_at.isoformat() if db_notification.clicked_at else None,
            error_message=db_notification.error_message,
            created_at=db_notification.created_at.isoformat() if db_notification.created_at else None,
            updated_at=db_notification.updated_at.isoformat() if db_notification.updated_at else None
        )
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

def get_notifications_by_restaurant(restaurant_id: str, limit: int = 100) -> List[RestaurantNotification]:
    """Get notifications for a restaurant"""
    db = SessionLocal()
    try:
        db_notifications = db.query(RestaurantNotificationDB).filter(
            RestaurantNotificationDB.restaurant_id == restaurant_id
        ).order_by(RestaurantNotificationDB.created_at.desc()).limit(limit).all()
        
        return [
            RestaurantNotification(
                id=n.id,
                restaurant_id=n.restaurant_id,
                order_id=n.order_id,
                notification_type=n.notification_type,
                notification_event=n.notification_event,
                recipient=n.recipient,
                message_body=n.message_body,
                status=n.status,
                button_clicked=n.button_clicked,
                clicked_at=n.clicked_at.isoformat() if n.clicked_at else None,
                error_message=n.error_message,
                created_at=n.created_at.isoformat() if n.created_at else None,
                updated_at=n.updated_at.isoformat() if n.updated_at else None
            )
            for n in db_notifications
        ]
    finally:
        db.close()

def get_notification_by_order_id(order_id: str) -> Optional[RestaurantNotification]:
    """Get the most recent notification for an order"""
    db = SessionLocal()
    try:
        db_notification = db.query(RestaurantNotificationDB).filter(
            RestaurantNotificationDB.order_id == order_id
        ).order_by(RestaurantNotificationDB.created_at.desc()).first()
        
        if not db_notification:
            return None
        
        return RestaurantNotification(
            id=db_notification.id,
            restaurant_id=db_notification.restaurant_id,
            order_id=db_notification.order_id,
            notification_type=db_notification.notification_type,
            notification_event=db_notification.notification_event,
            recipient=db_notification.recipient,
            message_body=db_notification.message_body,
            status=db_notification.status,
            button_clicked=db_notification.button_clicked,
            clicked_at=db_notification.clicked_at.isoformat() if db_notification.clicked_at else None,
            error_message=db_notification.error_message,
            created_at=db_notification.created_at.isoformat() if db_notification.created_at else None,
            updated_at=db_notification.updated_at.isoformat() if db_notification.updated_at else None
        )
    finally:
        db.close()
