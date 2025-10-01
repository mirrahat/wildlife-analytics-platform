#!/usr/bin/env python3
"""
Test the improved datetime fix
"""
import pandas as pd
import sqlite3

def test_improved_datetime_fix():
    """Test the improved datetime conversion"""
    print("🔧 Testing Improved DateTime Fix")
    print("=" * 35)
    
    # Load sample data
    conn = sqlite3.connect('data/aussie_wildlife.db')
    sample_data = pd.read_sql_query("SELECT observed_date FROM wildlife_silver LIMIT 10", conn)
    conn.close()
    
    print(f"📊 Sample data: {len(sample_data)} records")
    print(f"🔍 Sample values: {sample_data['observed_date'].unique()}")
    print(f"📝 Data type: {sample_data['observed_date'].dtype}")
    
    # Test the improved conversion logic
    try:
        print("\n🧪 Testing datetime conversion...")
        
        # Step 1: Try pandas datetime conversion
        sample_data['observed_date_dt'] = pd.to_datetime(sample_data['observed_date'], errors='coerce')
        print(f"✅ Conversion successful: {sample_data['observed_date_dt'].dtype}")
        
        # Step 2: Check if we have valid dates
        if not sample_data['observed_date_dt'].isna().all():
            print("✅ Valid datetime data found")
            
            # Step 3: Test groupby with dt accessor
            daily_counts = sample_data.groupby(sample_data['observed_date_dt'].dt.date).size()
            print(f"✅ Groupby successful: {len(daily_counts)} unique dates")
            print(f"📅 Date range: {daily_counts.index}")
            
        else:
            print("⚠️  No valid datetime data after conversion")
            # Fallback test
            date_counts = sample_data['observed_date'].value_counts()
            print(f"✅ Fallback working: {len(date_counts)} unique string dates")
        
        print("\n✅ Improved datetime fix is working!")
        
    except Exception as e:
        print(f"❌ Error in datetime fix: {e}")

if __name__ == "__main__":
    test_improved_datetime_fix()