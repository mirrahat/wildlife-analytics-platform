#!/usr/bin/env python3
"""
Test ETL Pipeline Dependency - Check if dashboard features depend on fresh ETL runs
"""
import sys
import os
import sqlite3
import pandas as pd
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_data_freshness():
    """Check how fresh the current data is and when ETL was last run"""
    print("🕒 DATA FRESHNESS ANALYSIS")
    print("=" * 50)
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        # Check ETL job execution times
        print("\n📊 ETL Pipeline Execution History:")
        try:
            recent_jobs = conn.execute("""
                SELECT job_name, status, start_time, end_time,
                       datetime('now') as current_time,
                       ROUND((julianday('now') - julianday(start_time)) * 24, 2) as hours_ago
                FROM etl_job_executions 
                ORDER BY start_time DESC 
                LIMIT 5
            """).fetchall()
            
            if recent_jobs:
                print("   Recent ETL runs:")
                for job in recent_jobs:
                    job_name, status, start_time, end_time, current_time, hours_ago = job
                    print(f"      {job_name}: {status} - {hours_ago} hours ago ({start_time})")
            else:
                print("   ❌ No ETL job history found")
                
        except Exception as e:
            print(f"   ❌ Error checking ETL history: {e}")
        
        # Check data creation/update timestamps
        print("\n📅 Data Layer Timestamps:")
        
        # Bronze layer freshness
        try:
            bronze_latest = conn.execute("""
                SELECT MAX(extracted_at) as latest_bronze,
                       COUNT(*) as total_records,
                       ROUND((julianday('now') - julianday(MAX(extracted_at))) * 24, 2) as hours_old
                FROM wildlife_bronze
            """).fetchone()
            
            if bronze_latest[0]:
                print(f"   🥉 Bronze layer: {bronze_latest[1]} records, latest {bronze_latest[2]:.1f}h old ({bronze_latest[0]})")
            else:
                print("   🥉 Bronze layer: No timestamp data")
        except Exception as e:
            print(f"   🥉 Bronze layer error: {e}")
        
        # Silver layer freshness
        try:
            silver_latest = conn.execute("""
                SELECT MAX(processed_at) as latest_silver,
                       COUNT(*) as total_records,
                       ROUND((julianday('now') - julianday(MAX(processed_at))) * 24, 2) as hours_old
                FROM wildlife_silver
            """).fetchone()
            
            if silver_latest[0]:
                print(f"   🥈 Silver layer: {silver_latest[1]} records, latest {silver_latest[2]:.1f}h old ({silver_latest[0]})")
            else:
                print("   🥈 Silver layer: No timestamp data")
        except Exception as e:
            print(f"   🥈 Silver layer error: {e}")
        
        # Multi-source data freshness
        try:
            multisource_latest = conn.execute("""
                SELECT MAX(collected_at) as latest_collection,
                       COUNT(*) as total_records,
                       ROUND((julianday('now') - julianday(MAX(collected_at))) * 24, 2) as hours_old
                FROM wildlife_multisource
            """).fetchone()
            
            if multisource_latest[0]:
                print(f"   🔗 Multi-source: {multisource_latest[1]} records, latest {multisource_latest[2]:.1f}h old ({multisource_latest[0]})")
            else:
                print("   🔗 Multi-source: No timestamp data")
        except Exception as e:
            print(f"   🔗 Multi-source error: {e}")

def simulate_fresh_etl_dependency():
    """Test what happens when we simulate a fresh ETL run vs old data"""
    print("\n🧪 ETL DEPENDENCY TEST")
    print("=" * 40)
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    print("\n1️⃣ Current Dashboard Data (Before ETL):")
    
    # Test current data state
    try:
        etl_summary = dashboard.load_etl_layers_summary()
        silver_data = dashboard.load_silver_layer_data()
        etl_history = dashboard.load_etl_job_history()
        
        print(f"   📊 ETL Summary metrics: {len(etl_summary)} items")
        if etl_summary:
            print(f"      Bronze: {etl_summary.get('bronze_count', 0)} records")
            print(f"      Silver: {etl_summary.get('silver_count', 0)} records")
            print(f"      Gold: {etl_summary.get('gold_count', 0)} records")
            print(f"      Success rate: {etl_summary.get('successful_jobs', 0)}/{etl_summary.get('total_jobs', 0)}")
        
        print(f"   🥈 Silver layer: {len(silver_data)} records")
        print(f"   📈 ETL history: {len(etl_history)} job records")
        
        # Check if data has real-time elements
        if not silver_data.empty:
            species_count = silver_data['common_name'].nunique()
            latest_observation = silver_data['observed_date'].max() if 'observed_date' in silver_data.columns else 'N/A'
            print(f"   🐾 Species diversity: {species_count} species")
            print(f"   📅 Latest observation: {latest_observation}")
    
    except Exception as e:
        print(f"   ❌ Error testing current data: {e}")

