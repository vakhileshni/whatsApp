"""
Notifications Router - API endpoints for restaurant notifications
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from repositories.notification_repo import (
    get_notifications_by_restaurant,
    get_notification_by_order_id
)
import auth

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    id: str
    restaurant_id: str
    order_id: Optional[str] = None
    notification_type: str
    notification_event: str
    recipient: str
    message_body: str
    status: str
    button_clicked: Optional[str] = None
    clicked_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    restaurant_id: str = Depends(auth.get_current_restaurant_id),
    limit: int = Query(100, ge=1, le=1000),
    event: Optional[str] = Query(None, description="Filter by event type"),
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all notifications for current restaurant"""
    try:
        notifications = get_notifications_by_restaurant(restaurant_id, limit=limit)
        
        # Apply filters
        if event:
            notifications = [n for n in notifications if n.notification_event == event]
        if status:
            notifications = [n for n in notifications if n.status == status]
        
        return [
            NotificationResponse(
                id=n.id,
                restaurant_id=n.restaurant_id,
                order_id=n.order_id,
                notification_type=n.notification_type,
                notification_event=n.notification_event,
                recipient=n.recipient,
                message_body=n.message_body,
                status=n.status,
                button_clicked=n.button_clicked,
                clicked_at=n.clicked_at,
                error_message=n.error_message,
                created_at=n.created_at,
                updated_at=n.updated_at
            )
            for n in notifications
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/order/{order_id}", response_model=NotificationResponse)
async def get_notification_by_order(
    order_id: str,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get notification for a specific order"""
    try:
        notification = get_notification_by_order_id(order_id)
        
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        if notification.restaurant_id != restaurant_id:
            raise HTTPException(status_code=403, detail="Not authorized to view this notification")
        
        return NotificationResponse(
            id=notification.id,
            restaurant_id=notification.restaurant_id,
            order_id=notification.order_id,
            notification_type=notification.notification_type,
            notification_event=notification.notification_event,
            recipient=notification.recipient,
            message_body=notification.message_body,
            status=notification.status,
            button_clicked=notification.button_clicked,
            clicked_at=notification.clicked_at,
            error_message=notification.error_message,
            created_at=notification.created_at,
            updated_at=notification.updated_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=dict)
async def get_notification_stats(
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Get notification statistics for current restaurant"""
    try:
        notifications = get_notifications_by_restaurant(restaurant_id, limit=1000)
        
        total = len(notifications)
        delivered = len([n for n in notifications if n.status == "delivered"])
        failed = len([n for n in notifications if n.status == "failed"])
        pending = len([n for n in notifications if n.status in ["pending", "sent"]])
        clicked = len([n for n in notifications if n.button_clicked is not None])
        
        return {
            "total": total,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "clicked": clicked
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
