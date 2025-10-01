#!/usr/bin/env python3
"""
Test the main dashboard functionality
"""
import sys
import os
import sqlite3
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_dashboard_functions():
    """Test the key dashboard functions"""
    
    # Import the dashboard class
    sys.path.append('.')
    from streamlit_dashboard import WildlifeDashboard
    
    print("🧪 Testing Dashboard Functions...")
    
    dashboard = WildlifeDashboard()
    
    # Test 1: Database connection
    print("\n1️⃣ Testing database connection...")
    conn = dashboard.get_connection()
    if conn:
        print("   ✅ Database connection successful")
        conn.close()
    else:
        print("   ❌ Database connection failed")
        return
    
    # Test 2: Load wildlife observations
    print("\n2️⃣ Testing wildlife observations loading...")
    try:
        wildlife_data = dashboard.load_wildlife_observations()
        print(f"   ✅ Loaded {len(wildlife_data)} wildlife observations")
        if not wildlife_data.empty:
            print(f"   📊 Columns: {list(wildlife_data.columns)}")
    except Exception as e:
        print(f"   ❌ Error loading wildlife observations: {e}")
    
    # Test 3: ETL layers summary
    print("\n3️⃣ Testing ETL layers summary...")
    try:
        etl_summary = dashboard.load_etl_layers_summary()
        if etl_summary:
            print("   ✅ ETL summary loaded successfully")
            for key, value in etl_summary.items():
                print(f"   📈 {key}: {value}")
        else:
            print("   ❌ ETL summary is empty")
    except Exception as e:
        print(f"   ❌ Error loading ETL summary: {e}")
    
    # Test 4: Silver layer data
    print("\n4️⃣ Testing silver layer data...")
    try:
        silver_data = dashboard.load_silver_layer_data()
        print(f"   ✅ Loaded {len(silver_data)} silver layer records")
        if not silver_data.empty:
            print(f"   🐾 Unique species: {silver_data['common_name'].nunique()}")
            print(f"   📍 Records with coordinates: {silver_data[['latitude', 'longitude']].notna().all(axis=1).sum()}")
    except Exception as e:
        print(f"   ❌ Error loading silver layer data: {e}")
    
    # Test 5: ETL job history
    print("\n5️⃣ Testing ETL job history...")
    try:
        etl_history = dashboard.load_etl_job_history()
        print(f"   ✅ Loaded {len(etl_history)} ETL job records")
        if not etl_history.empty:
            success_count = (etl_history['status'] == 'success').sum()
            print(f"   📊 Successful jobs: {success_count}/{len(etl_history)}")
    except Exception as e:
        print(f"   ❌ Error loading ETL history: {e}")

def test_advanced_analytics():
    """Test advanced analytics functionality"""
    print("\n🤖 Testing Advanced Analytics...")
    
    try:
        from src.advanced_analytics import AdvancedWildlifeAnalytics
        analytics = AdvancedWildlifeAnalytics()
        
        # Test data loading
        data = analytics.load_comprehensive_data()
        print(f"   ✅ Advanced analytics data loaded: {len(data)} records")
        
        if not data.empty:
            print(f"   🔬 Species for analysis: {data['species'].nunique()}")
            if 'observed_date' in data.columns:
                print(f"   📅 Date range: {data['observed_date'].min()} to {data['observed_date'].max()}")
            else:
                print(f"   📊 Available columns: {list(data.columns)}")
        
    except ImportError:
        print("   ⚠️ Advanced analytics module not available (missing scikit-learn?)")
    except Exception as e:
        print(f"   ❌ Error in advanced analytics: {e}")

if __name__ == "__main__":
    test_dashboard_functions()
    test_advanced_analytics()
    print("\n✅ Testing complete!")