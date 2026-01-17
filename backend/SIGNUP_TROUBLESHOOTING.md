# Signup Troubleshooting Guide

## Issue: Users table is blank after signup

If you've created signups but the `users` table is empty, here's how to troubleshoot:

### Step 1: Check if Database Connection is Working

```python
from database import check_db_connection
print(check_db_connection())  # Should return True
```

### Step 2: Verify Database Tables Exist

```sql
-- Connect to PostgreSQL and check tables
\dt  -- List all tables
SELECT * FROM users;  -- Check users table
SELECT * FROM restaurants;  -- Check restaurants table
```

### Step 3: Check Backend Logs

When you create a signup, check the backend console/terminal for any error messages. Look for:
- Database connection errors
- Foreign key constraint violations
- Transaction rollback messages

### Step 4: Test User Creation Directly

Run this Python script to test user creation:

```python
from repositories.user_repo import create_user
from repositories.restaurant_repo import create_restaurant
from models.user import User
from models.restaurant import Restaurant
from id_generator import generate_restaurant_id, generate_user_id
from database import SessionLocal
from models_db import UserDB

# Create restaurant first
restaurant_id = generate_restaurant_id()
restaurant = Restaurant(
    id=restaurant_id,
    name="Test Restaurant",
    phone="+919876543210",
    address="Test Address",
    latitude=26.8527,
    longitude=80.9495,
    delivery_fee=40.0,
    is_active=True,
    upi_id="",
    cuisine_type="both"
)
created_restaurant = create_restaurant(restaurant)

# Create user
user_id = generate_user_id()
user = User(
    id=user_id,
    email="test@example.com",
    password="test123",
    restaurant_id=restaurant_id,
    name="Test User"
)
created_user = create_user(user)

# Verify in database
db = SessionLocal()
users = db.query(UserDB).filter(UserDB.email == "test@example.com").all()
print(f"Users found: {len(users)}")
db.close()
```

### Common Issues

1. **Foreign Key Constraint**: User creation fails if the restaurant_id doesn't exist in the restaurants table
2. **Database Connection**: Database might not be running or connection string is incorrect
3. **Transaction Rollback**: If an error occurs, the transaction is rolled back
4. **Different Database**: Application might be connecting to a different database than you're checking

### Quick Check Commands

```sql
-- Check users table
SELECT COUNT(*) FROM users;
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;

-- Check restaurants table
SELECT COUNT(*) FROM restaurants;
SELECT id, name FROM restaurants ORDER BY created_at DESC LIMIT 10;

-- Check for recent signups
SELECT u.*, r.name as restaurant_name 
FROM users u 
JOIN restaurants r ON u.restaurant_id = r.id 
ORDER BY u.created_at DESC;
```

### Solution

If users are not being saved:

1. **Check backend logs** for errors during signup
2. **Verify database is running**: `docker ps` (if using Docker) or check PostgreSQL service
3. **Check DATABASE_URL**: Ensure it points to the correct database
4. **Verify tables exist**: Run `init-db.sql` if tables don't exist
5. **Check foreign key constraints**: Ensure restaurant is created before user
