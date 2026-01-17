"""
Script to create notifications for existing orders
This will backfill notifications for orders that were created before the notification system was implemented
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from repositories.order_repo import get_orders_by_restaurant
from repositories.restaurant_repo import get_all_restaurants
from repositories.notification_repo import create_notification, get_notifications_by_restaurant
from models.notification import RestaurantNotification
from services.whatsapp_service import get_restaurant_notification_message, format_phone_number
from repositories.settings_repo import get_settings_by_restaurant_id
import asyncio

async def create_notifications_for_existing_orders():
    """Create notifications for all existing orders"""
    print("=" * 60)
    print("Creating Notifications for Existing Orders")
    print("=" * 60)
    
    restaurants = get_all_restaurants()
    if not restaurants:
        print("❌ No restaurants found!")
        return
    
    total_notifications_created = 0
    
    for restaurant in restaurants:
        print(f"\n📦 Processing restaurant: {restaurant.name} (ID: {restaurant.id})")
        
        # Get orders
        orders = get_orders_by_restaurant(restaurant.id)
        if not orders:
            print(f"   ⚠️  No orders found")
            continue
        
        print(f"   ✅ Found {len(orders)} order(s)")
        
        # Get settings
        settings = get_settings_by_restaurant_id(restaurant.id)
        
        # Get WhatsApp number
        whatsapp_number = None
        if settings and settings.whatsapp_number:
            whatsapp_number = settings.whatsapp_number
        else:
            whatsapp_number = restaurant.phone
        
        if whatsapp_number:
            whatsapp_number = format_phone_number(whatsapp_number)
        
        # Get existing notifications for this restaurant
        existing_notifications = get_notifications_by_restaurant(restaurant.id, limit=1000)
        existing_order_ids = {n.order_id for n in existing_notifications if n.order_id}
        
        # Create notifications for orders that don't have one
        for order in orders:
            if order.id in existing_order_ids:
                print(f"   ⏭️  Order {order.id[:8]} already has notification, skipping")
                continue
            
            # Determine event based on order status
            event_map = {
                "pending": "new_order",
                "preparing": "preparing",
                "ready": "ready",
                "delivered": "delivered",
                "cancelled": "cancelled"
            }
            event = event_map.get(order.status, "new_order")
            
            # Generate message
            message = get_restaurant_notification_message(order, event)
            
            # Determine status
            status = "pending"
            error_message = None
            
            if not whatsapp_number:
                status = "skipped"
                error_message = "No WhatsApp number configured"
            elif settings and not settings.whatsapp_notifications_enabled:
                status = "disabled"
                error_message = "WhatsApp notifications disabled in settings"
            elif settings:
                # Check if event is enabled
                if event == "new_order" and not settings.notify_new_order:
                    status = "disabled"
                    error_message = f"Event '{event}' notifications disabled in settings"
                elif event == "preparing" and not settings.notify_preparing:
                    status = "disabled"
                    error_message = f"Event '{event}' notifications disabled in settings"
                elif event == "ready" and not settings.notify_ready:
                    status = "disabled"
                    error_message = f"Event '{event}' notifications disabled in settings"
                elif event == "delivered" and not settings.notify_delivered:
                    status = "disabled"
                    error_message = f"Event '{event}' notifications disabled in settings"
                elif event == "cancelled" and not settings.notify_cancelled:
                    status = "disabled"
                    error_message = f"Event '{event}' notifications disabled in settings"
            
            # Create notification
            notification = RestaurantNotification(
                id="",
                restaurant_id=restaurant.id,
                order_id=order.id,
                notification_type="whatsapp",
                notification_event=event,
                recipient=whatsapp_number or "",
                message_body=message,
                status=status,
                error_message=error_message
            )
            
            try:
                saved_notification = create_notification(notification)
                print(f"   ✅ Created notification for order {order.id[:8]} (status: {status}, ID: {saved_notification.id})")
                total_notifications_created += 1
            except Exception as e:
                print(f"   ❌ Failed to create notification for order {order.id[:8]}: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"✅ Total notifications created: {total_notifications_created}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(create_notifications_for_existing_orders())
