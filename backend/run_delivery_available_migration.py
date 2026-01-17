"""
Script to run migration for adding delivery_available column to restaurant_settings table
"""
from database import SessionLocal
from sqlalchemy import text
import os

def run_migration():
    """Run the delivery_available migration SQL"""
    db = SessionLocal()
    try:
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_delivery_available.sql')
        
        if not os.path.exists(migration_file):
            print(f"[ERROR] Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("[INFO] Running delivery_available migration...")
        
        # Execute the entire migration
        db.execute(text(migration_sql))
        db.commit()
        
        print("[OK] Migration completed successfully!")
        
        # Verify column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_settings'
            AND column_name = 'delivery_available'
        """))
        if result.fetchone():
            print("[OK] delivery_available column created successfully!")
        else:
            print("[ERROR] delivery_available column not found after migration!")
            return False
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Delivery Available Migration Script")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print()
        print("=" * 60)
        print("[OK] Migration completed successfully!")
        print("=" * 60)
        print()
        print("The delivery_available column has been added to restaurant_settings table.")
        print("Restaurants can now enable/disable delivery option for customers.")
    else:
        print()
        print("=" * 60)
        print("[ERROR] Migration failed!")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again.")
