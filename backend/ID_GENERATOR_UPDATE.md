# ID Generator Update - 9-Digit Serial Numbers

## Overview
All entity IDs have been updated to use **9-digit serial numbers** instead of UUID-based IDs like `rest_9cebbfb2`. IDs are now auto-generated sequentially: `000000001`, `000000002`, etc.

## Changes Made

### 1. Created ID Generator Utility (`backend/id_generator.py`)
- Generates sequential 9-digit IDs (zero-padded)
- Automatically finds the max ID in each table
- Supports migration from old ID formats (e.g., `rest_001` → `000000001`)
- Functions for each entity type:
  - `generate_restaurant_id()` → `"000000001"`
  - `generate_user_id()` → `"000000002"`
  - `generate_product_id()` → `"000000003"`
  - `generate_customer_id()` → `"000000004"`
  - `generate_order_id()` → `"000000005"`
  - `generate_order_item_id()` → `"000000006"`
  - And more...

### 2. Updated All Repository Create Functions
All repositories now automatically generate IDs if not provided:

- ✅ `backend/repositories/restaurant_repo.py` - Auto-generates restaurant IDs
- ✅ `backend/repositories/user_repo.py` - Auto-generates user IDs
- ✅ `backend/repositories/product_repo.py` - Auto-generates product IDs
- ✅ `backend/repositories/customer_repo.py` - Auto-generates customer IDs
- ✅ `backend/repositories/order_repo.py` - Auto-generates order and order item IDs

### 3. Updated All Routers
- ✅ `backend/routers/auth.py` - Uses ID generator for signup
- ✅ `backend/routers/menu.py` - Uses ID generator for products
- ✅ `backend/routers/orders.py` - Uses ID generator for orders and customers
- ✅ `backend/services/order_service.py` - Uses ID generator for orders
- ✅ `backend/main.py` - Updated customer ID generation

### 4. Updated Model Converters
- ✅ `backend/model_converters.py` - Order items now auto-generate IDs

## ID Format

**Before:**
- Restaurant: `rest_9cebbfb2`
- User: `user_abc12345`
- Product: `prod_xyz789`
- Order: `order_def456`

**After:**
- Restaurant: `000000001`
- User: `000000002`
- Product: `000000003`
- Order: `000000004`

## How It Works

1. When creating a new entity, the ID generator:
   - Queries the database for the maximum numeric ID
   - Extracts numeric parts from old-format IDs if needed
   - Increments by 1
   - Returns zero-padded 9-digit string

2. Example flow:
   ```python
   from id_generator import generate_restaurant_id
   
   restaurant_id = generate_restaurant_id()  # Returns "000000001"
   restaurant = Restaurant(id=restaurant_id, ...)
   ```

3. Repositories automatically generate IDs if not provided:
   ```python
   # This will auto-generate an ID
   restaurant = Restaurant(id="", name="My Restaurant", ...)
   created = create_restaurant(restaurant)  # ID auto-generated!
   ```

## Migration Notes

- **Existing data**: The ID generator handles old format IDs by extracting numeric parts
- **New data**: All new entities get 9-digit serial numbers
- **Database schema**: No changes needed - IDs remain VARCHAR(50) and can store both formats
- **Backward compatibility**: Old IDs still work, but new ones are 9-digit format

## Testing

To test the ID generator:
```bash
cd backend
python -c "from id_generator import generate_restaurant_id; print(generate_restaurant_id())"
```

Expected output: `000000001` (or next sequential number)

## Limits

- Maximum ID: `999999999` (999 million entities per table)
- If limit reached, an error will be raised

## Files Modified

1. `backend/id_generator.py` (NEW)
2. `backend/repositories/restaurant_repo.py`
3. `backend/repositories/user_repo.py`
4. `backend/repositories/product_repo.py`
5. `backend/repositories/customer_repo.py`
6. `backend/repositories/order_repo.py`
7. `backend/services/order_service.py`
8. `backend/routers/auth.py`
9. `backend/routers/menu.py`
10. `backend/routers/orders.py`
11. `backend/main.py`
12. `backend/model_converters.py`

## Next Steps

- All new entities will automatically get 9-digit IDs
- Existing entities with old format IDs will continue to work
- You can optionally migrate old IDs to new format if needed
