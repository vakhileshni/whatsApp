"""
Test script to verify notification saving works
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from repositories.order_repo import get_orders_by_restaurant
from repositories.restaurant_repo import get_all_restaurants
from services.whatsapp_service import send_restaurant_order_notification
import asyncio

async def test_notification_save():
    """Test that notifications are saved when orders exist"""
    print("=" * 60)
    print("Testing Notification Saving")
    print("=" * 60)
    
    # Get all restaurants
    restaurants = get_all_restaurants()
    if not restaurants:
        print("❌ No restaurants found!")
        return
    
    print(f"✅ Found {len(restaurants)} restaurant(s)")
    
    # Get orders for first restaurant
    restaurant = restaurants[0]
    print(f"\n📦 Testing with restaurant: {restaurant.name} (ID: {restaurant.id})")
    
    orders = get_orders_by_restaurant(restaurant.id)
    if not orders:
        print("❌ No orders found for this restaurant!")
        print("   Please create an order first, then run this test again.")
        return
    
    print(f"✅ Found {len(orders)} order(s)")
    
    # Test with first order
    order = orders[0]
    print(f"\n📋 Testing with order: {order.id}")
    print(f"   Status: {order.status}")
    print(f"   Customer: {order.customer_name}")
    
    # Try to send notification
    print("\n🔄 Calling send_restaurant_order_notification...")
    try:
        await send_restaurant_order_notification(order, "new_order")
        print("✅ Function executed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    # Check if notification was saved
    from repositories.notification_repo import get_notifications_by_restaurant
    notifications = get_notifications_by_restaurant(restaurant.id, limit=10)
    
    print(f"\n📊 Notifications in database: {len(notifications)}")
    if notifications:
        print("\nRecent notifications:")
        for n in notifications[:5]:
            print(f"  - ID: {n.id}")
            print(f"    Event: {n.notification_event}")
            print(f"    Status: {n.status}")
            print(f"    Order ID: {n.order_id}")
            print(f"    Created: {n.created_at}")
            print()
    else:
        print("❌ No notifications found in database!")
        print("   This means the notification was not saved.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_notification_save())
