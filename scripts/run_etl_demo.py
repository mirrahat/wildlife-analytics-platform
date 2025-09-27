#!/usr/bin/env python3
"""
ETL Pipeline Demo Script
=======================
Demonstrates the complete ETL pipeline implementation for wildlife data.

This script shows how to:
1. Extract data from existing sources
2. Transform and clean the data
3. Load data into Bronze, Silver, and Gold layers
4. Monitor ETL job performance and quality
"""

import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from etl_pipeline import WildlifeETLPipeline, ETLJob

def run_complete_etl_demo():
    """Run a complete ETL pipeline demonstration"""
    
    print("🔄 WILDLIFE DATA ETL PIPELINE DEMONSTRATION")
    print("=" * 50)
    print("This demo shows Extract, Transform, Load operations")
    print("across Bronze → Silver → Gold data layers")
    print()
    
    # Initialize the ETL pipeline
    print("1. INITIALIZING ETL PIPELINE")
    print("-" * 30)
    etl = WildlifeETLPipeline()
    print("   ✓ ETL infrastructure setup completed")
    print("   ✓ Transformation functions registered")
    print("   ✓ Quality check functions registered")
    print()
    
    # Job 1: Extract from existing data and load to Silver layer
    print("2. EXECUTING: EXISTING DATA → SILVER LAYER")
    print("-" * 45)
    
    cleanup_job = ETLJob(
        job_name="data_standardization",
        source_type="database",
        source_config={
            "table_name": "wildlife_observations",
            "incremental": False
        },
        target_layer="silver",
        transformations=[
            "standardize_species_names",
            "validate_coordinates",
            "normalize_dates", 
            "clean_locations",
            "add_quality_flags"
        ],
        quality_checks=[
            "check_required_fields",
            "validate_australian_bounds",
            "check_date_ranges",
            "validate_species_names",
            "detect_duplicates"
        ]
    )
    
    print("   • Extracting data from wildlife_observations table...")
    print("   • Applying transformations: species names, coordinates, dates...")
    print("   • Running quality checks: required fields, Australian bounds...")
    
    result1 = etl.run_etl_job(cleanup_job)
    
    print(f"   ✓ Status: {result1.status}")
    print(f"   ✓ Records processed: {result1.records_extracted} → {result1.records_transformed} → {result1.records_loaded}")
    print(f"   ✓ Processing time: {result1.performance_metrics.get('duration_seconds', 0):.2f} seconds")
    print(f"   ✓ Quality issues found: {len(result1.quality_issues)}")
    
    if result1.quality_issues:
        print("     Quality Issues:")
        for issue in result1.quality_issues[:3]:
            print(f"       • {issue}")
    print()
    
    # Job 2: Collect fresh API data and load to Bronze layer  
    print("3. EXECUTING: API DATA → BRONZE LAYER")
    print("-" * 40)
    
    api_job = ETLJob(
        job_name="fresh_api_data_collection",
        source_type="api",
        source_config={
            "species_list": ["koala", "kangaroo", "wombat"],
            "limit_per_species": 3,
            "source_name": "iNaturalist_Live_API"
        },
        target_layer="bronze", 
        transformations=[],  # Keep raw data in bronze
        quality_checks=[
            "check_required_fields",
            "check_data_freshness"
        ]
    )
    
    print("   • Collecting fresh data from iNaturalist API...")
    print("   • Species: koala, kangaroo, wombat (3 records each)")
    print("   • Loading raw data to bronze layer...")
    
    result2 = etl.run_etl_job(api_job)
    
    print(f"   ✓ Status: {result2.status}")
    print(f"   ✓ Records collected: {result2.records_extracted}")
    print(f"   ✓ Records stored in bronze: {result2.records_loaded}")
    print(f"   ✓ Collection time: {result2.performance_metrics.get('duration_seconds', 0):.2f} seconds")
    
    if result2.quality_issues:
        print("     Quality Issues:")
        for issue in result2.quality_issues:
            print(f"       • {issue}")
    print()
    
    # Job 3: Create analytics aggregations for Gold layer
    print("4. EXECUTING: SILVER DATA → GOLD LAYER (ANALYTICS)")
    print("-" * 50)
    
    analytics_job = ETLJob(
        job_name="biodiversity_analytics",
        source_type="database",
        source_config={
            "table_name": "wildlife_silver", 
            "incremental": False
        },
        target_layer="gold",
        transformations=[
            "calculate_biodiversity_metrics",
            "detect_rare_species"
        ],
        quality_checks=[
            "validate_species_names"
        ]
    )
    
    print("   • Extracting cleansed data from silver layer...")
    print("   • Calculating biodiversity metrics and species richness...")
    print("   • Detecting rare species patterns...")
    print("   • Creating analytics-ready aggregations...")
    
    result3 = etl.run_etl_job(analytics_job)
    
    print(f"   ✓ Status: {result3.status}")
    print(f"   ✓ Records analyzed: {result3.records_extracted}")
    print(f"   ✓ Analytics records created: {result3.records_loaded}")
    print(f"   ✓ Analysis time: {result3.performance_metrics.get('duration_seconds', 0):.2f} seconds")
    print()
    
    # Summary of ETL pipeline results
    print("5. ETL PIPELINE EXECUTION SUMMARY")
    print("-" * 35)
    
    total_duration = sum([
        result1.performance_metrics.get('duration_seconds', 0),
        result2.performance_metrics.get('duration_seconds', 0), 
        result3.performance_metrics.get('duration_seconds', 0)
    ])
    
    total_quality_issues = len(result1.quality_issues) + len(result2.quality_issues) + len(result3.quality_issues)
    
    print(f"   Jobs Executed: 3")
    print(f"   Total Processing Time: {total_duration:.2f} seconds")
    print(f"   Total Quality Issues: {total_quality_issues}")
    print()
    print("   Data Flow Summary:")
    print(f"     • Bronze Layer: {result2.records_loaded} raw API records")
    print(f"     • Silver Layer: {result1.records_loaded} cleaned records")
    print(f"     • Gold Layer: {result3.records_loaded} analytics records")
    print()
    
    # Show ETL job execution history
    print("6. QUERYING ETL EXECUTION HISTORY")
    print("-" * 35)
    
    import sqlite3
    with sqlite3.connect("data/aussie_wildlife.db") as conn:
        cursor = conn.cursor()
        
        # Get recent ETL executions
        cursor.execute('''
            SELECT job_name, status, records_extracted, records_loaded, 
                   datetime(start_time) as execution_time
            FROM etl_job_executions 
            ORDER BY start_time DESC 
            LIMIT 5
        ''')
        
        executions = cursor.fetchall()
        
        if executions:
            print("   Recent ETL Job Executions:")
            for job_name, status, extracted, loaded, exec_time in executions:
                print(f"     • {job_name}: {status} ({extracted}→{loaded} records) at {exec_time}")
        else:
            print("   No previous ETL executions found")
    
    print()
    print("✅ ETL PIPELINE DEMONSTRATION COMPLETED")
    print("=" * 50)
    print("Your wildlife data has been processed through all ETL layers:")
    print("  🥉 Bronze: Raw data from APIs and sources")
    print("  🥈 Silver: Cleaned, validated, standardized data") 
    print("  🥇 Gold: Analytics-ready aggregations and insights")
    print()
    print("Next steps:")
    print("  • Use src/analysis/data_explorer.py to explore the data")
    print("  • Launch web_dashboard.py to visualize the results")
    print("  • Schedule regular ETL jobs for ongoing data processing")

