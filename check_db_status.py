#!/usr/bin/env python3
"""Quick database status check script"""
import sqlite3
import sys

try:
    conn = sqlite3.connect('data/aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Available tables: {tables}")
    
    # Check multi-source table
    if 'wildlife_multisource' in tables:
        cursor.execute('SELECT COUNT(*) FROM wildlife_multisource')
        count = cursor.fetchone()[0]
        print(f"Multi-source records: {count}")
        
        if count > 0:
            cursor.execute('SELECT data_source, COUNT(*) FROM wildlife_multisource GROUP BY data_source')
            sources = cursor.fetchall()
            print("Records per source:")
            for source, count in sources:
                print(f"  {source}: {count}")
    else:
        print("wildlife_multisource table not found")
    
    # Check other tables
    for table in ['wildlife_bronze', 'wildlife_silver', 'wildlife_gold']:
        if table in tables:
            cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = cursor.fetchone()[0]
            print(f"{table} records: {count}")
    
    conn.close()
    print("Database check completed successfully!")
    
except Exception as e:
    print(f"Error checking database: {e}")
    sys.exit(1)
