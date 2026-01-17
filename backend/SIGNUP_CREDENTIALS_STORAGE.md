# Signup Credentials Storage

## Overview
When a new restaurant signs up, credentials (email and password) are stored in the **`users` table** in the PostgreSQL database.

## Database Table: `users`

### Table Structure
```sql
CREATE TABLE users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    restaurant_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    CONSTRAINT fk_users_restaurant FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(id) ON DELETE CASCADE
);
```

### Fields Storing Credentials

1. **`email`** (VARCHAR(255), UNIQUE, NOT NULL)
   - Stores the user's email address
   - Used for login authentication
   - Must be unique (one email per account)

2. **`password`** (VARCHAR(255), NOT NULL)
   - Stores the user's password
   - **⚠️ Currently stored as plain text** (should be hashed in production)
   - Used for login authentication

### Additional Fields

- **`id`** - Primary key (auto-generated 9-digit ID)
- **`restaurant_id`** - Foreign key linking to the `restaurants` table
- **`name`** - Owner/User's name
- **`created_at`** - Account creation timestamp
- **`updated_at`** - Last update timestamp
- **`is_active`** - Account status (active/inactive)
- **`last_login`** - Last login timestamp

## Signup Flow

When a user signs up via `/api/v1/auth/signup`:

1. **Creates Restaurant** (stored in `restaurants` table)
   - Restaurant ID, name, phone, address, location, etc.

2. **Creates User** (stored in `users` table)
   - User ID, email, password, restaurant_id, name

### Code Location
- **Signup Endpoint**: `backend/routers/auth.py` → `signup()` function
- **User Creation**: `backend/repositories/user_repo.py` → `create_user()` function
- **Database Model**: `backend/models_db.py` → `UserDB` class

## Query Examples

### View all users and their credentials:
```sql
SELECT id, email, password, restaurant_id, name, created_at, is_active 
FROM users;
```

### Find user by email:
```sql
SELECT * FROM users WHERE email = 'admin@restaurant.com';
```

### Find all users for a restaurant:
```sql
SELECT * FROM users WHERE restaurant_id = '000000001';
```

## Security Note

⚠️ **Important**: Passwords are currently stored as **plain text** in the database. 

For production, you should:
1. Hash passwords using bcrypt or similar
2. Never store plain text passwords
3. Use secure password validation
4. Implement password reset functionality

## Related Tables

- **`restaurants`** - Stores restaurant information (linked via `restaurant_id`)
- Other tables (orders, products, customers) reference restaurants, not users directly