def show_etl_layer_contents():
    """Show sample content from each ETL layer"""
    print("\n📊 ETL LAYER CONTENTS PREVIEW")
    print("=" * 35)
    
    import sqlite3
    with sqlite3.connect("data/aussie_wildlife.db") as conn:
        
        # Bronze layer sample
        print("\n🥉 BRONZE LAYER (Raw Data):")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
        bronze_count = cursor.fetchone()[0]
        print(f"   Total records: {bronze_count}")
        
        if bronze_count > 0:
            cursor.execute('''
                SELECT source_system, datetime(extracted_at) as extracted_time
                FROM wildlife_bronze 
                ORDER BY extracted_at DESC 
                LIMIT 3
            ''')
            recent_bronze = cursor.fetchall()
            print("   Recent extractions:")
            for source, time in recent_bronze:
                print(f"     • {source} at {time}")
        
        # Silver layer sample
        print("\n🥈 SILVER LAYER (Cleaned Data):")
        cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
        silver_count = cursor.fetchone()[0]
        print(f"   Total records: {silver_count}")
        
        if silver_count > 0:
            cursor.execute('''
                SELECT common_name, location_description, quality_score
                FROM wildlife_silver 
                ORDER BY quality_score DESC
                LIMIT 3
            ''')
            top_quality = cursor.fetchall()
            print("   Highest quality records:")
            for species, location, score in top_quality:
                print(f"     • {species} at {location} (quality: {score:.2f})")
        
        # Gold layer sample
        print("\n🥇 GOLD LAYER (Analytics Data):")
        cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
        gold_count = cursor.fetchone()[0]
        print(f"   Total metrics: {gold_count}")
        
        if gold_count > 0:
            cursor.execute('''
                SELECT aggregation_type, COUNT(*) as count
                FROM wildlife_gold
                GROUP BY aggregation_type
                ORDER BY count DESC
            ''')
            aggregations = cursor.fetchall()
            print("   Available aggregations:")
            for agg_type, count in aggregations:
                print(f"     • {agg_type}: {count} metrics")

def main():
    """Main function to run ETL demonstration"""
    try:
        run_complete_etl_demo()
        show_etl_layer_contents()
        
    except Exception as e:
        print(f"\n❌ ETL Demo Error: {e}")
        print("Make sure you have:")
        print("  • Run data collection first: python scripts/collect_wildlife_data.py")
        print("  • Installed required packages: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
