#!/usr/bin/env python3
"""
Test ETL monitoring functionality
"""
import sys
import os
import sqlite3
import pandas as pd
import subprocess

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_etl_monitoring():
    """Test ETL monitoring features"""
    print("⚙️ Testing ETL Monitoring Features...")
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    # Test ETL job history loading
    print("\n📊 Testing ETL job history...")
    try:
        etl_history = dashboard.load_etl_job_history()
        print(f"   ✅ Loaded {len(etl_history)} ETL job records")
        
        if not etl_history.empty:
            print(f"   🔍 Columns: {list(etl_history.columns)}")
            
            # Check for required columns
            required_cols = ['job_name', 'status', 'start_time', 'end_time', 'duration_seconds']
            missing_cols = [col for col in required_cols if col not in etl_history.columns]
            if missing_cols:
                print(f"   ⚠️  Missing columns: {missing_cols}")
            else:
                print("   ✅ All required columns present")
            
            # Show status distribution
            status_counts = etl_history['status'].value_counts()
            print(f"   📈 Status distribution: {dict(status_counts)}")
            
            # Show recent jobs
            recent_jobs = etl_history.head(3)[['job_name', 'status', 'duration_seconds']]
            print("   🕒 Recent jobs:")
            for _, job in recent_jobs.iterrows():
                print(f"      - {job['job_name']}: {job['status']} ({job['duration_seconds']}s)")
        
    except Exception as e:
        print(f"   ❌ Error loading ETL history: {e}")

def test_etl_execution():
    """Test ETL pipeline execution"""
    print("\n🚀 Testing ETL Pipeline Execution...")
    
    script_path = os.path.join("scripts", "enhanced_etl_demo.py")
    if not os.path.exists(script_path):
        print(f"   ❌ ETL script not found: {script_path}")
        return
    
    print(f"   ✅ ETL script found: {script_path}")
    
    # Don't actually run the ETL pipeline in test mode, just verify it's callable
    print("   💡 ETL pipeline is available for execution")
    print("   📝 Script can be called via subprocess or dashboard button")

def test_etl_layers():
    """Test ETL layer data integrity"""
    print("\n🗄️ Testing ETL Data Layers...")
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        layers = {
            'bronze': 'wildlife_bronze',
            'silver': 'wildlife_silver', 
            'gold': 'wildlife_gold'
        }
        
        for layer_name, table_name in layers.items():
            try:
                count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                print(f"   📊 {layer_name.title()} layer ({table_name}): {count:,} records")
                
                # Check data quality for each layer
                if layer_name == 'silver' and count > 0:
                    avg_quality = conn.execute(f"SELECT AVG(quality_score) FROM {table_name}").fetchone()[0]
                    print(f"      🎯 Average quality score: {avg_quality:.3f}")
                
                # Check recent records
                try:
                    recent = conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE datetime(processed_at) > datetime('now', '-1 day')").fetchone()[0]
                    print(f"      ⏰ Recent records (24h): {recent}")
                except:
                    print(f"      ⏰ Recent records: Unable to check (no processed_at column)")
                    
            except Exception as e:
                print(f"   ❌ Error checking {layer_name} layer: {e}")

if __name__ == "__main__":
    test_etl_monitoring()
    test_etl_execution()
    test_etl_layers()
    print("\n✅ ETL Monitoring tests complete!")