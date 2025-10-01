#!/usr/bin/env python3
"""
Quick database check script
"""
import sqlite3
import os

def check_database():
    db_path = "data/aussie_wildlife.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return
    
    print("✅ Database found!")
    
    conn = sqlite3.connect(db_path)
    
    tables = ['wildlife_observations', 'etl_job_executions', 'wildlife_bronze', 
              'wildlife_silver', 'wildlife_gold', 'wildlife_multisource']
    
    print("\n📊 Table Record Counts:")
    for table in tables:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"  {table}: {count:,} records")
        except Exception as e:
            print(f"  {table}: Error - {e}")
    
    # Check some sample data
    print("\n🔍 Sample Data Check:")
    try:
        result = conn.execute("SELECT common_name, scientific_name, location_description FROM wildlife_silver LIMIT 3").fetchall()
        for row in result:
            print(f"  - {row[0]} ({row[1]}) at {row[2]}")
    except Exception as e:
        print(f"  Sample data error: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_database()