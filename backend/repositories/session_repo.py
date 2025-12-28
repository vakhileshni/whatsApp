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

def create_session(session: CustomerSession) -> CustomerSession:
    """
    Create new customer session
    Later: INSERT INTO sessions (...) VALUES (...)
    Or: Redis SET session:{phone}:{restaurant_id} ...
    """
    key = f"{session.phone_number}:{session.restaurant_id}"
    CUSTOMER_SESSIONS[key] = session
    return session

def update_session(session: CustomerSession) -> CustomerSession:
    """
    Update customer session
    Later: UPDATE sessions SET ... WHERE phone_number = ? AND restaurant_id = ?
    Or: Redis SET session:{phone}:{restaurant_id} ...
    """
    key = f"{session.phone_number}:{session.restaurant_id}"
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


