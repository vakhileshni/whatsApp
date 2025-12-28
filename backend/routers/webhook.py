"""
Webhook Router - API endpoints for WhatsApp webhooks
QR code contains ONLY restaurant_id (e.g., "rest_001")
Backend identifies restaurant based on first WhatsApp message
"""
from fastapi import APIRouter, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
from services.whatsapp_service import send_whatsapp_message
from data.restaurants import get_restaurant_by_id, is_valid_restaurant_id
from services.session_manager import (
    get_customer_restaurant,
    set_customer_restaurant,
    is_customer_mapped
)
import logging

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

def format_menu_message(restaurant: dict) -> str:
    """
    Format restaurant menu as WhatsApp message
    """
    menu_items = restaurant.get("menu", [])
    if not menu_items:
        return f"*{restaurant['name']}*\n\nSorry, no menu items available at the moment."
    
    message = f"🍽️ *{restaurant['name']} - Menu*\n\n"
    message += "━━━━━━━━━━━━━━━━\n\n"
    
    for item in menu_items:
        message += f"• *{item['name']}*\n"
        message += f"  💰 ₹{item['price']}\n\n"
    
    message += "━━━━━━━━━━━━━━━━\n"
    message += "💬 *How to Order:*\n"
    message += "Reply with the item number or name\n"
    message += "Example: '1' or 'Margherita Pizza'\n\n"
    
    # Add UPI info if available
    if restaurant.get("upi_id"):
        message += f"💳 *Payment:* Send amount to {restaurant['upi_id']}\n\n"
    
    message += "Thank you for choosing us! 🙏"
    
    return message

async def process_whatsapp_message(from_number: str, to_number: str, body: str):
    """
    Process WhatsApp message from customer
    
    Logic:
    1. Normalize customer phone number
    2. IF customer not mapped:
       - Treat message body as restaurant_id (QR code scan)
       - Validate restaurant_id
       - Save customer → restaurant mapping
       - Send welcome message + menu
    3. ELSE (customer is mapped):
       - Get restaurant from session
       - Treat message as order/chat
       - Process order or respond accordingly
    """
    try:
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
            logger.info(f"✅ Restaurant identified: {restaurant['name']} (ID: {restaurant_id})")
            
            # Format and send welcome message with menu
            menu_message = format_menu_message(restaurant)
            await send_whatsapp_message(from_number, menu_message)
            
            logger.info(f"✅ Menu sent to {customer_phone} for restaurant {restaurant['name']}")
            
            return {
                "status": "success",
                "message": "Restaurant identified and menu sent",
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant["name"],
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
            
            logger.info(f"💬 Processing order/chat message for {restaurant['name']} (ID: {restaurant_id})")
            
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
                "restaurant_name": restaurant["name"],
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
