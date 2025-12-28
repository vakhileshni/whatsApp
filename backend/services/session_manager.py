"""
Session Manager - In-memory customer → restaurant mapping
Maintains customer phone to restaurant_id mapping
"""
import logging

logger = logging.getLogger(__name__)

# In-memory session map: customer_phone -> restaurant_id
customer_sessions = {}

def get_customer_restaurant(customer_phone: str):
    """
    Get restaurant_id for a customer
    Returns restaurant_id if customer is mapped, None otherwise
    """
    return customer_sessions.get(customer_phone)

def set_customer_restaurant(customer_phone: str, restaurant_id: str):
    """
    Map customer phone to restaurant_id
    Logs the session creation
    """
    customer_sessions[customer_phone] = restaurant_id
    logger.info(f"✅ Customer session created: {customer_phone} -> {restaurant_id}")
    return True

def is_customer_mapped(customer_phone: str) -> bool:
    """
    Check if customer is already mapped to a restaurant
    """
    return customer_phone in customer_sessions

def clear_customer_session(customer_phone: str):
    """
    Clear customer session (for testing or logout)
    """
    if customer_phone in customer_sessions:
        del customer_sessions[customer_phone]
        logger.info(f"🗑️ Customer session cleared: {customer_phone}")

def get_all_sessions():
    """
    Get all active sessions (for debugging)
    """
    return customer_sessions.copy()





