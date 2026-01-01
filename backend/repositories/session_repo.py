"""
Session Repository - Data access layer for customer sessions
Later: Replace with SQLAlchemy queries or Redis
"""
from typing import Optional
from models.session import CustomerSession
from data.sessions_data import CUSTOMER_SESSIONS

def get_session(phone_number: str, restaurant_id: str) -> Optional[CustomerSession]:
    """
    Get customer session
    Later: SELECT * FROM sessions WHERE phone_number = ? AND restaurant_id = ?
    Or: Redis GET session:{phone}:{restaurant_id}
    """
    key = f"{phone_number}:{restaurant_id}"
    return CUSTOMER_SESSIONS.get(key)

def get_session_by_phone(phone_number: str) -> Optional[CustomerSession]:
    """
    Get customer session by phone number only (for initial lookup)
    Returns the first session found for this phone number
    """
    # Try with "none" first (for sessions before restaurant selection)
    session = get_session(phone_number, "none")
    if session:
        return session
    
    # If not found, search all sessions for this phone number
    for key, sess in CUSTOMER_SESSIONS.items():
        if sess.phone_number == phone_number:
            return sess
    
    return None

def create_session(session: CustomerSession) -> CustomerSession:
    """
    Create new customer session
    Later: INSERT INTO sessions (...) VALUES (...)
    Or: Redis SET session:{phone}:{restaurant_id} ...
    """
    # Use "none" as restaurant_id in key if restaurant_id is None
    restaurant_id_key = session.restaurant_id if session.restaurant_id else "none"
    key = f"{session.phone_number}:{restaurant_id_key}"
    CUSTOMER_SESSIONS[key] = session
    return session

def update_session(session: CustomerSession) -> CustomerSession:
    """
    Update customer session
    Later: UPDATE sessions SET ... WHERE phone_number = ? AND restaurant_id = ?
    Or: Redis SET session:{phone}:{restaurant_id} ...
    """
    # Use "none" as restaurant_id in key if restaurant_id is None
    restaurant_id_key = session.restaurant_id if session.restaurant_id else "none"
    key = f"{session.phone_number}:{restaurant_id_key}"
    
    # If restaurant_id changed, we need to delete old session and create new one
    # Search for existing session with this phone number
    for existing_key in list(CUSTOMER_SESSIONS.keys()):
        if existing_key.startswith(f"{session.phone_number}:"):
            # Found existing session, delete it if key changed
            if existing_key != key:
                del CUSTOMER_SESSIONS[existing_key]
            break
    
    CUSTOMER_SESSIONS[key] = session
    return session

def delete_session(phone_number: str, restaurant_id: str) -> bool:
    """
    Delete customer session
    Later: DELETE FROM sessions WHERE phone_number = ? AND restaurant_id = ?
    Or: Redis DEL session:{phone}:{restaurant_id}
    """
    key = f"{phone_number}:{restaurant_id}"
    if key in CUSTOMER_SESSIONS:
        del CUSTOMER_SESSIONS[key]
        return True
    return False


