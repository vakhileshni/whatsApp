"""
WhatsApp Service - Handle WhatsApp messaging via Twilio
"""
import logging
from typing import Optional
from models.order import Order
from models.notification import RestaurantNotification
from repositories.notification_repo import create_notification
from repositories.settings_repo import get_settings_by_restaurant_id

logger = logging.getLogger(__name__)

# Twilio credentials (should be in environment variables)
TWILIO_ACCOUNT_SID = "AC86fcf2e736ee575dc4403337c0ffc5da"
TWILIO_AUTH_TOKEN = "f09de2609a6290b8d641ea91065c8050"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Your Twilio WhatsApp number

async def send_whatsapp_message(to_number: str, message: str, interactive_buttons: Optional[list] = None):
    """
    Send WhatsApp message via Twilio
    If interactive_buttons is provided, sends an interactive message with clickable buttons
    interactive_buttons format: [{"id": "button1", "title": "Accept"}, ...]
    """
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Format phone number for Twilio
        # Remove whatsapp: prefix if present (we'll add it back)
        if to_number.startswith("whatsapp:"):
            to_number = to_number.replace("whatsapp:", "")
        
        # Ensure it has + prefix for Twilio
        if not to_number.startswith("+"):
            to_number = f"+{to_number}"
        
        # Add whatsapp: prefix for Twilio API
        to_number = f"whatsapp:{to_number}"
        
        logger.info(f"📤 Sending WhatsApp message to {to_number}")
        logger.debug(f"   Message preview: {message[:100]}...")
        
        # If interactive buttons are provided, use Content API for interactive messages
        if interactive_buttons and len(interactive_buttons) > 0:
            try:
                # Create interactive message with buttons using Twilio Content API
                # Format: https://www.twilio.com/docs/content/whatsapp/interactive-messages
                content_sid = None  # We'll create content dynamically
                
                # For now, send as regular message with formatted buttons
                # Twilio's interactive buttons require Content API setup
                # As a workaround, format message with clear button-like text
                formatted_message = message
                if len(interactive_buttons) <= 3:  # WhatsApp supports max 3 buttons
                    formatted_message += "\n\n━━━━━━━━━━━━━━━━\n"
                    formatted_message += "⚡ *Tap to copy & reply:*\n\n"
                    for btn in interactive_buttons:
                        formatted_message += f"📌 {btn.get('title', btn.get('id', ''))}\n"
                        formatted_message += f"   → {btn.get('command', '')}\n\n"
                
                message_obj = client.messages.create(
                    from_=TWILIO_WHATSAPP_NUMBER,
                    to=to_number,
                    body=formatted_message
                )
                logger.info(f"✅ WhatsApp interactive message sent to {to_number}: {message_obj.sid}")
                return message_obj
            except Exception as e:
                logger.warning(f"⚠️ Failed to send interactive message, falling back to regular: {e}")
                # Fall through to regular message
        
        # Regular message (no interactive buttons or fallback)
        message_obj = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number,
            body=message
        )
        logger.info(f"✅ WhatsApp message sent successfully to {to_number}: {message_obj.sid}")
        return message_obj
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message to {to_number}: {e}")
        logger.error(f"   Error type: {type(e).__name__}")
        logger.error(f"   Error details: {str(e)}")
        # In development, log what would be sent
        logger.info(f"📤 Would send to {to_number}: {message[:200]}...")
        raise

