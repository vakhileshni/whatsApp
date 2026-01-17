"""
Database Connection Module
Uses SQLAlchemy for PostgreSQL database connectivity
"""
import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool

# Database configuration from environment variables or defaults
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://whatsapp_user:whatsapp_pass@localhost:5432/whatsapp_db"
)

# Create SQLAlchemy engine
# Using NullPool for single-threaded applications (can change to QueuePool for multi-threaded)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,  # Set to True for SQL query logging (useful for debugging)
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc"
    }
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Session:
    """
    Dependency function for FastAPI to get database session
    Usage: db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database by creating all tables
    Call this once when application starts
    """
    # Import all models here so they're registered with Base
    from models_db import (
        RestaurantDB, UserDB, ProductDB, CustomerDB, 
        OrderDB, OrderItemDB, CustomerSessionDB, 
        SubscriptionDB, PaymentDB, RestaurantRatingDB,
        RestaurantUPIQRCodeHistoryDB, RestaurantSettingsDB,
        RestaurantNotificationDB, DeliveryPersonDB
    )
    
    # Create all tables (if they don't exist)
    # Note: Tables are already created by init-db.sql, but this ensures they exist
    Base.metadata.create_all(bind=engine)


def check_db_connection():
    """
    Check if database connection is working
    Returns True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False





