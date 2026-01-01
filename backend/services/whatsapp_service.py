"""
WhatsApp Service - Handle WhatsApp messaging via Twilio
"""
import logging
from typing import Optional
from models.order import Order

logger = logging.getLogger(__name__)

# Twilio credentials (should be in environment variables)
TWILIO_ACCOUNT_SID = "AC86fcf2e736ee575dc4403337c0ffc5da"
TWILIO_AUTH_TOKEN = "f09de2609a6290b8d641ea91065c8050"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Your Twilio WhatsApp number

async def send_whatsapp_message(to_number: str, message: str):
    """Send WhatsApp message via Twilio"""
    try:
        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Ensure phone number has whatsapp: prefix
        if not to_number.startswith("whatsapp:"):
            to_number = f"whatsapp:{to_number}"
        
        message_obj = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number,
            body=message
        )
        logger.info(f"✅ WhatsApp message sent to {to_number}: {message_obj.sid}")
        return message_obj
    except Exception as e:
        logger.error(f"❌ Failed to send WhatsApp message: {e}")
        # In development, just log the message
        logger.info(f"📤 Would send to {to_number}: {message}")
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

def get_status_message(order: Order, status: str, old_status: Optional[str] = None) -> str:
    """Generate WhatsApp message based on order status"""
    from repositories.restaurant_repo import get_restaurant_by_id
    restaurant = get_restaurant_by_id(order.restaurant_id)
    restaurant_name = restaurant.name if restaurant else "Restaurant"
    
    status_messages = {
        "pending": f"✅ *Order Confirmed!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} has been received and is now pending.\n\n*Restaurant:* {restaurant_name}\n*Order Type:* {order.order_type.title()}\n*Total:* ₹{order.total_amount:.0f}\n\n*Items:*\n" + "\n".join([f"• {item.product_name} x{item.quantity} - ₹{item.price * item.quantity:.0f}" for item in order.items]) + f"\n\n*Payment:* {'Cash on Delivery' if order.payment_status == 'pending' else 'Online Payment'}\n\nWe'll notify you when we start preparing your order! 🍽️",
        
        "preparing": f"👨‍🍳 *Order Being Prepared*\n\nHi {order.customer_name}!\n\nGreat news! Your order #{order.id[:8]} is now being prepared in our kitchen.\n\n*Restaurant:* {restaurant_name}\n*Total:* ₹{order.total_amount:.0f}\n\nWe'll notify you as soon as it's ready. Estimated time: 15-20 minutes ⏰",
        
        "ready": f"🎉 *Order Ready!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} is ready!\n\n*Restaurant:* {restaurant_name}\n*Total:* ₹{order.total_amount:.0f}\n\n{'Your order will be delivered to you shortly.' if order.order_type == 'delivery' else 'Please come to pick up your order.'}\n\nThank you for choosing us! 🙏",
        
        "delivered": f"✅ *Order Delivered!*\n\nHi {order.customer_name}!\n\nYour order #{order.id[:8]} has been successfully delivered to you.\n\n*Total:* ₹{order.total_amount:.0f}\n\nThank you for your order! We hope you enjoyed it. 😊\n\nPlease rate your experience and visit us again! ⭐",
        
        "cancelled": f"❌ *Order Cancelled*\n\nHi {order.customer_name}!\n\nUnfortunately, your order #{order.id[:8]} has been cancelled.\n\n*Restaurant:* {restaurant_name}\n*Order Total:* ₹{order.total_amount:.0f}\n\nIf you made a payment, it will be refunded to your account within 3-5 business days.\n\nWe sincerely apologize for any inconvenience caused. 😔\n\n*Please help us improve by sharing your feedback:*\n\n🌟 Rate your experience: Reply with a rating from 1-5 stars\n💬 Share your feedback: Send your comments or suggestions\n\nYour feedback helps us serve you better! 🙏"
    }
    
    return status_messages.get(status, f"Your order #{order.id[:8]} status has been updated to: {status}")

async def send_upi_payment_link(customer_phone: str, restaurant, order, amount: float):
    """Send UPI payment link via WhatsApp for online payment"""
    import urllib.parse
    
    if not restaurant.upi_id:
        logger.error(f"Restaurant {restaurant.id} does not have UPI ID configured")
        raise ValueError("Restaurant UPI ID not configured")
    
    # Generate UPI payment link
    # Format: upi://pay?pa=<UPI_ID>&pn=<Payee Name>&am=<Amount>&cu=INR&tn=<Transaction Note>
    upi_id = restaurant.upi_id
    payee_name = restaurant.name.replace(" ", "")
    transaction_note = f"Order {order.id[:8]}"
    
    # Encode UPI parameters
    upi_link = f"upi://pay?pa={urllib.parse.quote(upi_id)}&pn={urllib.parse.quote(payee_name)}&am={amount:.2f}&cu=INR&tn={urllib.parse.quote(transaction_note)}"
    
    # Create WhatsApp message with UPI link
    message = f"💳 *Payment Required*\n\n"
    message += f"Hi {order.customer_name}!\n\n"
    message += f"Your order #{order.id[:8]} has been received.\n\n"
    message += f"*Order Total:* ₹{amount:.0f}\n\n"
    message += f"*Restaurant:* {restaurant.name}\n\n"
    message += f"📱 *Click the link below to complete payment:*\n\n"
    message += f"{upi_link}\n\n"
    message += f"✨ This will open your UPI app (PhonePe, GPay, Paytm, etc.) to complete the payment.\n\n"
    message += f"Your order will be processed once payment is confirmed. 🙏"
    
    # Send WhatsApp message
    try:
        await send_whatsapp_message(customer_phone, message)
        logger.info(f"✅ UPI payment link sent to {customer_phone} for order {order.id}")
    except Exception as e:
        logger.error(f"❌ Failed to send UPI payment link: {e}")
        raise
     