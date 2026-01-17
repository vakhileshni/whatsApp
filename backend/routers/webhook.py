"""
Webhook Router - API endpoints for WhatsApp webhooks
QR code contains ONLY restaurant_id (e.g., "rest_001")
Backend identifies restaurant based on first WhatsApp message
"""
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from repositories.restaurant_repo import get_restaurant_by_id, get_all_restaurants
import logging

# Import actual WhatsApp service function
from services.whatsapp_service import send_whatsapp_message

# Stub functions for session management (using session repo instead)
def is_valid_restaurant_id(restaurant_id: str) -> bool:
    """Check if restaurant_id is valid"""
    restaurant = get_restaurant_by_id(restaurant_id)
    return restaurant is not None

# Simple in-memory mapping for customer to restaurant (temporary solution)
_customer_restaurant_map = {}

def get_customer_restaurant(customer_phone: str) -> Optional[str]:
    """Get restaurant_id for a customer"""
    return _customer_restaurant_map.get(customer_phone)

def set_customer_restaurant(customer_phone: str, restaurant_id: str):
    """Map customer to restaurant"""
    _customer_restaurant_map[customer_phone] = restaurant_id

def is_customer_mapped(customer_phone: str) -> bool:
    """Check if customer is mapped to a restaurant"""
    return customer_phone in _customer_restaurant_map

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/webhook", tags=["webhook"])

class WhatsAppWebhook(BaseModel):
    From: str
    To: str
    Body: str
    MessageSid: Optional[str] = None

