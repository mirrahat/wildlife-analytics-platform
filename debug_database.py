import sqlite3

def check_database_tables():
    """Check all database tables and their schemas"""
    conn = sqlite3.connect('aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    print("=== Available Database Tables ===")
    for table in sorted(tables):
        print(f"\n📋 Table: {table}")
        
        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   Rows: {count}")
        except Exception as e:
            print(f"   Error counting rows: {e}")
            
        # Get schema
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            print("   Columns:")
            for col in columns:
                print(f"     {col[1]} ({col[2]})")
        except Exception as e:
            print(f"   Error getting schema: {e}")
    
    # Check specifically for wildlife data tables
    print("\n=== Wildlife Data Summary ===")
    wildlife_tables = [t for t in tables if 'wildlife' in t.lower()]
    for table in wildlife_tables:
        try:
            cursor.execute(f"SELECT DISTINCT data_source, COUNT(*) FROM {table} GROUP BY data_source")
            sources = cursor.fetchall()
            print(f"\n{table} data sources:")
            for source, count in sources:
                print(f"  {source}: {count} records")
        except Exception as e:
            print(f"  {table}: No data_source column or error: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database_tables()