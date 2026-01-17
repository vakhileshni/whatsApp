"""
Script to run migration for restaurant_settings table
"""
from database import SessionLocal, engine
from sqlalchemy import text
import os

def run_migration():
    """Run the restaurant_settings migration SQL"""
    db = SessionLocal()
    try:
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_restaurant_settings.sql')
        
        if not os.path.exists(migration_file):
            print(f"[ERROR] Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("[INFO] Running restaurant_settings migration...")
        
        # Execute the entire migration
        db.execute(text(migration_sql))
        db.commit()
        
        print("[OK] Migration completed successfully!")
        
        # Verify table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'restaurant_settings'
        """))
        if result.fetchone():
            print("[OK] restaurant_settings table created successfully!")
        else:
            print("[ERROR] restaurant_settings table not found after migration!")
            return False
        
        # Verify columns exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_settings'
            AND column_name IN ('delivery_radius_km', 'gst_number', 'pan_number', 'fssai_number', 'operating_hours')
        """))
        columns = [row[0] for row in result.fetchall()]
        if all(col in columns for col in ['delivery_radius_km', 'gst_number', 'pan_number', 'fssai_number', 'operating_hours']):
            print("[OK] All profile settings columns exist!")
        else:
            print(f"[WARNING] Some columns missing. Found: {columns}")
        
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
    print("Restaurant Settings Migration Script")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print()
        print("=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print()
        print("The restaurant_settings table is now ready to use.")
        print("You can now save notification, order, and profile settings.")
    else:
        print()
        print("=" * 60)
        print("❌ Migration failed!")
        print("=" * 60)
        print()
        print("Please check the error messages above and try again.")
