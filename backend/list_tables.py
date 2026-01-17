"""
List all tables in the database using SQL queries
"""
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://whatsapp_user:whatsapp_pass@localhost:5432/whatsapp_db"
)

engine = create_engine(DATABASE_URL)

print("=" * 80)
print("List of Tables")
print("=" * 80)

with engine.connect() as conn:
    # Method 1: Using information_schema (Standard SQL)
    print("\n📋 Method 1: Using information_schema")
    print("-" * 80)
    result = conn.execute(text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """))
    tables = result.fetchall()
    for i, (table_name,) in enumerate(tables, 1):
        print(f"  {i}. {table_name}")
    
    # Method 2: Get table count
    print(f"\n✅ Total tables: {len(tables)}")
    
    # Method 3: Get tables with row counts
    print("\n📊 Tables with Row Counts:")
    print("-" * 80)
    for table_name, in tables:
        try:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            print(f"  {table_name:30s} : {count:5d} rows")
        except Exception as e:
            print(f"  {table_name:30s} : Error - {e}")

print("\n" + "=" * 80)
