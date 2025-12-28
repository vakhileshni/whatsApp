"""
Product Repository - Data access layer for products
Later: Replace with SQLAlchemy queries
"""
from typing import List, Optional
from models.product import Product
from data.products_data import PRODUCTS

def get_product_by_id(product_id: str) -> Optional[Product]:
    """
    Get product by ID
    Later: SELECT * FROM products WHERE id = ?
    """
    return PRODUCTS.get(product_id)

def get_products_by_restaurant(restaurant_id: str) -> List[Product]:
    """
    Get all products for a restaurant
    Later: SELECT * FROM products WHERE restaurant_id = ?
    """
    return [p for p in PRODUCTS.values() if p.restaurant_id == restaurant_id]

def create_product(product: Product) -> Product:
    """
    Create a new product
    Later: INSERT INTO products (...) VALUES (...)
    """
    PRODUCTS[product.id] = product
    return product

def update_product(product: Product) -> Product:
    """
    Update a product
    Later: UPDATE products SET ... WHERE id = ?
    """
    PRODUCTS[product.id] = product
    return product

def delete_product(product_id: str) -> bool:
    """
    Delete a product
    Later: DELETE FROM products WHERE id = ?
    """
    if product_id in PRODUCTS:
        del PRODUCTS[product_id]
        return True
    return False


