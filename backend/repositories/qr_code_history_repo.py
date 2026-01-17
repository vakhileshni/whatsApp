"""
QR Code History Repository - SCD Type 2 implementation
Handles historical tracking of UPI QR code changes
"""
from typing import Optional, List
from database import SessionLocal
from models_db import RestaurantUPIQRCodeHistoryDB
from sqlalchemy import text, desc


def get_qr_code_history(restaurant_id: str, limit: int = 10) -> List[dict]:
    """
    Get QR code change history for a restaurant
    Returns list of versions ordered by version_number DESC
    """
    db = SessionLocal()
    try:
        history_records = db.query(RestaurantUPIQRCodeHistoryDB).filter(
            RestaurantUPIQRCodeHistoryDB.restaurant_id == restaurant_id
        ).order_by(desc(RestaurantUPIQRCodeHistoryDB.version_number)).limit(limit).all()
        
        return [record.to_dict() for record in history_records]
    finally:
        db.close()


def get_current_qr_code_version(restaurant_id: str) -> Optional[dict]:
    """
    Get the current (most recent) QR code version
    """
    db = SessionLocal()
    try:
        current = db.query(RestaurantUPIQRCodeHistoryDB).filter(
            RestaurantUPIQRCodeHistoryDB.restaurant_id == restaurant_id,
            RestaurantUPIQRCodeHistoryDB.is_current == True
        ).order_by(desc(RestaurantUPIQRCodeHistoryDB.version_number)).first()
        
        return current.to_dict() if current else None
    finally:
        db.close()


def get_qr_code_by_version(restaurant_id: str, version_number: int) -> Optional[dict]:
    """
    Get specific version of QR code
    """
    db = SessionLocal()
    try:
        version = db.query(RestaurantUPIQRCodeHistoryDB).filter(
            RestaurantUPIQRCodeHistoryDB.restaurant_id == restaurant_id,
            RestaurantUPIQRCodeHistoryDB.version_number == version_number
        ).first()
        
        return version.to_dict() if version else None
    finally:
        db.close()


def revert_to_version(restaurant_id: str, version_number: int) -> bool:
    """
    Revert QR code to a previous version
    Uses database function to handle SCD Type 2 properly
    """
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT revert_qr_code_to_version(:restaurant_id, :version_number)"),
            {"restaurant_id": restaurant_id, "version_number": version_number}
        )
        success = result.scalar()
        db.commit()
        return bool(success)
    except Exception as e:
        db.rollback()
        print(f"Error reverting QR code: {e}")
        return False
    finally:
        db.close()


def get_version_count(restaurant_id: str) -> int:
    """
    Get total number of versions for a restaurant
    """
    db = SessionLocal()
    try:
        count = db.query(RestaurantUPIQRCodeHistoryDB).filter(
            RestaurantUPIQRCodeHistoryDB.restaurant_id == restaurant_id
        ).count()
        return count
    finally:
        db.close()