def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to consistent format (remove whatsapp: prefix, ensure +91)
    Returns: normalized phone number without + prefix (e.g., "919876543210")
    """
    phone = phone.replace("whatsapp:", "").replace("+", "").strip()
    # Ensure starts with 91 (India country code)
    if not phone.startswith("91"):
        phone = "91" + phone
    return phone

def format_menu_message(restaurant) -> str:
    """
    Format restaurant menu as WhatsApp message
    restaurant can be either a Restaurant model object or dict
    """
    from repositories.product_repo import get_products_by_restaurant
    
    # Get menu items for the restaurant
    menu_items = get_products_by_restaurant(restaurant.id)
    
    # Get restaurant name and UPI ID
    restaurant_name = restaurant.name if hasattr(restaurant, 'name') else restaurant.get('name', 'Restaurant')
    upi_id = restaurant.upi_id if hasattr(restaurant, 'upi_id') else restaurant.get('upi_id', '')
    
    if not menu_items:
        return f"*{restaurant_name}*\n\nSorry, no menu items available at the moment."
    
    message = f"🍽️ *{restaurant_name} - Menu*\n\n"
    message += "━━━━━━━━━━━━━━━━\n\n"
    
    for idx, item in enumerate(menu_items, 1):
        if item.is_available:
            message += f"{idx}. *{item.name}*\n"
            message += f"   {item.description}\n"
            message += f"   💰 ₹{item.price:.0f}\n\n"
    
    message += "━━━━━━━━━━━━━━━━\n"
    message += "💬 *How to Order:*\n"
    message += "Reply with the item number or name\n"
    message += "Example: '1' or 'Margherita Pizza'\n\n"
    
    # Add UPI info if available
    if upi_id:
        message += f"💳 *Payment:* Send amount to {upi_id}\n\n"
    
    message += "Thank you for choosing us! 🙏"
    
    return message

async def process_restaurant_owner_command(from_number: str, body: str) -> Optional[dict]:
    """
    Process command from restaurant owner (e.g., "ACCEPT order_123", "PREPARE order_123")
    Returns dict with status if processed, None if not a restaurant command
    """
    from repositories.restaurant_repo import get_all_restaurants
    from repositories.settings_repo import get_settings_by_restaurant_id
    from repositories.order_repo import get_order_by_id
    from services.order_service import update_order_status_safe
    from services.whatsapp_service import format_phone_number
    from repositories.notification_repo import update_notification_status, get_notification_by_order_id
    
    # Normalize sender phone
    sender_phone = format_phone_number(from_number)
    
    # Check if sender is a restaurant owner
    restaurants = get_all_restaurants()
    restaurant = None
    
    for r in restaurants:
        # Check restaurant phone
        if format_phone_number(r.phone) == sender_phone:
            restaurant = r
            break
        
        # Check settings WhatsApp number
        settings = get_settings_by_restaurant_id(r.id)
        if settings and settings.whatsapp_number:
            if format_phone_number(settings.whatsapp_number) == sender_phone:
                restaurant = r
                break
    
    if not restaurant:
        return None  # Not a restaurant owner
    
    # Parse command: "ACCEPT order_123", "PREPARE order_123", etc.
    body_upper = body.strip().upper()
    
    # Extract command and order ID
    commands = ["ACCEPT", "PREPARE", "READY", "CANCEL", "DELIVERED", "VERIFY"]
    command = None
    order_id = None
    
    for cmd in commands:
        if body_upper.startswith(cmd):
            command = cmd.lower()
            # Extract order ID (everything after command)
            parts = body.strip().split()
            if len(parts) >= 2:
                # Try to find order ID in the message
                # Could be full ID or short ID (first 8 chars)
                potential_id = parts[1]
                
                # Try to find order by short ID (first 8 chars)
                from repositories.order_repo import get_orders_by_restaurant
                orders = get_orders_by_restaurant(restaurant.id)
                for order in orders:
                    if order.id.startswith(potential_id) or order.id == potential_id:
                        order_id = order.id
                        break
            break
    
    if not command or not order_id:
        return None  # Not a valid command
    
    # Get order
    order = get_order_by_id(order_id)
    if not order:
        await send_whatsapp_message(
            from_number,
            f"❌ Order {order_id[:8]} not found."
        )
        return {"status": "error", "message": "Order not found"}
    
    # Verify order belongs to restaurant
    if order.restaurant_id != restaurant.id:
        await send_whatsapp_message(
            from_number,
            f"❌ Order {order_id[:8]} does not belong to your restaurant."
        )
        return {"status": "error", "message": "Order not authorized"}
    
    # Handle VERIFY command separately (payment verification)
    if command == "verify":
        # Verify payment for online orders
        if order.payment_method != "online":
            await send_whatsapp_message(
                from_number,
                f"❌ Order {order_id[:8]} is not an online payment order. Payment verification not applicable."
            )
            return {"status": "error", "message": "Not an online payment order"}
        
        if order.payment_status == "verified":
            await send_whatsapp_message(
                from_number,
                f"✅ Order {order_id[:8]} payment is already verified.\n\n"
                f"Payment from: {order.customer_upi_name or 'N/A'}\n"
                f"Amount: ₹{order.total_amount:.0f}"
            )
            return {"status": "success", "message": "Payment already verified"}
        
        # Verify payment (mark as verified)
        from repositories.order_repo import update_order
        order.payment_status = "verified"
        update_order(order)
        
        # Update notification record
        notification = get_notification_by_order_id(order_id)
        if notification:
            update_notification_status(
                notification.id,
                "clicked",
                button_clicked="verify"
            )
        
        # Send payment confirmation to customer
        customer_message = (
            f"✅ *Payment Verified*\n\n"
            f"Your payment of ₹{order.total_amount:.0f} for order #{order_id[:8]} has been verified by the restaurant.\n\n"
            f"Your order is now being prepared! 🍽️\n\n"
            f"Thank you for your order!"
        )
        await send_whatsapp_message(
            order.customer_phone,
            customer_message
        )
        
        # Send confirmation to restaurant owner
        payment_info = f"Payment from: {order.customer_upi_name or 'N/A'}\n" if order.customer_upi_name else ""
        await send_whatsapp_message(
            from_number,
            f"💳 *Payment Verified*\n\n"
            f"Order: #{order_id[:8]}\n"
            f"Customer: {order.customer_name}\n"
            f"{payment_info}"
            f"Amount: ₹{order.total_amount:.0f}\n\n"
            f"✅ Customer has been notified."
        )
        
        logger.info(f"✅ Restaurant owner {sender_phone} verified payment for order {order_id}")
        
        return {
            "status": "success",
            "message": "Payment verified",
            "order_id": order_id
        }
    
    # Map command to order status
    status_map = {
        "accept": "pending",  # Accepting keeps it pending (ready to prepare)
        "prepare": "preparing",
        "ready": "ready",
        "cancel": "cancelled",
        "delivered": "delivered"
    }
    
    new_status = status_map.get(command)
    if not new_status:
        return None
    
    try:
        # Update order status
        updated_order, old_status = update_order_status_safe(order_id, new_status, restaurant.id)
        
        # Update notification record
        notification = get_notification_by_order_id(order_id)
        if notification:
            update_notification_status(
                notification.id,
                "clicked",
                button_clicked=command
            )
        
        # Send confirmation to restaurant owner
        status_emoji = {
            "pending": "✅",
            "preparing": "👨‍🍳",
            "ready": "🎉",
            "cancelled": "❌",
            "delivered": "✅"
        }
        emoji = status_emoji.get(new_status, "✅")
        
        await send_whatsapp_message(
            from_number,
            f"{emoji} Order {order_id[:8]} updated to: *{new_status.upper()}*\n\n"
            f"Customer: {order.customer_name}\n"
            f"Total: ₹{order.total_amount:.0f}"
        )
        
        logger.info(f"✅ Restaurant owner {sender_phone} updated order {order_id} to {new_status}")
        
        return {
            "status": "success",
            "order_id": order_id,
            "new_status": new_status,
            "restaurant_id": restaurant.id
        }
    except Exception as e:
        logger.error(f"❌ Error processing restaurant command: {e}")
        await send_whatsapp_message(
            from_number,
            f"❌ Error updating order: {str(e)}"
        )
        return {"status": "error", "message": str(e)}


async def process_whatsapp_message(from_number: str, to_number: str, body: str):
    """
    Process WhatsApp message from customer or restaurant owner
    
    Logic:
    1. First check if it's a restaurant owner command (ACCEPT, PREPARE, etc.)
    2. If not, treat as customer message:
       - IF customer not mapped: Treat as restaurant_id (QR code scan)
       - ELSE: Treat as order/chat
    """
    try:
        # First, check if it's a restaurant owner command
        owner_result = await process_restaurant_owner_command(from_number, body)
        if owner_result:
            return owner_result
        
        # Normalize customer phone number
        customer_phone = normalize_phone_number(from_number)
        
        logger.info(f"📱 Received WhatsApp message from {customer_phone}: '{body}'")
        
        # Check if customer is already mapped to a restaurant
        if not is_customer_mapped(customer_phone):
            # Customer not mapped - treat message as restaurant_id (QR code scan)
            # Handle formats: "rest_001" or "resto_rest_001" or "resto:rest_001"
            message_body = body.strip()
            restaurant_id = None
            
            # Extract restaurant_id from various formats
            if message_body.startswith("resto_"):
                restaurant_id = message_body.replace("resto_", "").strip()
            elif message_body.startswith("resto:"):
                restaurant_id = message_body.replace("resto:", "").strip()
            else:
                # Assume it's just the restaurant_id
                restaurant_id = message_body
            
            logger.info(f"🔍 New customer detected. Message: '{message_body}' -> Extracted restaurant_id: '{restaurant_id}'")
            
            # Validate restaurant_id
            if not is_valid_restaurant_id(restaurant_id):
                logger.warning(f"⚠️ Invalid restaurant_id attempted: '{restaurant_id}'")
                await send_whatsapp_message(
                    from_number,
                    "❌ Invalid QR code. Please scan the QR code from the restaurant again."
                )
                return {
                    "status": "error",
                    "message": "Invalid restaurant_id",
                    "restaurant_id": restaurant_id
                }
            
            # Get restaurant data
            restaurant = get_restaurant_by_id(restaurant_id)
            if not restaurant:
                logger.error(f"❌ Restaurant not found in registry: {restaurant_id}")
                await send_whatsapp_message(
                    from_number,
                    "❌ Restaurant not found. Please scan the QR code again."
                )
                return {
                    "status": "error",
                    "message": "Restaurant not found",
                    "restaurant_id": restaurant_id
                }
            
            # Save customer → restaurant mapping
            set_customer_restaurant(customer_phone, restaurant_id)
            logger.info(f"✅ Restaurant identified: {restaurant.name} (ID: {restaurant_id})")
            
            # Format and send welcome message with menu
            menu_message = format_menu_message(restaurant)
            await send_whatsapp_message(from_number, menu_message)
            
            logger.info(f"✅ Menu sent to {customer_phone} for restaurant {restaurant.name}")
            
            return {
                "status": "success",
                "message": "Restaurant identified and menu sent",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.name,
                "customer_phone": customer_phone
            }
        
        else:
            # Customer is already mapped - treat message as order/chat
            restaurant_id = get_customer_restaurant(customer_phone)
            restaurant = get_restaurant_by_id(restaurant_id)
            
            if not restaurant:
                logger.error(f"❌ Restaurant not found for mapped customer: {restaurant_id}")
                await send_whatsapp_message(
                    from_number,
                    "❌ Error: Your session is invalid. Please scan the QR code again."
                )
                return {
                    "status": "error",
                    "message": "Restaurant not found for mapped customer"
                }
            
            logger.info(f"💬 Processing order/chat message for {restaurant.name} (ID: {restaurant_id})")
            
            # For now, respond with a simple acknowledgment
            # TODO: Implement order processing logic here
            body_lower = body.lower().strip()
            
            # Check if it's a greeting or menu request
            if body_lower in ["hi", "hello", "hey", "menu", "show menu"]:
                menu_message = format_menu_message(restaurant)
                await send_whatsapp_message(from_number, menu_message)
                logger.info(f"✅ Menu resent to {customer_phone}")
            else:
                # Acknowledge the message (order processing will be implemented later)
                await send_whatsapp_message(
                    from_number,
                    f"✅ Thank you for your message!\n\n"
                    f"Your order request has been received. We'll process it shortly.\n\n"
                    f"Reply 'menu' to see the menu again."
                )
                logger.info(f"ℹ️ Order/chat message received: '{body}'")
            
            return {
                "status": "success",
                "message": "Order/chat message processed",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.name,
                "customer_phone": customer_phone
            }
    
    except Exception as e:
        logger.error(f"❌ Error processing WhatsApp message: {str(e)}", exc_info=True)
        # Always return 200 to prevent Twilio retries
        return {
            "status": "error",
            "message": f"Error processing message: {str(e)}"
        }

@router.post("/whatsapp")
async def whatsapp_webhook_form(
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: Optional[str] = Form(None)
):
    """
    WhatsApp webhook handler (Twilio form-encoded format)
    Always returns 200 status to prevent Twilio retries
    """
    try:
        # Extract phone numbers
        from_number = From.strip()
        to_number = To.strip()
        body = Body.strip()
        
        logger.info(f"📥 Webhook received: From={from_number}, To={to_number}, Body='{body}'")
        
        result = await process_whatsapp_message(from_number, to_number, body)
        
        # Always return 200 status
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in webhook handler: {str(e)}", exc_info=True)
        # Always return 200 to prevent Twilio retries
        return {
            "status": "error",
            "message": f"Error processing webhook: {str(e)}"
        }

@router.post("/whatsapp/json")
async def whatsapp_webhook_json(webhook_data: WhatsAppWebhook):
    """
    WhatsApp webhook handler (JSON format)
    Always returns 200 status to prevent Twilio retries
    """
    try:
        # Extract phone numbers
        from_number = webhook_data.From.strip()
        to_number = webhook_data.To.strip()
        body = webhook_data.Body.strip()
        
        logger.info(f"📥 Webhook received (JSON): From={from_number}, To={to_number}, Body='{body}'")
        
        result = await process_whatsapp_message(from_number, to_number, body)
        
        # Always return 200 status
        return result
        
    except Exception as e:
        logger.error(f"❌ Error in webhook handler: {str(e)}", exc_info=True)
        # Always return 200 to prevent Twilio retries
        return {
            "status": "error",
            "message": f"Error processing webhook: {str(e)}"
        }
