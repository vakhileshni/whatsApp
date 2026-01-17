# Restaurant Owner Notifications System

## Overview

This system enables restaurant owners to receive WhatsApp notifications when orders are created or status changes, and allows them to process orders directly from WhatsApp using interactive commands.

## Features

1. **WhatsApp Notifications to Restaurant Owners**
   - Receive notifications when new orders arrive
   - Receive notifications when order status changes
   - Notifications include order details and quick action buttons

2. **Interactive Order Processing from WhatsApp**
   - Restaurant owners can reply with commands to update order status
   - Commands: `ACCEPT`, `PREPARE`, `READY`, `CANCEL`, `DELIVERED`
   - Example: Reply "ACCEPT 000000123" to accept an order

3. **Notification Tracking**
   - All notifications are stored in `restaurant_notifications` table
   - Tracks notification status (sent, delivered, failed, clicked)
   - Records which button was clicked and when

4. **Settings-Based Control**
   - Restaurant owners can enable/disable notifications in Settings → Notifications tab
   - Can configure WhatsApp number for notifications
   - Can choose which events trigger notifications (new order, preparing, ready, etc.)

## Database Schema

### `restaurant_notifications` Table

```sql
CREATE TABLE restaurant_notifications (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NULL,
    notification_type VARCHAR(20) NOT NULL,  -- 'whatsapp', 'email', 'sms'
    notification_event VARCHAR(50) NOT NULL,  -- 'new_order', 'preparing', etc.
    recipient VARCHAR(255) NOT NULL,  -- phone number, email, etc.
    message_body TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',  -- 'sent', 'delivered', 'failed', 'clicked'
    button_clicked VARCHAR(50) NULL,  -- 'accept', 'preparing', 'ready', 'cancel', etc.
    clicked_at TIMESTAMP NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## How It Works

### 1. Order Creation Flow

When a new order is created:

1. Order is saved to database
2. Customer receives WhatsApp notification (existing flow)
3. **NEW**: Restaurant owner receives WhatsApp notification with:
   - Order details (customer name, items, total, address)
   - Quick action buttons (ACCEPT, PREPARE, CANCEL)
   - Dashboard link

### 2. Notification Message Format

```
📦 *New Order #00000012*

*Customer:* John Doe
*Phone:* 919876543210
*Type:* Delivery
*Total:* ₹450.00
*Payment:* Cash on Delivery

*Delivery Address:*
123 Main Street, City

*Items:*
• Margherita Pizza x2 - ₹400.00
• Coke x1 - ₹50.00

━━━━━━━━━━━━━━━━
⚡ *Quick Actions:*

Reply with one of the following:

✅ *ACCEPT 00000012* - Accept order
👨‍🍳 *PREPARE 00000012* - Start preparing
❌ *CANCEL 00000012* - Cancel order

Or manage orders in your dashboard:
http://localhost:3000/dashboard
```

### 3. Processing Restaurant Owner Commands

When restaurant owner replies with a command:

1. System identifies sender as restaurant owner (by phone number)
2. Parses command (ACCEPT, PREPARE, READY, CANCEL, DELIVERED)
3. Extracts order ID from message
4. Updates order status in database
5. Sends confirmation message to restaurant owner
6. Updates notification record (marks as "clicked", records button clicked)
7. Sends notification to customer about status change

### 4. Command Examples

- `ACCEPT 00000012` - Accepts order (status: pending → pending, but acknowledged)
- `PREPARE 00000012` - Starts preparing (status: pending → preparing)
- `READY 00000012` - Marks as ready (status: preparing → ready)
- `CANCEL 00000012` - Cancels order (status: any → cancelled)
- `DELIVERED 00000012` - Marks as delivered (status: ready → delivered)

## Configuration

### Enable/Disable Notifications

1. Go to Dashboard → Settings → Notifications tab
2. Toggle "WhatsApp Notifications" ON/OFF
3. Enter WhatsApp number (if different from restaurant phone)
4. Configure which events trigger notifications:
   - ✅ Notify on new order
   - ✅ Notify when preparing
   - ✅ Notify when ready
   - ✅ Notify when delivered
   - ✅ Notify when cancelled
   - ✅ Notify on payment received

### Setting WhatsApp Number

The system uses:
1. `restaurant_settings.whatsapp_number` (if set in Settings)
2. Falls back to `restaurants.phone` if not set

## API Endpoints

### Notification Tracking (Future)

- `GET /api/v1/notifications` - Get all notifications for restaurant
- `GET /api/v1/notifications/{notification_id}` - Get specific notification
- `GET /api/v1/notifications/order/{order_id}` - Get notifications for an order

## Code Structure

### Files

- **`backend/models/notification.py`** - Notification model
- **`backend/models_db.py`** - `RestaurantNotificationDB` database model
- **`backend/repositories/notification_repo.py`** - Notification repository (CRUD operations)
- **`backend/services/whatsapp_service.py`** - Enhanced with `send_restaurant_order_notification()`
- **`backend/routers/webhook.py`** - Enhanced with `process_restaurant_owner_command()`
- **`backend/routers/orders.py`** - Calls `send_restaurant_order_notification()` on order creation/update

### Key Functions

1. **`send_restaurant_order_notification(order, event)`**
   - Checks notification settings
   - Generates message with interactive buttons
   - Sends WhatsApp message
   - Creates notification record in database

2. **`process_restaurant_owner_command(from_number, body)`**
   - Identifies restaurant owner by phone number
   - Parses command and order ID
   - Updates order status
   - Updates notification record
   - Sends confirmation

3. **`get_restaurant_notification_message(order, event)`**
   - Generates formatted WhatsApp message
   - Includes order details and action buttons

## Testing

### Test Order Creation Notification

1. Create a new order (via frontend or API)
2. Check restaurant owner's WhatsApp (if notifications enabled)
3. Should receive notification with order details and action buttons

### Test Command Processing

1. Send WhatsApp message to Twilio number: `ACCEPT 00000012`
2. System should:
   - Identify you as restaurant owner
   - Update order status
   - Send confirmation message
   - Update notification record

### Check Notification Records

```sql
SELECT * FROM restaurant_notifications 
WHERE restaurant_id = 'your_restaurant_id' 
ORDER BY created_at DESC;
```

## Future Enhancements

1. **Email Notifications** - Send email notifications when enabled
2. **SMS Notifications** - Send SMS notifications when enabled
3. **Notification Dashboard** - View all notifications in frontend
4. **Notification Templates** - Customize notification messages
5. **Batch Notifications** - Send daily/weekly summaries
6. **WhatsApp Interactive Buttons** - Use Twilio's interactive button API (requires template approval)

## Troubleshooting

### Notifications Not Sending

1. Check `restaurant_settings.whatsapp_notifications_enabled = true`
2. Check `restaurant_settings.whatsapp_number` is set (or `restaurants.phone`)
3. Check Twilio credentials in `backend/services/whatsapp_service.py`
4. Check backend logs for errors

### Commands Not Working

1. Verify phone number matches restaurant phone or settings WhatsApp number
2. Check command format: `ACCEPT 00000012` (uppercase, space, order ID)
3. Verify order ID exists and belongs to your restaurant
4. Check backend logs for parsing errors

### Notification Records Not Created

1. Check database connection
2. Verify `restaurant_notifications` table exists
3. Check for database errors in logs