async def send_order_status_notification(order: Order, new_status: str, old_status: Optional[str] = None):
    """Send WhatsApp notification when order status changes"""
    from repositories.restaurant_repo import get_restaurant_by_id
    
    restaurant = get_restaurant_by_id(order.restaurant_id)
    if not restaurant:
        logger.error(f"Restaurant not found for order {order.id}")
        return
    
    # Get status message
    message = get_status_message(order, new_status, old_status)
    
    # Format phone number for WhatsApp
    phone_number = order.customer_phone.strip()
    
    # Remove whatsapp: prefix if present (will be added by send_whatsapp_message)
    if phone_number.startswith("whatsapp:"):
        phone_number = phone_number.replace("whatsapp:", "")
    
    # Remove + prefix if present
    if phone_number.startswith("+"):
        phone_number = phone_number[1:]
    
    # Remove spaces
    phone_number = phone_number.replace(" ", "")
    
    # Ensure it has country code format (e.g., 919452151637)
    # If it's 10 digits, assume it's Indian number and add 91
    if len(phone_number) == 10 and not phone_number.startswith("91"):
        phone_number = f"91{phone_number}"
    
    # Send notification
    try:
        await send_whatsapp_message(phone_number, message)
        logger.info(f"✅ Order notification sent to {phone_number} for order {order.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send order notification to {phone_number} for order {order.id}: {e}")
        # Don't raise - we don't want notification failures to break order creation/updates

def get_ready_message(order: Order, restaurant) -> str:
    """Generate ready message with location for pickup orders"""
    restaurant_name = restaurant.name if restaurant else "Restaurant"
    base_message = f"🎉 *Order Ready!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} is ready!\n\n*Restaurant:* {restaurant_name}\n*Total:* ₹{order.total_amount:.0f}\n\n"
    
    if order.order_type == 'delivery':
        base_message += "Your order will be delivered to you shortly.\n\n"
    else:
        # Pickup order - add location and Google Maps link
        base_message += "📍 *Please come to pick up your order.*\n\n"
        
        if restaurant and restaurant.address:
            base_message += f"*Address:* {restaurant.address}\n\n"
        
        # Add Google Maps link if restaurant has coordinates
        if restaurant and restaurant.latitude and restaurant.longitude:
            maps_link = f"https://www.google.com/maps?q={restaurant.latitude},{restaurant.longitude}"
            base_message += f"🗺️ *Get Directions:*\n{maps_link}\n\n"
            base_message += "Tap the link above to open Google Maps and navigate to our location.\n\n"
        elif restaurant and restaurant.address:
            # Fallback: use address for Google Maps search
            import urllib.parse
            encoded_address = urllib.parse.quote(restaurant.address)
            maps_link = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
            base_message += f"🗺️ *Get Directions:*\n{maps_link}\n\n"
            base_message += "Tap the link above to open Google Maps and navigate to our location.\n\n"
    
    base_message += "Thank you for choosing us! 🙏"
    return base_message

def get_preparing_message(order: Order, restaurant) -> str:
    """Generate preparing message with location info for pickup orders"""
    restaurant_name = restaurant.name if restaurant else "Restaurant"
    base_message = f"👨‍🍳 *Order Being Prepared*\n\nHi {order.customer_name}!\n\nGreat news! Your order #{order.id[:8]} is now being prepared in our kitchen.\n\n*Restaurant:* {restaurant_name}\n*Total:* ₹{order.total_amount:.0f}\n\n"
    
    if order.order_type == 'pickup':
        base_message += "📍 *Pickup Location:*\n"
        if restaurant and restaurant.address:
            base_message += f"{restaurant.address}\n\n"
        
        # Add Google Maps link if restaurant has coordinates
        if restaurant and restaurant.latitude and restaurant.longitude:
            maps_link = f"https://www.google.com/maps?q={restaurant.latitude},{restaurant.longitude}"
            base_message += f"🗺️ *View Location:*\n{maps_link}\n\n"
        elif restaurant and restaurant.address:
            import urllib.parse
            encoded_address = urllib.parse.quote(restaurant.address)
            maps_link = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
            base_message += f"🗺️ *View Location:*\n{maps_link}\n\n"
    
    base_message += "We'll notify you as soon as it's ready. Estimated time: 15-20 minutes ⏰"
    return base_message

