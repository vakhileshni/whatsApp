"""
WhatsApp Service - Send notifications via WhatsApp
"""
import os
import logging
from typing import Optional, List
from models.order import Order
from models.product import Product

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Twilio configuration (from environment variables)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

def format_phone_number(phone: str) -> str:
    """Format phone number for WhatsApp (add whatsapp: prefix)"""
    phone = phone.strip()
    if phone.startswith("whatsapp:"):
        return phone
    if not phone.startswith("+91"):
        if phone.startswith("91"):
            phone = "+" + phone
        else:
            phone = "+91" + phone
    return f"whatsapp:{phone}"

def get_status_message(order: Order, new_status: str) -> str:
    """Generate WhatsApp message based on order status"""
    order_id_short = order.id[-8:].upper()
    customer_name = order.customer_name.split()[0] if order.customer_name else "Customer"
    
    status_messages = {
        "pending": f"✅ *Order Confirmed*\nHi {customer_name}!\nOrder #{order_id_short} confirmed. Total: ₹{order.total_amount:.2f}",
        "preparing": f"👨‍🍳 *Order Being Prepared*\nHi {customer_name}!\nOrder #{order_id_short} is being prepared.",
        "ready": f"🎉 *Order Ready!*\nHi {customer_name}!\nOrder #{order_id_short} is ready!\nTotal: ₹{order.total_amount:.2f}",
        "delivered": f"✅ *Order Delivered!*\nHi {customer_name}!\nOrder #{order_id_short} delivered. Total: ₹{order.total_amount:.2f}",
        "cancelled": f"❌ *Order Cancelled*\nHi {customer_name}!\nOrder #{order_id_short} cancelled."
    }
    return status_messages.get(new_status.lower(), f"Order #{order_id_short} status updated to {new_status}.")

async def send_whatsapp_message(to_phone: str, message: str) -> bool:
    """Send WhatsApp message using Twilio"""
    try:
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_WHATSAPP_NUMBER:
            logger.warning("⚠️ Twilio credentials not configured. Message would be sent to: %s", to_phone)
            logger.info("📱 WhatsApp Message:\n%s", message)
            return False

        from twilio.rest import Client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        formatted_to = format_phone_number(to_phone)
        message_response = client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=formatted_to
        )

        logger.info("✅ WhatsApp message sent successfully. SID: %s", message_response.sid)
        return True

    except Exception as e:
        logger.error("❌ Error sending WhatsApp message: %s", str(e))
        logger.info("📱 WhatsApp Message (failed to send):\n%s", message)
        return False

def format_product_catalog(products: List[Product], restaurant_name: str) -> str:
    """Format product catalog for WhatsApp"""
    if not products:
        return f"*{restaurant_name}*\nNo products available."
    
    categories = {}
    for p in products:
        if p.is_available:
            categories.setdefault(p.category, []).append(p)
    
    message = f"🍽️ *{restaurant_name} - Menu*\n\n"
    for cat, items in categories.items():
        message += f"📋 *{cat}*\n"
        for item in items:
            message += f"• {item.name} - ₹{item.price:.2f}\n"
            if item.description:
                message += f"  _{item.description}_\n"
        message += "\n"
    
    message += "💬 Reply with product name and quantity. Example: '2 Butter Chicken'\nThank you! 🙏"
    return message
