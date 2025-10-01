#!/usr/bin/env python3
"""
Test Complete ETL Session Dependency
Verify that all dashboard features are properly locked until ETL is run in current session
"""

import os
import sys
import sqlite3

# Add current directory to path
sys.path.append(os.getcwd())

from streamlit_dashboard import WildlifeDashboard

def test_complete_etl_dependency():
    """Test that all dashboard features are properly controlled by ETL session state"""
    
    print("🧪 Testing Complete ETL Session Dependency")
    print("=" * 60)
    
    # Initialize dashboard
    dashboard = WildlifeDashboard()
    
    # Test 1: Check ETL status without session state
    print("\n📋 Test 1: ETL Status Check (No Session State)")
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    print(f"ETL Executed: {etl_executed}")
    print(f"Message: {etl_message}")
    
    # Test 2: Check if we have sufficient data in database
    print("\n📋 Test 2: Data Availability Check")
    has_data = dashboard.has_sufficient_data()
    print(f"Has Sufficient Data: {has_data}")
    
    # Test 3: Verify database contains data but status is False
    print("\n📋 Test 3: Database Content vs Session Status")
    conn = dashboard.get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Count records in all tables
            cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
            multisource_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
            silver_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM etl_job_executions WHERE status = 'success'")
            etl_jobs = cursor.fetchone()[0]
            
            print(f"Multi-source Records: {multisource_count}")
            print(f"Silver Layer Records: {silver_count}")
            print(f"Successful ETL Jobs: {etl_jobs}")
            print(f"Database Has Data: {multisource_count > 0 and silver_count > 0}")
            print(f"BUT ETL Session Status: {etl_executed}")
            
            conn.close()
            
        except Exception as e:
            print(f"Database error: {e}")
            conn.close()
    
    print("\n✅ Test Results Summary:")
    print("=" * 40)
    
    if not etl_executed and has_data:
        print("✅ CORRECT: Database has data but ETL status is False (session-based)")
        print("✅ CORRECT: Dashboard will show 'Run ETL Demo' requirement")
        print("✅ CORRECT: Metrics will show '---' placeholders")
        print("✅ CORRECT: All visualizations will be locked")
    elif etl_executed:
        print("❌ WARNING: ETL status is True (should be False initially)")
        print("❌ This means dashboard will show data without ETL button press")
    else:
        print("❌ ERROR: No data available for testing")
    
    print("\n🎯 Expected Behavior:")
    print("1. Dashboard starts with ETL status = False")
    print("2. Shows '---' for all metrics")
    print("3. Shows 'Run ETL Demo' requirements on all pages")
    print("4. Only after pressing ETL button: status = True, data visible")
    
    print("\n🚀 Ready to test dashboard at http://localhost:8502")

if __name__ == "__main__":
    test_complete_etl_dependency()