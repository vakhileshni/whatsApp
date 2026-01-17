"""
ID Generator Utility
Generates 9-digit serial numbers for all entities
Format: "000000001", "000000002", etc. (zero-padded to 9 digits)
"""
from database import SessionLocal
from sqlalchemy import text, func
from models_db import RestaurantDB, UserDB, ProductDB, CustomerDB, OrderDB, OrderItemDB, CustomerSessionDB


def generate_next_id(table_name: str) -> str:
    """
    Generate next sequential 9-digit ID for a table
    
    Args:
        table_name: Name of the table (e.g., 'restaurants', 'users', 'products', etc.)
    
    Returns:
        str: 9-digit zero-padded ID (e.g., "000000001", "000000002")
    """
    db = SessionLocal()
    try:
        # Strategy 1: Try to find max numeric ID (for pure numeric IDs)
        result = db.execute(text(f"""
            SELECT MAX(CAST(id AS BIGINT)) 
            FROM {table_name}
            WHERE id ~ '^[0-9]+$' AND LENGTH(id) <= 9
        """))
        max_id = result.scalar()
        
        if max_id is not None:
            next_id = max_id + 1
            if next_id > 999999999:
                raise ValueError(f"Maximum ID limit reached for {table_name}")
            return str(next_id).zfill(9)
        
        # Strategy 2: Extract numeric part from existing IDs (for old format like "rest_001")
        result = db.execute(text(f"SELECT id FROM {table_name} ORDER BY id DESC LIMIT 100"))
        rows = result.fetchall()
        
        max_numeric = 0
        for row in rows:
            last_id = row[0]
            if isinstance(last_id, str):
                # Extract all numbers from the ID
                import re
                numbers = re.findall(r'\d+', last_id)
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        if num <= 999999999:  # Valid 9-digit range
                            max_numeric = max(max_numeric, num)
                    except:
                        pass
        
        # If we found numeric IDs, use them; otherwise start from 1
        next_id = max_numeric + 1 if max_numeric > 0 else 1
        
        if next_id > 999999999:
            raise ValueError(f"Maximum ID limit reached for {table_name}")
        
        return str(next_id).zfill(9)
        
    except Exception as e:
        # Ultimate fallback: start from 1
        print(f"Warning: Could not determine max ID for {table_name}: {e}. Starting from 1.")
        return "000000001"
    finally:
        db.close()


def generate_restaurant_id() -> str:
    """Generate next restaurant ID"""
    return generate_next_id('restaurants')


def generate_user_id() -> str:
    """Generate next user ID"""
    return generate_next_id('users')


def generate_product_id() -> str:
    """Generate next product ID"""
    return generate_next_id('products')


def generate_customer_id() -> str:
    """Generate next customer ID"""
    return generate_next_id('customers')


def generate_order_id() -> str:
    """Generate next order ID"""
    return generate_next_id('orders')


def generate_order_item_id() -> str:
    """Generate next order item ID"""
    return generate_next_id('order_items')


def generate_session_id() -> str:
    """Generate next session ID (using phone_number as key, so this might not be needed)"""
    # Sessions use phone_number as primary key, so this might not be used
    return generate_next_id('customer_sessions')


def generate_subscription_id() -> str:
    """Generate next subscription ID"""
    return generate_next_id('subscriptions')


def generate_payment_id() -> str:
    """Generate next payment ID"""
    return generate_next_id('payments')


def generate_rating_id() -> str:
    """Generate next rating ID (restaurant_ratings uses restaurant_id as PK, so might not be needed)"""
    # This table uses restaurant_id as primary key
    return generate_next_id('restaurant_ratings')


def generate_settings_id() -> str:
    """Generate next settings ID"""
    return generate_next_id('restaurant_settings')


def generate_notification_id() -> str:
    """Generate next notification ID"""
    return generate_next_id('restaurant_notifications')


def generate_delivery_person_id() -> str:
    """Generate next delivery person ID"""
    return generate_next_id('delivery_persons')