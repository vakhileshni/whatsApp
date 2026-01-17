"""
Delivery Person Repository - Data access layer for delivery persons
"""
from typing import Optional
from models.delivery_person import DeliveryPerson
from database import SessionLocal
from models_db import DeliveryPersonDB

def get_delivery_person_by_email(email: str) -> Optional[DeliveryPerson]:
    """Get delivery person by email from database"""
    db = SessionLocal()
    try:
        db_person = db.query(DeliveryPersonDB).filter(DeliveryPersonDB.email.ilike(email)).first()
        if db_person:
            return delivery_person_db_to_model(db_person)
        return None
    finally:
        db.close()

def get_delivery_person_by_phone(phone: str) -> Optional[DeliveryPerson]:
    """Get delivery person by phone from database"""
    db = SessionLocal()
    try:
        db_person = db.query(DeliveryPersonDB).filter(DeliveryPersonDB.phone == phone).first()
        if db_person:
            return delivery_person_db_to_model(db_person)
        return None
    finally:
        db.close()

def get_delivery_person_by_id(person_id: str) -> Optional[DeliveryPerson]:
    """Get delivery person by ID from database"""
    db = SessionLocal()
    try:
        db_person = db.query(DeliveryPersonDB).filter(DeliveryPersonDB.id == person_id).first()
        if db_person:
            return delivery_person_db_to_model(db_person)
        return None
    finally:
        db.close()

def create_delivery_person(person: DeliveryPerson) -> Optional[DeliveryPerson]:
    """Create a new delivery person in database"""
    db = SessionLocal()
    try:
        # Check if person already exists
        existing = db.query(DeliveryPersonDB).filter(
            (DeliveryPersonDB.id == person.id) | 
            (DeliveryPersonDB.email.ilike(person.email)) |
            (DeliveryPersonDB.phone == person.phone)
        ).first()
        if existing:
            return None
        
        # Create database model
        db_person = DeliveryPersonDB(
            id=person.id,
            name=person.name,
            phone=person.phone,
            email=person.email,
            password_hash=person.password_hash,
            vehicle_type=person.vehicle_type,
            license_number=person.license_number,
            is_available=person.is_available,
            current_latitude=person.current_latitude,
            current_longitude=person.current_longitude
        )
        
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        
        return delivery_person_db_to_model(db_person)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def update_delivery_person(person: DeliveryPerson) -> Optional[DeliveryPerson]:
    """Update delivery person in database"""
    db = SessionLocal()
    try:
        db_person = db.query(DeliveryPersonDB).filter(DeliveryPersonDB.id == person.id).first()
        if not db_person:
            return None
        
        db_person.name = person.name
        db_person.phone = person.phone
        db_person.email = person.email
        db_person.password_hash = person.password_hash
        db_person.vehicle_type = person.vehicle_type
        db_person.license_number = person.license_number
        db_person.is_available = person.is_available
        db_person.current_latitude = person.current_latitude
        db_person.current_longitude = person.current_longitude
        
        db.commit()
        db.refresh(db_person)
        
        return delivery_person_db_to_model(db_person)
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delivery_person_db_to_model(db_person: DeliveryPersonDB) -> DeliveryPerson:
    """Convert database model to dataclass model"""
    return DeliveryPerson(
        id=db_person.id,
        name=db_person.name,
        phone=db_person.phone,
        email=db_person.email,
        password_hash=db_person.password_hash,
        vehicle_type=db_person.vehicle_type,
        license_number=db_person.license_number,
        is_available=db_person.is_available,
        current_latitude=float(db_person.current_latitude) if db_person.current_latitude else None,
        current_longitude=float(db_person.current_longitude) if db_person.current_longitude else None
    )
