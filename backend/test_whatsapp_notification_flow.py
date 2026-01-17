"""
Test script to verify WhatsApp notification flow works correctly
1. Enable WhatsApp notifications in settings
2. Create an order
3. Verify notification is sent
4. Test processing order from WhatsApp
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from repositories.order_repo import get_orders_by_restaurant, get_order_by_id
from repositories.restaurant_repo import get_all_restaurants
from repositories.settings_repo import get_settings_by_restaurant_id, create_or_update_settings
from models.restaurant_settings import RestaurantSettings
from services.whatsapp_service import send_restaurant_order_notification
import asyncio

async def test_whatsapp_notification_flow():
    """Test the complete WhatsApp notification flow"""
    print("=" * 60)
    print("Testing WhatsApp Notification Flow")
    print("=" * 60)
    
    # Get a restaurant with orders
    restaurants = get_all_restaurants()
    if not restaurants:
        print("❌ No restaurants found!")
        return
    
    # Find restaurant with orders
    restaurant = None
    for r in restaurants:
        orders = get_orders_by_restaurant(r.id)
        if orders:
            restaurant = r
            break
    
    if not restaurant:
        print("❌ No restaurant with orders found!")
        print("   Please create an order first.")
        return
    
    print(f"\n📦 Testing with restaurant: {restaurant.name} (ID: {restaurant.id})")
    print(f"   Phone: {restaurant.phone}")
    
    # Get or create settings
    settings = get_settings_by_restaurant_id(restaurant.id)
    if not settings:
        print("\n⚙️  Creating default settings...")
        settings = RestaurantSettings(
            id="",
            restaurant_id=restaurant.id,
            whatsapp_notifications_enabled=True,
            whatsapp_number=restaurant.phone,
            notify_new_order=True,
            notify_preparing=True,
            notify_ready=True,
            notify_delivered=True,
            notify_cancelled=True,
            notify_payment=True
        )
        settings = create_or_update_settings(settings)
        print("   ✅ Settings created")
    else:
        print("\n⚙️  Current settings:")
        print(f"   WhatsApp notifications enabled: {settings.whatsapp_notifications_enabled}")
        print(f"   WhatsApp number: {settings.whatsapp_number or restaurant.phone}")
        print(f"   Notify new order: {settings.notify_new_order}")
        
        # Enable notifications if disabled
        if not settings.whatsapp_notifications_enabled or not settings.notify_new_order:
            print("\n🔧 Enabling WhatsApp notifications...")
            settings.whatsapp_notifications_enabled = True
            settings.notify_new_order = True
            if not settings.whatsapp_number:
                settings.whatsapp_number = restaurant.phone
            settings = create_or_update_settings(settings)
            print("   ✅ Notifications enabled")
    
    # Get an order
    orders = get_orders_by_restaurant(restaurant.id)
    order = orders[0]
    print(f"\n📋 Testing with order: {order.id}")
    print(f"   Status: {order.status}")
    print(f"   Customer: {order.customer_name}")
    print(f"   Total: ₹{order.total_amount:.0f}")
    
    # Test sending notification
    print("\n📤 Sending WhatsApp notification...")
    try:
        await send_restaurant_order_notification(order, "new_order")
        print("   ✅ Notification function executed successfully!")
        print(f"\n💡 If WhatsApp is configured, you should receive a message on: {settings.whatsapp_number or restaurant.phone}")
        print(f"   The message will include order details and action buttons.")
        print(f"\n💡 To process the order from WhatsApp, reply with:")
        print(f"   - ACCEPT {order.id[:8]} - Accept order")
        print(f"   - PREPARE {order.id[:8]} - Start preparing")
        print(f"   - READY {order.id[:8]} - Mark as ready")
        print(f"   - CANCEL {order.id[:8]} - Cancel order")
        print(f"   - DELIVERED {order.id[:8]} - Mark as delivered")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check notification in database
    from repositories.notification_repo import get_notifications_by_restaurant
    notifications = get_notifications_by_restaurant(restaurant.id, limit=5)
    if notifications:
        latest = notifications[0]
        print(f"\n📊 Latest notification:")
        print(f"   ID: {latest.id}")
        print(f"   Status: {latest.status}")
        print(f"   Event: {latest.notification_event}")
        print(f"   Recipient: {latest.recipient}")
        if latest.error_message:
            print(f"   Error: {latest.error_message}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Check your WhatsApp for the notification message")
    print("2. Reply with a command like: PREPARE " + order.id[:8])
    print("3. The order status should update automatically")
    print("4. You'll receive a confirmation message")

if __name__ == "__main__":
    asyncio.run(test_whatsapp_notification_flow())
