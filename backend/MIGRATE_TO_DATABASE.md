# Migrate from Hardcoded Data to Database

This guide explains how to update the repositories to use PostgreSQL instead of hardcoded data.

## Current vs Future

### Current (Hardcoded)
```python
# repositories/product_repo.py
from data.products_data import PRODUCTS

def get_product_by_id(product_id: str):
    return PRODUCTS.get(product_id)
```

### Future (Database)
```python
# repositories/product_repo.py
from database import SessionLocal
from models.product import Product as ProductModel

def get_product_by_id(product_id: str):
    db = SessionLocal()
    try:
        return db.query(ProductModel).filter(ProductModel.id == product_id).first()
    finally:
        db.close()
```

## Migration Steps

### Step 1: Create SQLAlchemy Models

First, we need to create SQLAlchemy ORM models that match our database schema.

**Note**: These are different from the existing `models/` which are Pydantic/dataclasses. We'll need ORM models.

### Step 2: Update Each Repository

Each repository file needs to be updated to use SQLAlchemy instead of hardcoded data.

The good news: **All other code stays the same!**
- Routers don't change
- Services don't change  
- Only repositories change

### Step 3: Test

After updating repositories:
1. Test each API endpoint
2. Verify data is saved to database
3. Check data persists after server restart

## Files to Update

1. `repositories/user_repo.py`
2. `repositories/restaurant_repo.py`
3. `repositories/product_repo.py`
4. `repositories/customer_repo.py`
5. `repositories/order_repo.py`
6. `repositories/session_repo.py`

## Next Steps

Would you like me to:
1. Create SQLAlchemy ORM models?
2. Update all repositories to use database?
3. Create a data migration script to import existing demo data?

Let me know and I'll proceed!
