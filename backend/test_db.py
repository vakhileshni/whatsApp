"""
Database Connection Test Script
Run this to verify your database connection is working
"""
import os
from dotenv import load_dotenv
from database import check_db_connection, engine

# Load environment variables
load_dotenv()

def test_database():
    print("=" * 60)
    print("Testing Database Connection")
    print("=" * 60)
    
    # Show connection string (hide password)
    db_url = os.getenv("DATABASE_URL", "Not set")
    if db_url:
        # Hide password in output
        if "@" in db_url:
            parts = db_url.split("@")
            if ":" in parts[0]:
                user_pass = parts[0].split(":")
                if len(user_pass) == 3:  # postgresql://user:pass
                    masked = f"{user_pass[0]}://{user_pass[1]}:****@{parts[1]}"
                    print(f"Connection String: {masked}")
                else:
                    print(f"Connection String: {db_url.split('@')[0]}@****")
            else:
                print(f"Connection String: {db_url}")
        else:
            print(f"Connection String: {db_url}")
    else:
        print("⚠️  DATABASE_URL not set in .env file")
    
    print("\n1. Testing connection...")
    
    if check_db_connection():
        print("   ✅ Database connection successful!")
        
        # Test queries
        try:
            print("\n2. Testing table access...")
            with engine.connect() as conn:
                # Check if tables exist
                from sqlalchemy import text
                
                tables_to_check = [
                    'restaurants', 'users', 'products', 'customers',
                    'orders', 'order_items', 'customer_sessions'
                ]
                
                for table in tables_to_check:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        print(f"   ✅ Table '{table}': {count} rows")
                    except Exception as e:
                        print(f"   ❌ Table '{table}': {str(e)}")
                
                print("\n3. Database is ready to use! 🎉")
                
        except Exception as e:
            print(f"   ❌ Error querying tables: {e}")
            print("\n   ⚠️  Database connection works, but tables might not exist.")
            print("   Run: psql -U postgres -d whatsapp_db -f backend/init-db.sql")
            
    else:
        print("   ❌ Database connection failed!")
        print("\n   Troubleshooting:")
        print("   1. Check PostgreSQL is running")
        print("   2. Verify DATABASE_URL in .env file")
        print("   3. Ensure database 'whatsapp_db' exists")
        print("   4. Check username/password are correct")
        print("   5. Verify port 5432 is not blocked")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_database()
