# WhatsApp Order Processing Guide

## Overview

When a restaurant owner enables WhatsApp notifications in Settings, they will:
1. **Receive WhatsApp notifications** when orders are created or status changes
2. **Process orders directly from WhatsApp** by replying with simple commands

## How to Enable WhatsApp Notifications

### Step 1: Go to Settings
1. Login to your dashboard
2. Click on **Settings** (⚙️ icon in top right)
3. Go to **Notifications** tab

### Step 2: Enable WhatsApp Notifications
1. Toggle **"WhatsApp Notifications"** to **ON** ✅
2. Enter your **WhatsApp Number** (or it will use your restaurant phone number)
3. Enable the events you want to be notified about:
   - ✅ **Notify on new order** - Get notified when new orders arrive
   - ✅ **Notify when preparing** - Get notified when order status changes to preparing
   - ✅ **Notify when ready** - Get notified when order is ready
   - ✅ **Notify when delivered** - Get notified when order is delivered
   - ✅ **Notify when cancelled** - Get notified when order is cancelled
   - ✅ **Notify on payment received** - Get notified when payment is received

4. Click **"Save Changes"**

## What Happens When Enabled

### When a New Order Arrives

You will receive a WhatsApp message like this:

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

## Processing Orders from WhatsApp

### Available Commands

You can reply to the WhatsApp notification with these commands:

| Command | Example | What It Does |
|---------|---------|--------------|
| **ACCEPT** | `ACCEPT 00000012` | Accepts the order (keeps status as pending) |
| **PREPARE** | `PREPARE 00000012` | Starts preparing the order (status: preparing) |
| **READY** | `READY 00000012` | Marks order as ready (status: ready) |
| **CANCEL** | `CANCEL 00000012` | Cancels the order (status: cancelled) |
| **DELIVERED** | `DELIVERED 00000012` | Marks order as delivered (status: delivered) |

### How to Use Commands

1. **Receive notification** on WhatsApp with order details
2. **Reply with command** - Type the command and order ID (first 8 characters)
   - Example: `PREPARE 00000012`
   - You can use the full order ID or just the first 8 characters
3. **Get confirmation** - You'll receive a confirmation message:
   ```
   👨‍🍳 Order 00000012 updated to: *PREPARING*
   
   Customer: John Doe
   Total: ₹450.00
   ```
4. **Order updates automatically** - The order status is updated in your dashboard
5. **Customer is notified** - The customer receives a WhatsApp notification about the status change

## Example Workflow

### Scenario: New Order Arrives

1. **10:00 AM** - Customer places order
2. **10:00 AM** - You receive WhatsApp notification:
   ```
   📦 *New Order #00000012*
   ...
   ```
3. **10:05 AM** - You reply: `PREPARE 00000012`
4. **10:05 AM** - You receive confirmation:
   ```
   👨‍🍳 Order 00000012 updated to: *PREPARING*
   ```
5. **10:05 AM** - Customer receives notification:
   ```
   👨‍🍳 *Order Being Prepared*
   ...
   ```
6. **10:20 AM** - Order is ready, you reply: `READY 00000012`
7. **10:20 AM** - Customer receives notification:
   ```
   🎉 *Order Ready!*
   ...
   ```

## Important Notes

### Phone Number Format
- The system automatically formats phone numbers
- Use your WhatsApp number (with country code, e.g., 919452151637)
- Or use your restaurant phone number (it will be auto-formatted)

### Order ID Format
- You can use the full order ID or just the first 8 characters
- Example: `PREPARE 00000012` or `PREPARE 000000123456789`
- Both will work!

### Command Format
- Commands are **case-insensitive** (ACCEPT, accept, Accept all work)
- Must have a space between command and order ID
- Example: `PREPARE 00000012` ✅
- Example: `PREPARE00000012` ❌ (no space)

### Notifications Are Always Saved
- Even if WhatsApp sending fails, the notification is saved in the database
- You can view all notifications in Dashboard → Notifications
- Check notification status: sent, delivered, failed, disabled, skipped, clicked

## Troubleshooting

### Not Receiving Notifications?

1. **Check Settings:**
   - Go to Dashboard → Settings → Notifications
   - Ensure "WhatsApp Notifications" is **ON**
   - Ensure "Notify on new order" is **ON**
   - Check your WhatsApp number is correct

2. **Check Phone Number:**
   - Make sure your WhatsApp number is correct
   - Format: Country code + number (e.g., 919452151637)
   - The number should be registered with WhatsApp

3. **Check Twilio Configuration:**
   - Ensure Twilio credentials are configured in backend
   - Check backend logs for errors

4. **Check Notification Status:**
   - Go to Dashboard → Notifications
   - Check if notifications are being created
   - Look at the status: "delivered" means sent successfully, "failed" means there was an error

### Commands Not Working?

1. **Check Phone Number:**
   - Make sure you're replying from the same number configured in settings
   - The system identifies you by matching your phone number

2. **Check Command Format:**
   - Use format: `COMMAND ORDER_ID`
   - Example: `PREPARE 00000012`
   - Commands are case-insensitive

3. **Check Order ID:**
   - Use the order ID from the notification message
   - You can use first 8 characters or full ID
   - Make sure the order belongs to your restaurant

4. **Check Backend Logs:**
   - Look for errors in backend console
   - Check if webhook is receiving your messages

## Viewing Notification History

1. Go to **Dashboard → Notifications**
2. View all notifications sent to your restaurant
3. See which buttons were clicked
4. Filter by event type or status
5. View notification statistics

## Security

- Only restaurant owners can process orders via WhatsApp
- System verifies your phone number matches restaurant settings
- Orders can only be updated by the restaurant that owns them
- All actions are logged in the notifications table

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Check backend logs for errors
3. Verify Twilio configuration
4. Check notification status in Dashboard → Notifications
