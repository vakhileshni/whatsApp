"""
Quick Database Query Tool
Simple script to run SQL queries from command line
"""
from sqlalchemy import create_engine, text
import os
import sys

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://whatsapp_user:whatsapp_pass@localhost:5432/whatsapp_db"
)

def run_query(sql_query: str):
    """Run a SQL query and print results"""
    engine = create_engine(DATABASE_URL)
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql_query))
            
            # Get column names
            columns = result.keys()
            
            # Print header
            print("\n" + "=" * 80)
            print("Query Results:")
            print("=" * 80)
            print(" | ".join(str(col) for col in columns))
            print("-" * 80)
            
            # Print rows
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(" | ".join(str(val) for val in row))
                print(f"\nTotal rows: {len(rows)}")
            else:
                print("(No rows returned)")
            
            print("=" * 80 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    return True

def interactive_mode():
    """Interactive query mode"""
    print("=" * 80)
    print("Database Query Tool - Interactive Mode")
    print("=" * 80)
    print("Enter SQL queries (type 'exit' or 'quit' to stop)\n")
    
    engine = create_engine(DATABASE_URL)
    
    while True:
        try:
            query = input("SQL> ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            if not query:
                continue
            
            # Check for semicolon (optional)
            if not query.endswith(';'):
                query += ';'
            
            with engine.connect() as conn:
                result = conn.execute(text(query))
                columns = result.keys()
                rows = result.fetchall()
                
                if rows:
                    print("\n" + " | ".join(str(col) for col in columns))
                    print("-" * 80)
                    for row in rows:
                        print(" | ".join(str(val) for val in row))
                    print(f"\n({len(rows)} rows)\n")
                else:
                    print("✅ Query executed (no rows returned)\n")
                    
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run query from command line argument
        query = " ".join(sys.argv[1:])
        run_query(query)
    else:
        # Interactive mode
        interactive_mode()