def get_status_message(order: Order, status: str, old_status: Optional[str] = None) -> str:
    """Generate WhatsApp message based on order status"""
    from repositories.restaurant_repo import get_restaurant_by_id
    restaurant = get_restaurant_by_id(order.restaurant_id)
    restaurant_name = restaurant.name if restaurant else "Restaurant"
    
    # Base messages
    base_messages = {
        "pending": f"✅ *Order Confirmed!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} has been received and is now pending.\n\n*Restaurant:* {restaurant_name}\n*Order Type:* {order.order_type.title()}\n*Total:* ₹{order.total_amount:.0f}\n\n*Items:*\n" + "\n".join([f"• {item.product_name} x{item.quantity} - ₹{item.price * item.quantity:.0f}" for item in order.items]) + f"\n\n*Payment:* {'Cash on Delivery' if order.payment_status == 'pending' else 'Online Payment'}\n\nWe'll notify you when we start preparing your order! 🍽️",
        
        "preparing": get_preparing_message(order, restaurant),
        
        "ready": get_ready_message(order, restaurant),
        
        "delivered": f"✅ *Order Delivered!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} has been successfully delivered to you.\n\n*Total:* ₹{order.total_amount:.0f}\n\nThank you for your order! We hope you enjoyed it. 😊\n\nPlease rate your experience and visit us again! ⭐",
        
        "cancelled": f"❌ *Order Cancelled*\n\nHi {order.customer_name}!\n\nUnfortunately, your order #{order.id[:8]} has been cancelled.\n\n*Restaurant:* {restaurant_name}\n*Order Total:* ₹{order.total_amount:.0f}\n\nIf you made a payment, it will be refunded to your account within 3-5 business days.\n\nWe sincerely apologize for any inconvenience caused. 😔\n\n*Please help us improve by sharing your feedback:*\n\n🌟 Rate your experience: Reply with a rating from 1-5 stars\n💬 Share your feedback: Send your comments or suggestions\n\nYour feedback helps us serve you better! 🙏"
    }
    
    message = base_messages.get(status, f"Your order #{order.id[:8]} status has been updated to: {status}")
    
    return message

