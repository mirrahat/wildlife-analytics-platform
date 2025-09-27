#!/usr/bin/env python3
"""
ETL Pipeline Debug and Repair Tool
=================================
Diagnoses and fixes common ETL pipeline issues.
"""

import sqlite3
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def diagnose_etl_issues():
    """Diagnose common ETL pipeline issues"""
    
    print("🔍 ETL PIPELINE DIAGNOSTICS")
    print("=" * 40)
    
    db_path = "data/aussie_wildlife.db"
    
    if not os.path.exists(db_path):
        print("❌ Database not found!")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check table structures
            print("\n📊 TABLE STRUCTURE ANALYSIS:")
            
            tables = ['wildlife_bronze', 'wildlife_silver', 'wildlife_gold', 'etl_job_executions']
            for table in tables:
                try:
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = cursor.fetchall()
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    
                    print(f"\n🔹 {table.upper()}:")
                    print(f"   Records: {count}")
                    print(f"   Columns: {len(columns)}")
                    
                    # Show key columns
                    if table == 'wildlife_silver':
                        key_cols = ['common_name', 'location_description', 'observed_date']
                        for col in key_cols:
                            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL")
                            not_null_count = cursor.fetchone()[0]
                            percentage = (not_null_count / count * 100) if count > 0 else 0
                            print(f"   {col}: {not_null_count}/{count} ({percentage:.1f}% complete)")
                    
                except Exception as e:
                    print(f"   ❌ Error checking {table}: {e}")
            
            # Check recent ETL failures
            print(f"\n📋 RECENT ETL JOB ANALYSIS:")
            cursor.execute("""
                SELECT job_name, status, records_extracted, records_loaded, 
                       quality_issues, error_details
                FROM etl_job_executions 
                ORDER BY start_time DESC 
                LIMIT 5
            """)
            
            jobs = cursor.fetchall()
            for job_name, status, extracted, loaded, issues, errors in jobs:
                status_icon = "✅" if status == "success" else "❌"
                print(f"   {status_icon} {job_name}: {extracted}→{loaded} records")
                
                if issues:
                    try:
                        import json
                        issue_list = json.loads(issues)
                        if issue_list:
                            print(f"      Issues: {len(issue_list)}")
                            for issue in issue_list[:2]:  # Show first 2
                                print(f"        • {issue}")
                    except:
                        pass
                
                if errors and status == "failed":
                    print(f"      Error: {errors[:100]}...")
    
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return False
    
    return True

def fix_gold_layer_issues():
    """Fix common Gold layer analytics issues"""
    
    print("\n🔧 FIXING GOLD LAYER ANALYTICS")
    print("=" * 35)
    
    try:
        with sqlite3.connect("data/aussie_wildlife.db") as conn:
            # Read silver layer data
            silver_df = pd.read_sql("SELECT * FROM wildlife_silver", conn)
            
            if silver_df.empty:
                print("❌ No silver layer data to process")
                return False
            
            print(f"✅ Found {len(silver_df)} records in silver layer")
            
            # Check required columns
            required_cols = ['common_name', 'location_description', 'observed_date']
            missing_cols = [col for col in required_cols if col not in silver_df.columns]
            
            if missing_cols:
                print(f"❌ Missing columns: {missing_cols}")
                return False
            
            print("✅ All required columns present")
            
            # Generate analytics manually
            analytics_records = []
            
            # 1. Species counts
            species_counts = silver_df['common_name'].value_counts()
            for species, count in species_counts.items():
                analytics_records.append({
                    'aggregation_type': 'species_abundance',
                    'dimension_1': species,
                    'dimension_2': None,
                    'metric_name': 'observation_count',
                    'metric_value': count,
                    'created_at': pd.Timestamp.now()
                })
            
            # 2. Location richness
            location_species = silver_df.groupby('location_description')['common_name'].nunique()
            for location, species_count in location_species.items():
                analytics_records.append({
                    'aggregation_type': 'location_biodiversity',
                    'dimension_1': location,
                    'dimension_2': None,
                    'metric_name': 'species_richness',
                    'metric_value': species_count,
                    'created_at': pd.Timestamp.now()
                })
            
            # 3. Monthly trends
            silver_df['observed_date'] = pd.to_datetime(silver_df['observed_date'], errors='coerce')
            silver_df['year_month'] = silver_df['observed_date'].dt.to_period('M')
            monthly_counts = silver_df.groupby('year_month').size()
            
            for period, count in monthly_counts.items():
                analytics_records.append({
                    'aggregation_type': 'temporal_trends',
                    'dimension_1': str(period),
                    'dimension_2': None,
                    'metric_name': 'monthly_observations',
                    'metric_value': count,
                    'created_at': pd.Timestamp.now()
                })
            
            # Clear existing gold data and insert new
            cursor = conn.cursor()
            cursor.execute("DELETE FROM wildlife_gold")
            
            # Insert new analytics
            analytics_df = pd.DataFrame(analytics_records)
            analytics_df.to_sql('wildlife_gold', conn, if_exists='append', index=False)
            
            print(f"✅ Generated {len(analytics_records)} analytics records")
            print(f"   • Species abundance: {len(species_counts)} metrics")
            print(f"   • Location biodiversity: {len(location_species)} metrics")
            print(f"   • Temporal trends: {len(monthly_counts)} metrics")
            
            return True
            
    except Exception as e:
        print(f"❌ Fix error: {e}")
        return False

def run_etl_repair():
    """Run complete ETL repair process"""
    
    print("🔧 ETL PIPELINE REPAIR TOOL")
    print("=" * 30)
    
    # Step 1: Diagnose issues
    if not diagnose_etl_issues():
        return False
    
    # Step 2: Fix gold layer
    if not fix_gold_layer_issues():
        return False
    
    # Step 3: Verify fix
    print(f"\n✅ VERIFICATION:")
    try:
        with sqlite3.connect("data/aussie_wildlife.db") as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
            gold_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT aggregation_type) FROM wildlife_gold")
            agg_types = cursor.fetchone()[0]
            
            print(f"   Gold layer records: {gold_count}")
            print(f"   Analytics types: {agg_types}")
            
            if gold_count > 0:
                print("🎉 ETL pipeline repair successful!")
                return True
            
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    return False

if __name__ == "__main__":
    success = run_etl_repair()
    if success:
        print("\n🚀 Run ETL pipeline again to test the fix!")
    else:
        print("\n❌ Manual intervention required.")
