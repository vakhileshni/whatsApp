"""
Script to check if restaurant_settings table exists and has all required columns
"""
from database import SessionLocal
from sqlalchemy import text

def check_table():
    """Check if restaurant_settings table exists and has all columns"""
    db = SessionLocal()
    try:
        # Check if table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name = 'restaurant_settings'
        """))
        
        table_exists = result.fetchone() is not None
        
        if not table_exists:
            print("[ERROR] restaurant_settings table does NOT exist!")
            print("You need to run the migration: python run_settings_migration.py")
            return False
        
        print("[OK] restaurant_settings table exists!")
        
        # Check all columns
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'restaurant_settings'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
        print(f"\n[INFO] Found {len(columns)} columns in restaurant_settings table:")
        print("-" * 80)
        for col in columns:
            print(f"  - {col[0]:40} {col[1]:20} {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        # Check for required profile columns
        required_profile_columns = [
            'delivery_radius_km',
            'gst_number', 
            'pan_number',
            'fssai_number',
            'operating_hours'
        ]
        
        existing_column_names = [col[0] for col in columns]
        missing_columns = [col for col in required_profile_columns if col not in existing_column_names]
        
        if missing_columns:
            print("\n[WARNING] Missing profile columns:")
            for col in missing_columns:
                print(f"  - {col}")
            print("\nYou need to add these columns. Run: python add_profile_columns.py")
            return False
        else:
            print("\n[OK] All required columns exist!")
            return True
        
    except Exception as e:
        print(f"[ERROR] Error checking table: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("Restaurant Settings Table Checker")
    print("=" * 80)
    print()
    
    check_table()
    
    print()
    print("=" * 80)
