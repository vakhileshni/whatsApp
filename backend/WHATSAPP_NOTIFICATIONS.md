# WhatsApp Order Status Notifications

## Overview

The system automatically sends WhatsApp notifications to customers whenever their order status changes. This provides real-time updates to customers about their order progress.

## How It Works

1. **Order Status Update**: When a restaurant admin updates an order status in the dashboard, the system:
   - Updates the order status in the database
   - Generates a personalized WhatsApp message based on the new status
   - Sends the message to the customer's phone number via WhatsApp

2. **Message Templates**: Each status has a custom message template:
   - **Pending**: Order confirmation message
   - **Preparing**: Kitchen is preparing the order
   - **Ready**: Order is ready for pickup/delivery
   - **Delivered**: Order completion confirmation
   - **Cancelled**: Order cancellation notification

## Setup Instructions

### Option 1: Using Twilio WhatsApp API (Production)

1. **Install Twilio package** (already in requirements.txt):
   ```bash
   pip install twilio
   ```

2. **Get Twilio credentials**:
   - Sign up at https://www.twilio.com
   - Get your Account SID and Auth Token from the dashboard
   - Set up a WhatsApp-enabled phone number

3. **Configure environment variables**:
   Create a `.env` file in the backend directory:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

4. **Test the setup**:
   - Update an order status in the dashboard
   - Check the backend logs to see if the message was sent
   - Customer should receive the WhatsApp message

### Option 2: Development Mode (Logging Only)

If Twilio credentials are not configured, the system will:
- Log all messages to the console instead of sending them
- Show you exactly what message would be sent
- Allow you to test the notification system without Twilio setup

Check the backend logs when updating order status to see the messages.

## Message Format

Messages are formatted with:
- **Bold text** using WhatsApp markdown (`*text*`)
- Personalized customer name
- Order ID (shortened)
- Order total amount
- Status-specific content and emojis

## Example Messages

### Order Being Prepared
```
👨‍🍳 *Order Being Prepared*

Hi Rajesh!

Great news! Your order #ORDER_001 is now being prepared in our kitchen.

We'll notify you as soon as it's ready. Estimated time: 15-20 minutes ⏰
```

### Order Ready
```
🎉 *Order Ready!*

Hi Rajesh!

Your order #ORDER_001 is ready!

*For Delivery:*
Your order is ready and will be delivered to you shortly.

*Order Total:* ₹1020.00

Thank you for choosing us! 🙏
```

### Order Delivered
```
✅ *Order Delivered!*

Hi Rajesh!

Your order #ORDER_001 has been successfully delivered to you.

*Order Total:* ₹1020.00

Thank you for your order! We hope you enjoyed it. 😊

Please rate your experience and visit us again! ⭐
```

## Testing

1. **Test in Development Mode** (without Twilio):
   - Update an order status in the dashboard
   - Check backend console logs
   - You'll see: "⚠️ Twilio credentials not configured" and the message content

2. **Test with Twilio** (production):
   - Configure Twilio credentials
   - Update an order status
   - Customer receives WhatsApp message in real-time

## Error Handling

- If Twilio credentials are missing: Messages are logged to console
- If Twilio API fails: Error is logged but order status update still succeeds
- Network issues: Errors are logged without blocking the order update

## Code Structure

- **Service**: `backend/services/whatsapp_service.py`
  - `send_order_status_notification()` - Main notification function
  - `get_status_message()` - Message template generation
  - `send_whatsapp_message()` - Twilio API integration

- **Integration**: `backend/routers/orders.py`
  - Order status update endpoint calls the notification service

- **Order Service**: `backend/services/order_service.py`
  - Returns old status so router can send notification

## Notes

- Notifications are sent asynchronously (non-blocking)
- Order status update succeeds even if notification fails
- Phone numbers are automatically formatted with country code (+91 for India)
- Messages support WhatsApp markdown formatting (bold, emojis)