async def send_upi_payment_link(customer_phone: str, restaurant, order, amount: float):
    """Send UPI payment link via WhatsApp for online payment"""
    import urllib.parse
    
    # Validate inputs
    if not customer_phone or not customer_phone.strip():
        logger.error(f"❌ Empty phone number provided for order {order.id}")
        raise ValueError("Customer phone number is required")
    
    if not restaurant or not restaurant.upi_id:
        logger.error(f"Restaurant {restaurant.id if restaurant else 'None'} does not have UPI ID configured")
        raise ValueError("Restaurant UPI ID not configured")
    
    # Format phone number for WhatsApp
    formatted_phone = format_phone_number(customer_phone)
    logger.info(f"📱 Sending UPI payment link to formatted phone: {formatted_phone} (original: {customer_phone})")
    
    # Validate formatted phone number
    if not formatted_phone or len(formatted_phone) < 10:
        logger.error(f"❌ Invalid phone number format: {formatted_phone} (original: {customer_phone})")
        raise ValueError(f"Invalid phone number format: {customer_phone}")
    
    # Try to use QR code format if available (this ensures exact same format that works)
    upi_link = None
    if restaurant.upi_qr_code and restaurant.upi_qr_code.startswith('data:image/'):
        try:
            from services.qr_decoder import decode_qr_code_from_base64
            qr_string = decode_qr_code_from_base64(restaurant.upi_qr_code)
            
            if qr_string and qr_string.startswith('upi://pay'):
                logger.info(f"✅ Using QR code format for payment link (QR works, so link will work too)")
                # Simply replace the amount parameter in the QR string
                import re
                # Replace am= parameter with new amount (handles both am=100.00 and am=100 formats)
                new_amount = f"{amount:.2f}"
                # Use regex to replace amount parameter while preserving encoding
                upi_link = re.sub(r'am=([^&]+)', f'am={urllib.parse.quote(new_amount)}', qr_string)
                logger.info(f"🔗 Generated UPI link from QR code format:")
                logger.info(f"   Original QR: {qr_string[:150]}...")
                logger.info(f"   New Link: {upi_link[:150]}...")
                logger.info(f"   Amount updated: {new_amount}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to use QR code format, falling back to manual generation: {e}")
    
    # Fallback: Generate UPI payment link manually if QR code format not available
    if not upi_link:
        # Format: upi://pay?pa=<UPI_ID>&pn=<Payee Name>&am=<Amount>&cu=INR&tn=<Transaction Note>
        upi_id = restaurant.upi_id.strip()
        # Keep payee name with spaces (properly encoded) - removing spaces can look suspicious
        payee_name = restaurant.name.strip()
        # Use simpler transaction note - avoid "Order" keyword which might trigger security
        transaction_note = f"Payment {order.id[:8]}"
        
        # UPI amount should be in format: "100.00" (with 2 decimals)
        amount_str = f"{amount:.2f}"
        
        # Encode UPI parameters properly
        upi_link = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn={urllib.parse.quote(payee_name)}&am={amount_str}&cu=INR&tn={urllib.parse.quote(transaction_note)}"
        
        logger.info(f"🔗 Generated UPI link manually for order {order.id}:")
        logger.info(f"   UPI ID: {upi_id}")
        logger.info(f"   Payee Name: {payee_name}")
        logger.info(f"   Amount: {amount_str}")
        logger.info(f"   Transaction Note: {transaction_note}")
        logger.info(f"   Full Link: {upi_link}")
    
    # Create a short WhatsApp message with the payment link
    message = (
        f"💳 *Pay for order* #{order.id[:8]}\n"
        f"Amount: ₹{amount:.0f}\n"
        f"Restaurant: {restaurant.name}\n\n"
        f"🔗 *Tap to pay:*\n{upi_link}"
    )
    
    # Send WhatsApp message
    try:
        await send_whatsapp_message(formatted_phone, message)
        logger.info(f"✅ UPI payment link sent successfully to {formatted_phone} for order {order.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send UPI payment link to {formatted_phone}: {e}")
        logger.error(f"   Original phone: {customer_phone}")
        logger.error(f"   Restaurant UPI ID: {restaurant.upi_id}")
        logger.error(f"   Order ID: {order.id}")
        raise


def format_phone_number(phone: str) -> str:
    """Format phone number for WhatsApp (remove whatsapp: prefix, ensure country code)"""
    phone = phone.strip()
    
    # Remove whatsapp: prefix if present
    if phone.startswith("whatsapp:"):
        phone = phone.replace("whatsapp:", "")
    
    # Remove + prefix if present
    if phone.startswith("+"):
        phone = phone[1:]
    
    # Remove spaces
    phone = phone.replace(" ", "")
    
    # Ensure it has country code format (e.g., 919452151637)
    # If it's 10 digits, assume it's Indian number and add 91
    if len(phone) == 10 and not phone.startswith("91"):
        phone = f"91{phone}"
    
    return phone


