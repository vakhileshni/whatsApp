"""
Product Repository - Data access layer for products
Now using SQLAlchemy with PostgreSQL database
"""
from typing import List, Optional
from models.product import Product
from database import SessionLocal
from models_db import ProductDB
from model_converters import product_db_to_model, product_model_to_db
from id_generator import generate_product_id


def get_product_by_id(product_id: str) -> Optional[Product]:
    """
    Get product by ID from database
    """
    db = SessionLocal()
    try:
        db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if db_product:
            return product_db_to_model(db_product)
        return None
    finally:
        db.close()


def get_products_by_restaurant(restaurant_id: str) -> List[Product]:
    """
    Get all products for a restaurant from database
    """
    db = SessionLocal()
    try:
        db_products = db.query(ProductDB).filter(
            ProductDB.restaurant_id == restaurant_id
        ).all()
        return [product_db_to_model(p) for p in db_products]
    finally:
        db.close()


def create_product(product: Product) -> Product:
    """
    Create a new product in database
    Automatically generates 9-digit ID if not provided
    """
    db = SessionLocal()
    try:
        # Generate ID if not provided
        if not product.id:
            product.id = generate_product_id()
        
        # Check if product already exists
        existing = db.query(ProductDB).filter(ProductDB.id == product.id).first()
        if existing:
            # Update instead
            for key, value in product_model_to_db(product).items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return product_db_to_model(existing)
        
        # Create new product
        db_product = ProductDB(**product_model_to_db(product))
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return product_db_to_model(db_product)
    except Exception as e:
        db.rollback()
        print(f"Error creating product: {e}")
        raise
    finally:
        db.close()


def update_product(product: Product) -> Product:
    """
    Update a product in database
    """
    db = SessionLocal()
    try:
        db_product = db.query(ProductDB).filter(ProductDB.id == product.id).first()
        if not db_product:
            raise ValueError(f"Product {product.id} not found")
        
        # Update fields
        for key, value in product_model_to_db(product).items():
            setattr(db_product, key, value)
        
        db.commit()
        db.refresh(db_product)
        return product_db_to_model(db_product)
    except Exception as e:
        db.rollback()
        print(f"Error updating product: {e}")
        raise
    finally:
        db.close()


def delete_product(product_id: str) -> bool:
    """
    Delete a product from database
    """
    db = SessionLocal()
    try:
        db_product = db.query(ProductDB).filter(ProductDB.id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting product: {e}")
        return False
    finally:
        db.close()