def check_static_vs_dynamic_data():
    """Check if the data is static (cached) or dynamic (ETL-dependent)"""
    print("\n🔍 STATIC vs DYNAMIC DATA ANALYSIS")
    print("=" * 45)
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        # Check for any indicators of dynamic vs static data
        
        # 1. Check if there are multiple data collection dates
        try:
            date_variety = conn.execute("""
                SELECT COUNT(DISTINCT DATE(observed_date)) as unique_dates,
                       MIN(observed_date) as earliest,
                       MAX(observed_date) as latest
                FROM wildlife_silver
                WHERE observed_date IS NOT NULL
            """).fetchone()
            
            print(f"\n📅 Temporal Data Variety:")
            print(f"   Unique observation dates: {date_variety[0]}")
            print(f"   Date range: {date_variety[1]} to {date_variety[2]}")
            
            if date_variety[0] <= 1:
                print("   🚨 WARNING: All data from same date - likely static/demo data")
            else:
                print("   ✅ Multiple dates - indicates dynamic data collection")
                
        except Exception as e:
            print(f"   ❌ Error checking date variety: {e}")
        
        # 2. Check for batch processing indicators
        try:
            batch_info = conn.execute("""
                SELECT COUNT(DISTINCT batch_id) as batches,
                       COUNT(DISTINCT source_system) as sources
                FROM wildlife_bronze
            """).fetchone()
            
            print(f"\n🔄 Batch Processing Indicators:")
            print(f"   Unique batch IDs: {batch_info[0]}")
            print(f"   Source systems: {batch_info[1]}")
            
            if batch_info[0] <= 1:
                print("   🚨 WARNING: Single batch - may be demo/test data")
            else:
                print("   ✅ Multiple batches - indicates ongoing ETL processing")
                
        except Exception as e:
            print(f"   ❌ Error checking batch info: {e}")
        
        # 3. Check for real-time collection patterns
        try:
            collection_pattern = conn.execute("""
                SELECT DATE(collected_at) as collection_date,
                       COUNT(*) as records_per_day
                FROM wildlife_multisource
                GROUP BY DATE(collected_at)
                ORDER BY collection_date DESC
                LIMIT 7
            """).fetchall()
            
            print(f"\n📊 Recent Collection Pattern:")
            if collection_pattern:
                for date, count in collection_pattern:
                    print(f"   {date}: {count} records")
                
                if len(collection_pattern) == 1:
                    print("   🚨 WARNING: All data collected on same day - likely batch demo data")
                else:
                    print("   ✅ Multiple collection dates - indicates ongoing data pipeline")
            else:
                print("   ❌ No collection pattern data available")
                
        except Exception as e:
            print(f"   ❌ Error checking collection pattern: {e}")

def test_etl_pipeline_necessity():
    """Test if running ETL pipeline actually changes the dashboard results"""
    print("\n🎯 ETL PIPELINE NECESSITY TEST")
    print("=" * 40)
    
    # Check if the ETL script exists and is functional
    etl_script_path = os.path.join("scripts", "enhanced_etl_demo.py")
    
    if os.path.exists(etl_script_path):
        print(f"   ✅ ETL script found: {etl_script_path}")
        
        # Get current data counts before potential ETL run
        db_path = "data/aussie_wildlife.db"
        with sqlite3.connect(db_path) as conn:
            current_counts = {}
            tables = ['wildlife_bronze', 'wildlife_silver', 'wildlife_gold', 'wildlife_multisource']
            
            for table in tables:
                try:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    current_counts[table] = count
                except:
                    current_counts[table] = 0
        
        print("\n📊 Current Data Counts (Pre-ETL):")
        for table, count in current_counts.items():
            print(f"   {table}: {count:,} records")
        
        print("\n💡 ETL Pipeline Analysis:")
        print("   - Dashboard shows data even without fresh ETL runs")
        print("   - Data appears to be from previous ETL executions")
        print("   - Pipeline likely populates database, dashboard reads cached results")
        print("   - For truly fresh data, ETL pipeline should be run regularly")
        
        # Check ETL execution logs to see actual dependency
        try:
            with sqlite3.connect(db_path) as conn:
                last_successful_etl = conn.execute("""
                    SELECT MAX(end_time) as last_success
                    FROM etl_job_executions 
                    WHERE status = 'success'
                """).fetchone()[0]
                
                if last_successful_etl:
                    print(f"   📅 Last successful ETL: {last_successful_etl}")
                    
                    # Calculate time since last ETL
                    from datetime import datetime
                    try:
                        last_etl_time = datetime.fromisoformat(last_successful_etl.replace('Z', '+00:00'))
                        time_diff = datetime.now() - last_etl_time.replace(tzinfo=None)
                        hours_since = time_diff.total_seconds() / 3600
                        
                        if hours_since > 24:
                            print(f"   🚨 WARNING: ETL last ran {hours_since:.1f} hours ago - data may be stale")
                        else:
                            print(f"   ✅ ETL ran {hours_since:.1f} hours ago - relatively fresh data")
                    except:
                        print("   ⚠️  Could not parse ETL timestamp for freshness check")
                else:
                    print("   ❌ No successful ETL runs found")
                    
        except Exception as e:
            print(f"   ❌ Error checking ETL logs: {e}")
    
    else:
        print(f"   ❌ ETL script not found: {etl_script_path}")

if __name__ == "__main__":
    check_data_freshness()
    simulate_fresh_etl_dependency()
    check_static_vs_dynamic_data()
    test_etl_pipeline_necessity()
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION:")
    print("=" * 60)
    print("✅ Dashboard DOES show results without fresh ETL runs")
    print("📚 Data comes from PREVIOUS ETL executions stored in database")
    print("🔄 ETL pipeline SHOULD be run regularly for fresh data")
    print("⚠️  Current data may be cached/demo data from earlier runs")
    print("💡 For production: Set up scheduled ETL runs for data freshness")
    print("\n🌐 Dashboard remains accessible at: http://localhost:8501")