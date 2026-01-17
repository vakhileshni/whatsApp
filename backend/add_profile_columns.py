"""
Script to add missing profile columns to restaurant_settings table
"""
from database import SessionLocal
from sqlalchemy import text

def add_missing_columns():
    """Add missing profile columns to restaurant_settings table"""
    db = SessionLocal()
    try:
        print("[INFO] Adding missing profile columns to restaurant_settings table...")
        
        # Add columns one by one (IF NOT EXISTS equivalent)
        columns_to_add = [
            ("delivery_radius_km", "INT NULL"),
            ("gst_number", "VARCHAR(50) NULL"),
            ("pan_number", "VARCHAR(20) NULL"),
            ("fssai_number", "VARCHAR(50) NULL"),
            ("operating_hours", "TEXT NULL"),
        ]
        
        for col_name, col_def in columns_to_add:
            try:
                # Check if column exists
                result = db.execute(text(f"""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'restaurant_settings'
                    AND column_name = '{col_name}'
                """))
                
                if result.fetchone():
                    print(f"[SKIP] Column {col_name} already exists")
                else:
                    # Add column
                    db.execute(text(f"ALTER TABLE restaurant_settings ADD COLUMN {col_name} {col_def}"))
                    print(f"[OK] Added column {col_name}")
            except Exception as e:
                print(f"[ERROR] Failed to add column {col_name}: {e}")
                db.rollback()
                return False
        
        db.commit()
        print("\n[OK] All columns added successfully!")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to add columns: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 80)
    print("Add Profile Columns to restaurant_settings")
    print("=" * 80)
    print()
    
    success = add_missing_columns()
    
    if success:
        print()
        print("=" * 80)
        print("SUCCESS! Profile columns added to restaurant_settings table")
        print("=" * 80)
    else:
        print()
        print("=" * 80)
        print("FAILED! Please check the error messages above")
        print("=" * 80)
