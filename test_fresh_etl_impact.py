#!/usr/bin/env python3
"""
Test Fresh ETL Impact - Show Real Before/After Changes
"""
import sqlite3
import pandas as pd
from datetime import datetime

def clear_database_for_fresh_demo():
    """Clear database to show real ETL impact"""
    
    print("🧹 CLEARING DATABASE FOR FRESH ETL DEMO")
    print("=" * 50)
    
    conn = sqlite3.connect('data/aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Show BEFORE counts
    cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
    bronze_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_silver") 
    silver_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
    gold_before = cursor.fetchone()[0]
    
    print(f"BEFORE ETL:")
    print(f"  Bronze: {bronze_before:,} records")
    print(f"  Silver: {silver_before:,} records") 
    print(f"  Gold: {gold_before:,} records")
    
    # Clear the layers (keep structure)
    cursor.execute("DELETE FROM wildlife_bronze")
    cursor.execute("DELETE FROM wildlife_silver")
    cursor.execute("DELETE FROM wildlife_gold")
    cursor.execute("DELETE FROM etl_job_executions")
    
    conn.commit()
    
    # Show AFTER clearing
    cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
    bronze_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
    silver_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
    gold_after = cursor.fetchone()[0]
    
    print(f"\nAFTER CLEARING:")
    print(f"  Bronze: {bronze_after:,} records")
    print(f"  Silver: {silver_after:,} records")
    print(f"  Gold: {gold_after:,} records")
    
    conn.close()
    
    print("\n✅ Database cleared! Now run 'Run ETL Demo' to see REAL impact!")
    print("📊 Your Streamlit dashboard will now show:")
    print("   BEFORE: All metrics at 0")
    print("   AFTER: Fresh data populated")

if __name__ == "__main__":
    clear_database_for_fresh_demo()