"""
Database Query Examples
How to write queries and fetch data from PostgreSQL database
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://whatsapp_user:whatsapp_pass@localhost:5432/whatsapp_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# ============================================================
# METHOD 1: Using Raw SQL Queries (text())
# ============================================================

def query_with_raw_sql():
    """Example: Using raw SQL queries"""
    db = SessionLocal()
    try:
        # Example 1: Select all restaurants
        result = db.execute(text("SELECT * FROM restaurants"))
        restaurants = result.fetchall()
        print("All Restaurants:")
        for row in restaurants:
            print(f"  ID: {row[0]}, Name: {row[1]}, Phone: {row[2]}")
        
        # Example 2: Select with WHERE clause
        result = db.execute(
            text("SELECT * FROM restaurants WHERE is_active = :active"),
            {"active": True}
        )
        active_restaurants = result.fetchall()
        print("\nActive Restaurants:")
        for row in active_restaurants:
            print(f"  {row[1]}")
        
        # Example 3: Select specific columns
        result = db.execute(
            text("SELECT id, name, phone, delivery_fee FROM restaurants")
        )
        restaurants = result.fetchall()
        print("\nRestaurant Summary:")
        for row in restaurants:
            print(f"  {row[1]} - Phone: {row[2]}, Fee: {row[3]}")
        
        # Example 4: COUNT query
        result = db.execute(text("SELECT COUNT(*) FROM restaurants"))
        count = result.scalar()
        print(f"\nTotal Restaurants: {count}")
        
        # Example 5: JOIN query
        result = db.execute(text("""
            SELECT 
                r.name as restaurant_name,
                p.name as product_name,
                p.price
            FROM restaurants r
            JOIN products p ON r.id = p.restaurant_id
            WHERE r.is_active = true
            ORDER BY r.name, p.name
        """))
        products = result.fetchall()
        print("\nProducts by Restaurant:")
        for row in products:
            print(f"  {row[0]} - {row[1]}: ₹{row[2]}")
        
        # Example 6: ORDER BY and LIMIT
        result = db.execute(text("""
            SELECT name, created_at 
            FROM restaurants 
            ORDER BY created_at DESC 
            LIMIT 5
        """))
        recent = result.fetchall()
        print("\nRecent Restaurants:")
        for row in recent:
            print(f"  {row[0]} - Created: {row[1]}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# ============================================================
# METHOD 2: Using Parameterized Queries (Safe from SQL Injection)
# ============================================================

def query_with_parameters():
    """Example: Using parameterized queries for safety"""
    db = SessionLocal()
    try:
        # Example 1: Find restaurant by ID
        restaurant_id = "rest1"
        result = db.execute(
            text("SELECT * FROM restaurants WHERE id = :id"),
            {"id": restaurant_id}
        )
        restaurant = result.fetchone()
        if restaurant:
            print(f"Found Restaurant: {restaurant[1]}")
        
        # Example 2: Search by name pattern
        search_term = "%Pizza%"
        result = db.execute(
            text("SELECT * FROM products WHERE name LIKE :pattern"),
            {"pattern": search_term}
        )
        products = result.fetchall()
        print(f"\nProducts matching '{search_term}': {len(products)}")
        
        # Example 3: Date range query
        result = db.execute(text("""
            SELECT * FROM orders 
            WHERE created_at >= :start_date 
            AND created_at <= :end_date
        """), {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        orders = result.fetchall()
        print(f"\nOrders in date range: {len(orders)}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# ============================================================
# METHOD 3: Complex Queries
# ============================================================

def complex_queries():
    """Example: Complex queries with JOINs, GROUP BY, etc."""
    db = SessionLocal()
    try:
        # Example 1: Get restaurant with order count
        result = db.execute(text("""
            SELECT 
                r.name,
                COUNT(o.id) as total_orders,
                SUM(o.total_amount) as total_revenue
            FROM restaurants r
            LEFT JOIN orders o ON r.id = o.restaurant_id
            GROUP BY r.id, r.name
            ORDER BY total_revenue DESC NULLS LAST
        """))
        stats = result.fetchall()
        print("\nRestaurant Statistics:")
        for row in stats:
            print(f"  {row[0]}: {row[1]} orders, ₹{row[2] or 0} revenue")
        
        # Example 2: Get order details with customer and items
        result = db.execute(text("""
            SELECT 
                o.id as order_id,
                o.order_status,
                o.total_amount,
                c.name as customer_name,
                c.phone as customer_phone,
                r.name as restaurant_name
            FROM orders o
            JOIN customers c ON o.customer_id = c.id
            JOIN restaurants r ON o.restaurant_id = r.id
            WHERE o.order_status != 'delivered'
            ORDER BY o.created_at DESC
        """))
        orders = result.fetchall()
        print("\nActive Orders:")
        for row in orders:
            print(f"  Order #{row[0]}: {row[1]} - {row[2]} - Customer: {row[3]} ({row[4]})")
        
        # Example 3: Get top selling products
        result = db.execute(text("""
            SELECT 
                p.name as product_name,
                r.name as restaurant_name,
                SUM(oi.quantity) as total_sold,
                SUM(oi.price * oi.quantity) as total_revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN restaurants r ON p.restaurant_id = r.id
            GROUP BY p.id, p.name, r.name
            ORDER BY total_sold DESC
            LIMIT 10
        """))
        top_products = result.fetchall()
        print("\nTop Selling Products:")
        for row in top_products:
            print(f"  {row[0]} ({row[1]}): {row[2]} sold, ₹{row[3]} revenue")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()


# ============================================================
# METHOD 4: INSERT, UPDATE, DELETE Examples
# ============================================================

def insert_update_delete_examples():
    """Example: INSERT, UPDATE, DELETE operations"""
    db = SessionLocal()
    try:
        # Example 1: INSERT
        db.execute(text("""
            INSERT INTO restaurants (id, name, phone, address, latitude, longitude, delivery_fee)
            VALUES (:id, :name, :phone, :address, :lat, :lng, :fee)
            ON CONFLICT (id) DO NOTHING
        """), {
            "id": "rest_new",
            "name": "New Restaurant",
            "phone": "+1234567890",
            "address": "123 Main St",
            "lat": 40.7128,
            "lng": -74.0060,
            "fee": 50.00
        })
        db.commit()
        print("✅ Restaurant inserted")
        
        # Example 2: UPDATE
        db.execute(text("""
            UPDATE restaurants 
            SET delivery_fee = :fee 
            WHERE id = :id
        """), {
            "id": "rest_new",
            "fee": 45.00
        })
        db.commit()
        print("✅ Restaurant updated")
        
        # Example 3: DELETE
        db.execute(text("DELETE FROM restaurants WHERE id = :id"), {
            "id": "rest_new"
        })
        db.commit()
        print("✅ Restaurant deleted")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


# ============================================================
# METHOD 5: Return as Dictionary (Easier to work with)
# ============================================================

def query_as_dict():
    """Example: Convert results to dictionaries"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM restaurants LIMIT 5"))
        
        # Get column names
        columns = result.keys()
        
        # Convert each row to dictionary
        restaurants = []
        for row in result:
            restaurant_dict = dict(zip(columns, row))
            restaurants.append(restaurant_dict)
        
        print("\nRestaurants as Dictionary:")
        for rest in restaurants:
            print(f"  {rest['name']} - {rest['phone']}")
        
        return restaurants
        
    except Exception as e:
        print(f"Error: {e}")
        return []
    finally:
        db.close()


# ============================================================
# Run Examples
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Database Query Examples")
    print("=" * 60)
    
    print("\n1. Raw SQL Queries:")
    print("-" * 60)
    query_with_raw_sql()
    
    print("\n\n2. Parameterized Queries:")
    print("-" * 60)
    query_with_parameters()
    
    print("\n\n3. Complex Queries:")
    print("-" * 60)
    complex_queries()
    
    print("\n\n4. Insert/Update/Delete:")
    print("-" * 60)
    insert_update_delete_examples()
    
    print("\n\n5. Query as Dictionary:")
    print("-" * 60)
    query_as_dict()
    
    print("\n" + "=" * 60)
    print("Done!")