async def send_restaurant_order_notification(order: Order, event: str = "new_order"):
    """
    Send WhatsApp notification to restaurant owner when order is created or status changes
    Includes interactive buttons for quick actions
    """
    from repositories.restaurant_repo import get_restaurant_by_id
    
    restaurant = get_restaurant_by_id(order.restaurant_id)
    if not restaurant:
        logger.error(f"Restaurant not found for order {order.id}")
        return
    
    # Get restaurant settings to check notification preferences
    settings = get_settings_by_restaurant_id(restaurant.id)
    if not settings:
        logger.warning(f"No settings found for restaurant {restaurant.id}, using defaults")
        settings = None
    
    # Get restaurant owner's WhatsApp number
    whatsapp_number = None
    if settings and settings.whatsapp_number:
        whatsapp_number = settings.whatsapp_number
    else:
        # Fallback to restaurant phone
        whatsapp_number = restaurant.phone
    
    # Format phone number if available
    if whatsapp_number:
        whatsapp_number = format_phone_number(whatsapp_number)
    
    # Generate notification message with interactive buttons
    message = get_restaurant_notification_message(order, event)
    
    # Prepare interactive buttons for the message
    interactive_buttons = []
    if event == "new_order" and order.status == "pending":
        short_order_id = order.id[:8]
        interactive_buttons = [
            {"id": "accept", "title": "✅ Accept Order", "command": f"ACCEPT {short_order_id}"},
            {"id": "prepare", "title": "👨‍🍳 Start Preparing", "command": f"PREPARE {short_order_id}"},
        ]
        
        # Add payment verification button for online payments
        if order.payment_method == 'online' and order.payment_status != "verified":
            interactive_buttons.append({"id": "verify", "title": "💳 Verify Payment", "command": f"VERIFY {short_order_id}"})
        
        interactive_buttons.append({"id": "cancel", "title": "❌ Cancel Order", "command": f"CANCEL {short_order_id}"})
    
    # Create notification record (ALWAYS save to database)
    notification = RestaurantNotification(
        id="",  # Will be generated
        restaurant_id=restaurant.id,
        order_id=order.id,
        notification_type="whatsapp",
        notification_event=event,
        recipient=whatsapp_number or "",
        message_body=message,
        status="pending"  # Will be updated after sending attempt
    )
    
    # Check if WhatsApp notifications are enabled
    if settings and not settings.whatsapp_notifications_enabled:
        logger.info(f"WhatsApp notifications disabled for restaurant {restaurant.id}")
        notification.status = "disabled"
        notification.error_message = "WhatsApp notifications disabled in settings"
        try:
            create_notification(notification)
        except Exception as e:
            logger.error(f"❌ Failed to save notification record: {e}")
        return
    
    # Check if this event should trigger notification
    if settings:
        should_notify = True
        if event == "new_order" and not settings.notify_new_order:
            should_notify = False
        elif event == "preparing" and not settings.notify_preparing:
            should_notify = False
        elif event == "ready" and not settings.notify_ready:
            should_notify = False
        elif event == "delivered" and not settings.notify_delivered:
            should_notify = False
        elif event == "cancelled" and not settings.notify_cancelled:
            should_notify = False
        elif event == "payment_received" and not settings.notify_payment:
            should_notify = False
        
        if not should_notify:
            notification.status = "disabled"
            notification.error_message = f"Event '{event}' notifications disabled in settings"
            try:
                saved_notification = create_notification(notification)
                logger.info(f"✅ Notification saved (disabled) for order {order.id}, notification ID: {saved_notification.id}")
            except Exception as e:
                logger.error(f"❌ Failed to save notification record: {e}")
                import traceback
                traceback.print_exc()
            return
    
    # If no WhatsApp number, mark as skipped but still save
    if not whatsapp_number:
        logger.warning(f"No WhatsApp number configured for restaurant {restaurant.id}")
        notification.status = "skipped"
        notification.error_message = "No WhatsApp number configured"
        try:
            saved_notification = create_notification(notification)
            logger.info(f"✅ Notification saved (skipped) for order {order.id}, notification ID: {saved_notification.id}")
        except Exception as e:
            logger.error(f"❌ Failed to save notification record: {e}")
            import traceback
            traceback.print_exc()
        return
    
    # Try to send WhatsApp message
    try:
        # Send WhatsApp message with interactive buttons
        await send_whatsapp_message(whatsapp_number, message, interactive_buttons=interactive_buttons if interactive_buttons else None)
        
        # Update notification status to delivered
        notification.status = "delivered"
        logger.info(f"✅ Restaurant notification sent to {whatsapp_number} for order {order.id}")
    except Exception as e:
        # Update notification status to failed
        notification.status = "failed"
        notification.error_message = str(e)
        logger.error(f"❌ Failed to send restaurant notification: {e}")
        # Don't raise - we don't want notification failures to break order creation/updates
    
    # ALWAYS save notification to database (even if sending failed)
    try:
        saved_notification = create_notification(notification)
        logger.info(f"✅ Notification saved to database for order {order.id}, status: {notification.status}, notification ID: {saved_notification.id}")
    except Exception as e:
        logger.error(f"❌ Failed to save notification record: {e}")
        import traceback
        traceback.print_exc()


