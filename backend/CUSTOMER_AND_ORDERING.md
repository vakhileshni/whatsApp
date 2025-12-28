# Customer and Location-Based Ordering

## Customer Data Structure

### Customer Model (`models/customer.py`)
```python
@dataclass
class Customer:
    id: str
    restaurant_id: str
    phone: str
    latitude: float  # For location-based routing
    longitude: float  # For location-based routing
```

### Sample Customer Data (`data/customers_data.py`)

| ID | Restaurant ID | Phone | Latitude | Longitude |
|----|--------------|-------|----------|-----------|
| 1 | rest_001 | 9876543210 | 19.0760 | 72.8777 |
| 2 | rest_002 | 9123456780 | 28.6139 | 77.2090 |
| 3 | rest_001 | 9988776655 | 19.0759 | 72.8776 |

## Order Data Structure

### Order Model (`models/order.py`)
```python
@dataclass
class Order:
    id: str
    restaurant_id: str
    customer_id: str  # Links to customer
    customer_phone: str
    customer_name: str
    items: List[OrderItem]
    order_type: str  # "Delivery" or "Pickup"
    delivery_fee: float
    total_amount: float
    status: str  # "PREPARING", "READY", "DELIVERED", etc.
    created_at: str
    updated_at: str
    delivery_address: Optional[str]
```

### Sample Order Data (`data/orders_data.py`)

**Order 1:**
- ID: 1
- Restaurant: rest_001
- Customer ID: 1
- Status: PREPARING
- Type: Delivery
- Delivery Fee: ₹40
- Total: ₹290
- Created: 2025-12-27 12:30

**Order 2:**
- ID: 2
- Restaurant: rest_002
- Customer ID: 2
- Status: READY
- Type: Pickup
- Delivery Fee: ₹0
- Total: ₹150
- Created: 2025-12-27 12:45

## Location-Based Restaurant Routing

### How It Works

When a customer places an order, the system automatically determines the nearest restaurant using:

1. **Haversine Formula**: Calculates distance between customer location and restaurant locations
2. **Nearest Restaurant**: Routes order to closest active restaurant
3. **Fallback Logic**: If location not provided, uses existing customer's restaurant or first available restaurant

### Implementation

**Repository Function** (`repositories/customer_repo.py`):
```python
def find_nearest_restaurant(customer_latitude: float, customer_longitude: float):
    """
    Find nearest restaurant based on customer location
    Uses Haversine formula to calculate distance
    """
    # Calculates distance for each restaurant
    # Returns nearest active restaurant
```

**Order Creation Flow** (`routers/orders.py`):
1. **If location provided** → Find nearest restaurant
2. **If customer exists** → Use their existing restaurant
3. **Fallback** → Use first available restaurant

### Example Usage

```python
# Create order with location
POST /api/v1/orders
{
    "customer_phone": "9876543210",
    "customer_name": "John Doe",
    "customer_latitude": 19.0760,  # Mumbai
    "customer_longitude": 72.8777,
    "items": [...],
    "order_type": "Delivery"
}

# System automatically routes to nearest restaurant (Spice Garden in Mumbai)
```

## Customer Repository Functions

- `get_customer_by_id(customer_id)` - Get customer by ID
- `get_customer_by_phone(phone)` - Get customer by phone number
- `get_customers_by_restaurant(restaurant_id)` - Get all customers for a restaurant
- `create_customer(customer)` - Create new customer
- `find_nearest_restaurant(latitude, longitude)` - Find nearest restaurant (location-based routing)

## Database Schema (Future)

When migrating to database, tables will look like:

**customers table:**
```sql
CREATE TABLE customers (
    id VARCHAR PRIMARY KEY,
    restaurant_id VARCHAR,
    phone VARCHAR UNIQUE,
    latitude FLOAT,
    longitude FLOAT
);
```

**orders table:**
```sql
CREATE TABLE orders (
    id VARCHAR PRIMARY KEY,
    restaurant_id VARCHAR,
    customer_id VARCHAR REFERENCES customers(id),
    customer_phone VARCHAR,
    customer_name VARCHAR,
    delivery_type VARCHAR,  -- "Delivery" or "Pickup"
    delivery_fee FLOAT,
    total_amount FLOAT,
    status VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    delivery_address TEXT
);
```

## Benefits

✅ **Automatic Routing**: Orders automatically go to nearest restaurant  
✅ **Location-Based**: Uses customer GPS coordinates  
✅ **Multi-Tenant**: Each customer linked to specific restaurant  
✅ **Scalable**: Easy to add more restaurants  
✅ **Smart Fallback**: Handles cases where location unavailable  


