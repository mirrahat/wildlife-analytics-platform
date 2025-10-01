import sqlite3

def check_data_database():
    """Check the data/aussie_wildlife.db database"""
    conn = sqlite3.connect('data/aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    print("=== Data Directory Database Tables ===")
    for table in sorted(tables):
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table}: {count} records")
        except Exception as e:
            print(f"{table}: Error - {e}")
    
    # Check specifically for wildlife data tables
    print("\n=== Wildlife Data Sources in data/aussie_wildlife.db ===")
    wildlife_tables = [t for t in tables if 'wildlife' in t.lower()]
    for table in wildlife_tables:
        try:
            cursor.execute(f"SELECT DISTINCT data_source, COUNT(*) FROM {table} GROUP BY data_source")
            sources = cursor.fetchall()
            print(f"\n{table}:")
            for source, count in sources:
                print(f"  {source}: {count} records")
        except Exception as e:
            print(f"  {table}: No data_source column or error: {e}")
    
    # Check if silver_wildlife_data exists and has data
    if 'silver_wildlife_data' in tables:
        print(f"\n=== silver_wildlife_data schema ===")
        cursor.execute("PRAGMA table_info(silver_wildlife_data)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_data_database()