def get_restaurant_notification_message(order: Order, event: str) -> str:
    """Generate WhatsApp message for restaurant owner with interactive buttons"""
    from repositories.restaurant_repo import get_restaurant_by_id
    
    restaurant = get_restaurant_by_id(order.restaurant_id)
    restaurant_name = restaurant.name if restaurant else "Restaurant"
    
    # Short order ID for display
    short_order_id = order.id[:8]
    
    # Format order items
    items_text = "\n".join([
        f"• {item.product_name} x{item.quantity} - ₹{item.price * item.quantity:.0f}"
        for item in order.items
    ])
    
    # Base message with order details
    base_message = f"📦 *New Order Received from WhatsApp* #{short_order_id}\n\n"
    base_message += f"*Customer:* {order.customer_name}\n"
    base_message += f"*Phone:* {order.customer_phone}\n"
    base_message += f"*Type:* {order.order_type.title()}\n"
    base_message += f"*Total:* ₹{order.total_amount:.0f}\n"
    base_message += f"*Payment:* {'Cash on Delivery' if order.payment_method == 'cod' else 'Online Payment'}\n"
    
    # Add payment status and details for online payments
    if order.payment_method == 'online':
        payment_status_text = "✅ Verified" if order.payment_status == "verified" else "⏳ Pending"
        base_message += f"*Payment Status:* {payment_status_text}\n"
        
        # Show customer payment details if available (for verification)
        if order.customer_upi_name:
            base_message += f"*Payment From:* {order.customer_upi_name}\n"
        elif order.payment_status == "pending":
            base_message += "*Payment From:* Waiting for customer payment details\n"
    
    base_message += "\n"
    
    if order.delivery_address:
        base_message += f"*Delivery Address:*\n{order.delivery_address}\n\n"
    
    base_message += f"*Items:*\n{items_text}\n\n"
    
    # Add interactive buttons based on order status
    if event == "new_order" and order.status == "pending":
        base_message += "━━━━━━━━━━━━━━━━\n"
        base_message += "⚡ *Quick Actions:*\n\n"
        base_message += "Tap to copy & reply:\n\n"
        base_message += f"✅ *ACCEPT {short_order_id}* - Accept order\n"
        base_message += f"👨‍🍳 *PREPARE {short_order_id}* - Start preparing\n"
        
        # Add payment verification button for online payments
        if order.payment_method == 'online' and order.payment_status != "verified":
            base_message += f"💳 *VERIFY {short_order_id}* - Verify payment\n"
        
        base_message += f"❌ *CANCEL {short_order_id}* - Cancel order\n\n"
        base_message += "Or manage orders in your dashboard:\n"
        base_message += "http://localhost:3000/dashboard\n"
    elif event == "preparing":
        base_message += "━━━━━━━━━━━━━━━━\n"
        base_message += "⚡ *Quick Actions:*\n\n"
        base_message += f"🎉 *READY {short_order_id}* - Mark as ready\n"
        base_message += f"❌ *CANCEL {short_order_id}* - Cancel order\n"
    elif event == "ready":
        base_message += "━━━━━━━━━━━━━━━━\n"
        base_message += "⚡ *Quick Actions:*\n\n"
        base_message += f"✅ *DELIVERED {short_order_id}* - Mark as delivered\n"
    elif event == "payment_received":
        base_message += "💳 *Payment Received*\n\n"
        base_message += f"Payment of ₹{order.total_amount:.0f} has been received for order #{short_order_id}.\n"
    
    return base_message
    