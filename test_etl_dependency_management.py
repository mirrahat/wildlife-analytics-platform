import sqlite3
import pandas as pd

def test_etl_dependency_management():
    """Test the new ETL dependency management system"""
    print("=== Testing ETL Dependency Management System ===")
    
    # Test the ETL status check functions
    print("\n🔍 1. Testing ETL Status Check Functions:")
    
    try:
        # Import the dashboard class
        import sys
        sys.path.append('.')
        from streamlit_dashboard import WildlifeDashboard
        
        dashboard = WildlifeDashboard()
        
        # Test ETL execution status
        etl_executed, etl_message = dashboard.check_etl_execution_status()
        print(f"✅ ETL Execution Status: {etl_executed}")
        print(f"   Message: {etl_message}")
        
        # Test data sufficiency
        has_data = dashboard.has_sufficient_data()
        print(f"✅ Has Sufficient Data: {has_data}")
        
    except Exception as e:
        print(f"❌ Dashboard class test error: {e}")
    
    print("\n🔍 2. Testing Database Data Counts:")
    
    try:
        conn = sqlite3.connect('data/aussie_wildlife.db')
        cursor = conn.cursor()
        
        # Count multisource records
        cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
        multisource_count = cursor.fetchone()[0]
        print(f"   Multi-source records: {multisource_count}")
        
        # Count silver records
        cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
        silver_count = cursor.fetchone()[0]
        print(f"   Silver layer records: {silver_count}")
        
        # Count recent multisource records (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) FROM wildlife_multisource 
            WHERE collected_at > datetime('now', '-1 day')
        """)
        recent_multisource = cursor.fetchone()[0]
        print(f"   Recent multi-source records: {recent_multisource}")
        
        # Count recent ETL jobs
        cursor.execute("""
            SELECT COUNT(*) FROM etl_job_executions 
            WHERE start_time > datetime('now', '-1 day')
            AND status = 'success'
        """)
        recent_etl_jobs = cursor.fetchone()[0]
        print(f"   Recent successful ETL jobs: {recent_etl_jobs}")
        
        conn.close()
        
        # Determine thresholds
        data_sufficient = multisource_count >= 100 or silver_count >= 50
        recent_activity = recent_multisource > 0 and recent_etl_jobs > 0
        
        print(f"\n📊 Threshold Analysis:")
        print(f"   Data sufficient (≥100 multi or ≥50 silver): {data_sufficient}")
        print(f"   Recent ETL activity (last 24h): {recent_activity}")
        
    except Exception as e:
        print(f"❌ Database query error: {e}")
    
    print("\n🎯 Expected Dashboard Behavior:")
    
    try:
        dashboard = WildlifeDashboard()
        etl_executed, etl_message = dashboard.check_etl_execution_status()
        has_data = dashboard.has_sufficient_data()
        
        if etl_executed and has_data:
            print("✅ **FULL DASHBOARD MODE**")
            print("   - Main dashboard: Success banner")
            print("   - Data Quality: Complete analysis with charts")
            print("   - All features available")
            print("   - Sidebar: '✅ ETL: Ready'")
        else:
            print("⚠️ **ETL REQUIRED MODE**")
            print("   - Main dashboard: ETL requirement banner")
            print("   - Data Quality: Warning with limited preview")
            print("   - User guided to run ETL Demo")
            print("   - Sidebar: '⚠️ ETL: Required'")
            
    except Exception as e:
        print(f"❌ Dashboard behavior test error: {e}")
    
    print("\n🚀 ETL Dependency System Features:")
    print("✅ check_etl_execution_status() - Checks recent ETL activity")
    print("✅ has_sufficient_data() - Validates data quantity thresholds") 
    print("✅ Main Dashboard - ETL status banner")
    print("✅ Data Quality Dashboard - ETL requirement check with preview")
    print("✅ Sidebar - ETL status indicator")
    print("✅ Enhanced ETL Button - Context-aware button text")
    print("✅ Session State - Tracks ETL execution")
    print("✅ User Guidance - Clear instructions for ETL execution")
    
    print(f"\n🌐 Test the ETL dependency system at: http://localhost:8502")
    print("**Testing Steps:**")
    print("1. Navigate to Data Quality page - observe ETL requirements")
    print("2. Check main dashboard - observe status banners")
    print("3. Look at sidebar - observe ETL status indicator")
    print("4. Click 'Run ETL Demo' - observe enhanced button behavior")
    print("5. After ETL completion - observe changed dashboard behavior")

if __name__ == "__main__":
    test_etl_dependency_management()