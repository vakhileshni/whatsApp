# Backend Architecture

## Clean Architecture Pattern

This backend follows **enterprise-grade clean architecture** with clear separation of concerns:

```
Routers → Services → Repositories → Data
```

### Directory Structure

```
backend/
├── main.py                 # FastAPI app entry point
├── auth.py                 # JWT authentication utilities
│
├── models/                 # Pure data structures (dataclasses)
│   ├── user.py
│   ├── restaurant.py
│   ├── product.py
│   ├── order.py
│   └── session.py
│
├── data/                   # Hardcoded data (acts like database tables)
│   ├── users_data.py
│   ├── restaurants_data.py
│   ├── products_data.py
│   ├── orders_data.py
│   └── sessions_data.py
│
├── repositories/           # Data access layer (IMPORTANT!)
│   ├── user_repo.py
│   ├── restaurant_repo.py
│   ├── product_repo.py
│   ├── order_repo.py
│   └── session_repo.py
│
├── services/               # Business logic layer
│   ├── auth_service.py
│   └── order_service.py
│
└── routers/                # API endpoints (FastAPI routes)
    ├── auth.py
    ├── menu.py
    ├── orders.py
    ├── dashboard.py
    └── webhook.py
```

## Flow of Data

### Example: Creating an Order

1. **Router** (`routers/orders.py`)
   - Receives HTTP request
   - Validates request data
   - Calls service

2. **Service** (`services/order_service.py`)
   - Contains business logic
   - Validates business rules
   - Calls repository

3. **Repository** (`repositories/order_repo.py`)
   - Data access logic
   - Currently: Accesses hardcoded data
   - Later: Will use SQLAlchemy/DB

4. **Data** (`data/orders_data.py`)
   - Hardcoded data storage
   - Acts like database tables
   - Later: Replaced with actual database

## Key Benefits

✅ **Separation of Concerns**
- Each layer has single responsibility
- Easy to test each layer independently

✅ **Easy Database Migration**
- Only `repositories/` change when adding DB
- All other code stays the same

✅ **Clean Code**
- Business logic separated from data access
- Models are pure data structures

✅ **Scalable**
- Add new features easily
- Add new data sources without breaking existing code

## When Adding Database

### Current (Hardcoded Data)
```python
# repositories/product_repo.py
from data.products_data import PRODUCTS

def get_product_by_id(product_id: str):
    return PRODUCTS.get(product_id)
```

### Future (SQLAlchemy)
```python
# repositories/product_repo.py
from models.product import Product
from database import Session

def get_product_by_id(product_id: str):
    db = Session()
    return db.query(Product).filter(Product.id == product_id).first()
```

**Nothing else changes!** ✅
- Routers stay the same
- Services stay the same
- Models stay the same
- Only repositories change

## Models

All models are pure dataclasses with no business logic:

- `models/user.py` - User model
- `models/restaurant.py` - Restaurant model (includes latitude/longitude)
- `models/product.py` - Product model
- `models/order.py` - Order and OrderItem models
- `models/session.py` - Customer session model

## Data

Hardcoded demo data organized like database tables:

- `data/users_data.py` - User records
- `data/restaurants_data.py` - Restaurant records
- `data/products_data.py` - Product records
- `data/orders_data.py` - Order records (starts empty)
- `data/sessions_data.py` - Session records (starts empty)

## Repositories

Data access layer - these are the only files that will change when adding a database:

- `repositories/user_repo.py` - User data access
- `repositories/restaurant_repo.py` - Restaurant data access (includes location-based queries)
- `repositories/product_repo.py` - Product data access (CRUD operations)
- `repositories/order_repo.py` - Order data access
- `repositories/session_repo.py` - Session data access

## Services

Business logic layer - these contain validation and business rules:

- `services/auth_service.py` - Authentication logic
- `services/order_service.py` - Order creation and validation logic

## Routers

API endpoints - these handle HTTP requests and responses:

- `routers/auth.py` - Authentication endpoints
- `routers/menu.py` - Menu/product endpoints
- `routers/orders.py` - Order endpoints
- `routers/dashboard.py` - Dashboard statistics
- `routers/webhook.py` - WhatsApp webhook handler

## Adding New Features

1. **Add model** → `models/new_model.py`
2. **Add data** → `data/new_model_data.py`
3. **Add repository** → `repositories/new_model_repo.py`
4. **Add service** (if needed) → `services/new_model_service.py`
5. **Add router** → `routers/new_model.py`
6. **Include router** → `main.py`

This structure ensures clean, maintainable, and scalable code! 🚀


