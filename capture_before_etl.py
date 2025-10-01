#!/usr/bin/env python3
"""
Quick before/after ETL comparison tool
"""
import sqlite3
from datetime import datetime

def capture_current_metrics():
    """Capture current metrics for comparison"""
    print("📸 CAPTURING CURRENT METRICS")
    print("=" * 35)
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        metrics = {}
        
        # Record counts
        tables = ['wildlife_bronze', 'wildlife_silver', 'wildlife_gold', 'wildlife_multisource']
        print("📊 Current Record Counts:")
        for table in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            metrics[table] = count
            print(f"   {table}: {count:,}")
        
        # ETL jobs
        etl_count = conn.execute("SELECT COUNT(*) FROM etl_job_executions").fetchone()[0]
        metrics['etl_jobs'] = etl_count
        print(f"   etl_job_executions: {etl_count:,}")
        
        # Latest ETL time
        latest_etl = conn.execute("""
            SELECT MAX(end_time) FROM etl_job_executions WHERE status = 'success'
        """).fetchone()[0]
        metrics['latest_etl'] = latest_etl
        print(f"   Latest successful ETL: {latest_etl}")
        
        # Species count
        species_count = conn.execute("""
            SELECT COUNT(DISTINCT common_name) FROM wildlife_silver WHERE common_name IS NOT NULL
        """).fetchone()[0]
        metrics['species_count'] = species_count
        print(f"   Unique species: {species_count}")
        
        print(f"\n⏰ Snapshot taken at: {datetime.now()}")
        
        return metrics

def instructions_for_comparison():
    """Provide instructions for running comparison"""
    print("\n🎯 COMPARISON INSTRUCTIONS")
    print("=" * 30)
    
    print("📋 Steps to see ETL differences:")
    print("   1. Note the metrics above ☝️")
    print("   2. Run ETL: python scripts/enhanced_etl_demo.py")
    print("   3. After completion, run: python compare_after_etl.py")
    print("   4. Compare the before/after numbers")
    
    print("\n🔍 What to Look For:")
    print("   • Higher record counts in all layers")
    print("   • New ETL job entries") 
    print("   • Updated timestamps (current time)")
    print("   • Potentially new species count")
    
    print("\n⚡ Quick Dashboard Check:")
    print("   • Go to ETL Monitoring page")
    print("   • Look for new jobs at top of list")
    print("   • Check if timestamps show current time")
    print("   • Refresh main dashboard to see updated metrics")

if __name__ == "__main__":
    metrics = capture_current_metrics()
    instructions_for_comparison()
    
    print(f"\n💡 TIP: Copy these numbers to compare after ETL run!")
    print("🌐 Dashboard: http://localhost:8501")