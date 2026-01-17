"""
Payment Service - Razorpay Integration for Automatic Payment Verification
"""
import logging
import os
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# Try to import razorpay - make it optional
try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    razorpay = None
    RAZORPAY_AVAILABLE = False
    logger.warning("⚠️ Razorpay package not installed. Install with: pip install razorpay")

# Razorpay credentials from environment
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# Initialize Razorpay client
razorpay_client = None
if RAZORPAY_AVAILABLE and RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    try:
        razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        logger.info("✅ Razorpay client initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Razorpay client: {e}")
        razorpay_client = None
elif not RAZORPAY_AVAILABLE:
    logger.warning("⚠️ Razorpay package not installed. Payment gateway features will be disabled.")
elif not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
    logger.warning("⚠️ Razorpay credentials not configured. Payment gateway features will be disabled.")


def create_razorpay_payment_link(
    order_id: str,
    amount: float,
    customer_name: str,
    customer_phone: str,
    customer_email: Optional[str] = None,
    description: Optional[str] = None
) -> Optional[Dict]:
    """
    Create a Razorpay payment link for an order
    
    Args:
        order_id: Order ID
        amount: Payment amount in INR
        customer_name: Customer name
        customer_phone: Customer phone number
        customer_email: Customer email (optional)
        description: Payment description (optional)
    
    Returns:
        Payment link data with 'short_url' and 'id', or None if failed
    """
    if not razorpay_client:
        logger.error("Razorpay client not initialized. Cannot create payment link.")
        return None
    
    try:
        # Convert amount to paise (Razorpay uses paise, not rupees)
        amount_paise = int(amount * 100)
        
        # Create payment link
        payment_link_data = {
            "amount": amount_paise,
            "currency": "INR",
            "accept_partial": False,
            "first_min_partial_amount": amount_paise,
            "description": description or f"Payment for order {order_id}",
            "customer": {
                "name": customer_name,
                "contact": customer_phone,
            },
            "notify": {
                "sms": True,
                "email": False
            },
            "reminder_enable": True,
            "notes": {
                "order_id": order_id,
                "payment_type": "online"
            },
            "callback_url": os.getenv("FRONTEND_URL", "http://localhost:3000") + f"/payment?order_id={order_id}",
            "callback_method": "get"
        }
        
        if customer_email:
            payment_link_data["customer"]["email"] = customer_email
        
        logger.info(f"Creating Razorpay payment link for order {order_id}, amount: ₹{amount}")
        payment_link = razorpay_client.payment_link.create(data=payment_link_data)
        
        logger.info(f"✅ Razorpay payment link created: {payment_link.get('short_url')}")
        return payment_link
        
    except Exception as e:
        logger.error(f"❌ Failed to create Razorpay payment link: {e}", exc_info=True)
        return None


def verify_razorpay_webhook_signature(webhook_body: str, signature: str) -> bool:
    """
    Verify Razorpay webhook signature for security
    
    Args:
        webhook_body: Raw webhook request body
        signature: X-Razorpay-Signature header value
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not RAZORPAY_AVAILABLE or not razorpay_client:
        logger.warning("Razorpay not available. Skipping signature verification.")
        return True  # Allow in development, but warn
    
    if not RAZORPAY_WEBHOOK_SECRET:
        logger.warning("Razorpay webhook secret not configured. Skipping signature verification.")
        return True  # Allow in development, but warn
    
    try:
        razorpay_client.utility.verify_webhook_signature(webhook_body, signature, RAZORPAY_WEBHOOK_SECRET)
        return True
    except Exception as e:
        logger.error(f"❌ Webhook signature verification failed: {e}")
        return False


def get_payment_status(payment_link_id: str) -> Optional[Dict]:
    """
    Get payment status from Razorpay
    
    Args:
        payment_link_id: Razorpay payment link ID
    
    Returns:
        Payment link status data or None if failed
    """
    if not RAZORPAY_AVAILABLE or not razorpay_client:
        logger.warning("Razorpay not available. Cannot fetch payment status.")
        return None
    
    try:
        payment_link = razorpay_client.payment_link.fetch(payment_link_id)
        return payment_link
    except Exception as e:
        logger.error(f"❌ Failed to fetch payment status: {e}")
        return None
