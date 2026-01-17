"""
Session Repository - Data access layer for customer sessions
Now using SQLAlchemy with PostgreSQL database
"""
from typing import Optional
from models.session import CustomerSession
from database import SessionLocal
from models_db import CustomerSessionDB
from model_converters import session_db_to_model, session_model_to_db


def get_session(phone_number: str, restaurant_id: str) -> Optional[CustomerSession]:
    """
    Get customer session from database
    """
    db = SessionLocal()
    try:
        # Use None handling for restaurant_id
        if restaurant_id and restaurant_id != "none":
            db_session = db.query(CustomerSessionDB).filter(
                CustomerSessionDB.phone_number == phone_number,
                CustomerSessionDB.restaurant_id == restaurant_id
            ).first()
        else:
            db_session = db.query(CustomerSessionDB).filter(
                CustomerSessionDB.phone_number == phone_number,
                CustomerSessionDB.restaurant_id.is_(None)
            ).first()
        
        if db_session:
            return session_db_to_model(db_session)
        return None
    finally:
        db.close()


def get_session_by_phone(phone_number: str) -> Optional[CustomerSession]:
    """
    Get customer session by phone number only (for initial lookup)
    Returns the first session found for this phone number
    """
    db = SessionLocal()
    try:
        # Try with None restaurant_id first (for sessions before restaurant selection)
        db_session = db.query(CustomerSessionDB).filter(
            CustomerSessionDB.phone_number == phone_number,
            CustomerSessionDB.restaurant_id.is_(None)
        ).first()
        
        if db_session:
            return session_db_to_model(db_session)
        
        # If not found, get any session for this phone number
        db_session = db.query(CustomerSessionDB).filter(
            CustomerSessionDB.phone_number == phone_number
        ).first()
        
        if db_session:
            return session_db_to_model(db_session)
        
        return None
    finally:
        db.close()


def create_session(session: CustomerSession) -> CustomerSession:
    """
    Create new customer session in database
    """
    db = SessionLocal()
    try:
        # Check if session already exists
        existing = db.query(CustomerSessionDB).filter(
            CustomerSessionDB.phone_number == session.phone_number
        ).first()
        
        if existing:
            # Update existing session
            for key, value in session_model_to_db(session).items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return session_db_to_model(existing)
        
        # Create new session
        db_session = CustomerSessionDB(**session_model_to_db(session))
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return session_db_to_model(db_session)
    except Exception as e:
        db.rollback()
        print(f"Error creating session: {e}")
        raise
    finally:
        db.close()


def update_session(session: CustomerSession) -> CustomerSession:
    """
    Update customer session in database
    """
    db = SessionLocal()
    try:
        db_session = db.query(CustomerSessionDB).filter(
            CustomerSessionDB.phone_number == session.phone_number
        ).first()
        
        if not db_session:
            # Create if doesn't exist
            return create_session(session)
        
        # Update fields
        for key, value in session_model_to_db(session).items():
            setattr(db_session, key, value)
        
        db.commit()
        db.refresh(db_session)
        return session_db_to_model(db_session)
    except Exception as e:
        db.rollback()
        print(f"Error updating session: {e}")
        raise
    finally:
        db.close()


def delete_session(phone_number: str, restaurant_id: str) -> bool:
    """
    Delete customer session from database
    """
    db = SessionLocal()
    try:
        if restaurant_id and restaurant_id != "none":
            db_session = db.query(CustomerSessionDB).filter(
                CustomerSessionDB.phone_number == phone_number,
                CustomerSessionDB.restaurant_id == restaurant_id
            ).first()
        else:
            db_session = db.query(CustomerSessionDB).filter(
                CustomerSessionDB.phone_number == phone_number,
                CustomerSessionDB.restaurant_id.is_(None)
            ).first()
        
        if db_session:
            db.delete(db_session)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting session: {e}")
        return False
    finally:
        db.close()
