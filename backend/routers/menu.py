"""
Menu Router - API endpoints for menu/products
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid
from services.auth_service import get_user_restaurant
from repositories.product_repo import (
    get_products_by_restaurant,
    get_product_by_id,
    create_product as repo_create_product,
    update_product as repo_update_product,
    delete_product as repo_delete_product
)
from models.product import Product
import auth

router = APIRouter(prefix="/api/v1/menu", tags=["menu"])

class ProductResponse(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: str
    price: float
    category: str
    is_available: bool

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    is_available: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None

def product_to_response(product: Product) -> ProductResponse:
    """Convert Product model to ProductResponse"""
    return ProductResponse(
        id=product.id,
        restaurant_id=product.restaurant_id,
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        is_available=product.is_available
    )

@router.get("", response_model=List[ProductResponse])
async def get_menu(restaurant_id: str = Depends(auth.get_current_restaurant_id)):
    """Get all menu items for current restaurant"""
    products = get_products_by_restaurant(restaurant_id)
    return [product_to_response(p) for p in products]

@router.post("", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Create a new menu item"""
    product_id = f"prod_{uuid.uuid4().hex[:8]}"
    new_product = Product(
        id=product_id,
        restaurant_id=restaurant_id,
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category=product_data.category,
        is_available=product_data.is_available
    )
    
    created_product = repo_create_product(new_product)
    return product_to_response(created_product)

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Update a menu item"""
    product = get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")
    
    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.price is not None:
        product.price = product_data.price
    if product_data.category is not None:
        product.category = product_data.category
    if product_data.is_available is not None:
        product.is_available = product_data.is_available
    
    updated_product = repo_update_product(product)
    return product_to_response(updated_product)

@router.delete("/{product_id}")
async def delete_product(
    product_id: str,
    restaurant_id: str = Depends(auth.get_current_restaurant_id)
):
    """Delete a menu item"""
    product = get_product_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.restaurant_id != restaurant_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    
    repo_delete_product(product_id)
    return {"message": "Product deleted successfully"}


