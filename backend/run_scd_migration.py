"""
Script to run SCD Type 2 migration for UPI QR Code history
"""
from database import SessionLocal, engine
from sqlalchemy import text
import os

def run_migration():
    """Run the SCD migration SQL"""
    db = SessionLocal()
    try:
        # Read migration file
        migration_file = os.path.join(os.path.dirname(__file__), 'migrations', 'add_upi_qr_code_history.sql')
        
        if not os.path.exists(migration_file):
            print(f"[ERROR] Migration file not found: {migration_file}")
            return False
        
        with open(migration_file, 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Split by semicolons and execute each statement
        # PostgreSQL allows multiple statements in one execute
        print("[INFO] Running SCD Type 2 migration...")
        
        # Execute the entire migration
        db.execute(text(migration_sql))
        db.commit()
        
        print("[OK] Migration completed successfully!")
        
        # Verify table exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'restaurant_upi_qr_code_history'
        """))
        if result.fetchone():
            print("[OK] History table created successfully!")
        else:
            print("[ERROR] History table not found after migration!")
            return False
        
        # Verify trigger exists
        result = db.execute(text("""
            SELECT trigger_name 
            FROM information_schema.triggers 
            WHERE trigger_name = 'trigger_upi_qr_code_scd_update'
        """))
        if result.fetchone():
            print("[OK] SCD trigger created successfully!")
        else:
            print("[WARNING] SCD trigger not found!")
        
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
    print("SCD Type 2 Migration for UPI QR Code History")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    print()
    print("=" * 60)
    if success:
        print("[SUCCESS] Migration completed!")
    else:
        print("[FAILED] Migration had errors. Please check logs above.")
    print("=" * 60)
