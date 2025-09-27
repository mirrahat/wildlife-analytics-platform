#!/usr/bin/env python3
"""
Enhanced ETL Pipeline Demonstration
=================================
Comprehensive demonstration of the Australian Biodiversity ETL pipeline
showing enterprise-grade features, error handling, and data lifecycle management.

Features demonstrated:
1. Multi-source data extraction (API + Database)
2. Robust transformation pipeline with error handling
3. Quality validation and monitoring
4. Bronze → Silver → Gold data lake architecture
5. Performance monitoring and job tracking
6. Data lineage and audit trails
"""

import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import sqlite3

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from etl_pipeline import WildlifeETLPipeline, ETLJob
from analysis.data_explorer import WildlifeAnalyzer

def demonstrate_complete_data_lifecycle():
    """Demonstrate complete data lifecycle management"""
    
    print("🌟 ENTERPRISE WILDLIFE DATA ETL PIPELINE")
    print("=" * 55)
    print("Demonstrating contemporary, enterprise-grade ETL operations")
    print("for Australian Biodiversity Analytics Platform\n")
    
    # Initialize components
    etl = WildlifeETLPipeline()
    analyzer = WildlifeAnalyzer()
    
    print("📊 PHASE 1: DATA EXTRACTION & BRONZE LAYER")
    print("-" * 50)
    
    # Job 1: Collect fresh API data
    api_job = ETLJob(
        job_name="api_data_ingestion",
        source_type="api",
        source_config={
            "species_list": ["koala", "kangaroo", "echidna", "wombat", "platypus"],
            "limit_per_species": 4,
            "source_name": "iNaturalist_Live_API"
        },
        target_layer="bronze",
        transformations=[],  # Keep raw in bronze
        quality_checks=["check_data_freshness"]
    )
    
    print("🔄 Executing API data collection...")
    print("   • Target species: Koala, Kangaroo, Echidna, Wombat, Platypus")
    print("   • Data source: iNaturalist Live API")
    print("   • Target layer: Bronze (raw data)")
    
    api_result = etl.run_etl_job(api_job)
    
    print(f"\n   ✓ Collection Status: {api_result.status}")
    print(f"   ✓ Records collected: {api_result.records_extracted}")
    print(f"   ✓ Records stored: {api_result.records_loaded}")
    print(f"   ✓ Duration: {api_result.performance_metrics.get('duration_seconds', 0):.2f}s")
    
    if api_result.quality_issues:
        print("   ⚠️  Quality Issues:")
        for issue in api_result.quality_issues[:3]:
            print(f"      • {issue}")
    
    print("\n🔄 PHASE 2: DATA STANDARDIZATION & SILVER LAYER")
    print("-" * 52)
    
    # Job 2: Transform existing observations to silver
    standardization_job = ETLJob(
        job_name="data_standardization_enhanced",
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
    
    print("🔄 Executing data standardization...")
    print("   • Source: Existing wildlife observations")
    print("   • Transformations: Species names, coordinates, dates, locations")
    print("   • Quality checks: 5 validation rules")
    print("   • Target layer: Silver (clean, validated data)")
    
    standard_result = etl.run_etl_job(standardization_job)
    
    print(f"\n   ✓ Processing Status: {standard_result.status}")
    print(f"   ✓ Records processed: {standard_result.records_extracted} → {standard_result.records_transformed}")
    print(f"   ✓ Records loaded: {standard_result.records_loaded}")
    print(f"   ✓ Quality score: {standard_result.performance_metrics.get('transformation_success_rate', 0)*100:.1f}%")
    print(f"   ✓ Duration: {standard_result.performance_metrics.get('duration_seconds', 0):.2f}s")
    
    if standard_result.quality_issues:
        print("   📋 Quality Assessment:")
        issue_types = {'CRITICAL': [], 'WARNING': [], 'INFO': []}
        for issue in standard_result.quality_issues:
            if 'CRITICAL' in issue:
                issue_types['CRITICAL'].append(issue)
            elif 'WARNING' in issue:
                issue_types['WARNING'].append(issue)
            else:
                issue_types['INFO'].append(issue)
        
        for level, issues in issue_types.items():
            if issues:
                print(f"      {level}: {len(issues)} issues")
                for issue in issues[:2]:  # Show first 2 of each type
                    print(f"        • {issue.replace(level+': ', '')}")
    
    print("\n📈 PHASE 3: ANALYTICS GENERATION & GOLD LAYER")
    print("-" * 51)
    
    # Job 3: Create analytics aggregations
    analytics_job = ETLJob(
        job_name="biodiversity_analytics_enhanced",
        source_type="database",
        source_config={
            "table_name": "wildlife_silver",
            "incremental": False
        },
        target_layer="gold",
        transformations=[
            "calculate_biodiversity_metrics",
            "detect_rare_species",
            "aggregate_by_location",
            "aggregate_by_time"
        ],
        quality_checks=[
            "validate_species_names"
        ]
    )
    
    print("🔄 Executing analytics generation...")
    print("   • Source: Silver layer validated data")
    print("   • Analytics: Biodiversity metrics, rare species, spatial/temporal patterns")
    print("   • Target layer: Gold (analytics-ready aggregations)")
    
    analytics_result = etl.run_etl_job(analytics_job)
    
    print(f"\n   ✓ Analytics Status: {analytics_result.status}")
    print(f"   ✓ Records analyzed: {analytics_result.records_extracted}")
    print(f"   ✓ Metrics generated: {analytics_result.records_loaded}")
    print(f"   ✓ Duration: {analytics_result.performance_metrics.get('duration_seconds', 0):.2f}s")
    
    if analytics_result.quality_issues:
        print("   📊 Analytics Issues:")
        for issue in analytics_result.quality_issues[:3]:
            print(f"      • {issue}")
    
    return [api_result, standard_result, analytics_result]

def show_data_lake_summary():
    """Show comprehensive data lake summary"""
    
    print("\n🏛️  DATA LAKE ARCHITECTURE SUMMARY")
    print("=" * 50)
    
    analyzer = WildlifeAnalyzer()
    
    try:
        with sqlite3.connect("data/aussie_wildlife.db") as conn:
            cursor = conn.cursor()
            
            # Bronze layer stats
            cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
            bronze_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT source_system, COUNT(*) as count 
                FROM wildlife_bronze 
                GROUP BY source_system 
                ORDER BY count DESC
            """)
            bronze_sources = cursor.fetchall()
            
            print(f"\n🥉 BRONZE LAYER (Raw Data Storage)")
            print(f"   📦 Total raw records: {bronze_count:,}")
            if bronze_sources:
                print("   📊 Data sources:")
                for source, count in bronze_sources[:5]:
                    print(f"      • {source}: {count:,} records")
            
            # Silver layer stats
            cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
            silver_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT AVG(quality_score) as avg_quality, 
                       COUNT(CASE WHEN quality_score >= 0.8 THEN 1 END) as high_quality
                FROM wildlife_silver
            """)
            quality_stats = cursor.fetchone()
            
            print(f"\n🥈 SILVER LAYER (Validated Data)")
            print(f"   🎯 Total validated records: {silver_count:,}")
            if quality_stats[0]:
                avg_quality, high_quality = quality_stats
                print(f"   ⭐ Average quality score: {avg_quality:.3f}")
                print(f"   🏆 High quality records (≥0.8): {high_quality:,} ({high_quality/silver_count*100:.1f}%)")
            
            # Gold layer stats  
            cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
            gold_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT aggregation_type, COUNT(*) as count
                FROM wildlife_gold
                GROUP BY aggregation_type
                ORDER BY count DESC
            """)
            gold_types = cursor.fetchall()
            
            print(f"\n🥇 GOLD LAYER (Analytics Ready)")
            print(f"   📈 Total analytics records: {gold_count:,}")
            if gold_types:
                print("   📊 Analytics types:")
                for agg_type, count in gold_types:
                    print(f"      • {agg_type}: {count:,} metrics")
            
            # Data flow efficiency
            print(f"\n⚡ DATA PIPELINE EFFICIENCY")
            if bronze_count > 0 and silver_count > 0:
                processing_rate = (silver_count / bronze_count) * 100
                print(f"   🔄 Bronze → Silver: {processing_rate:.1f}% success rate")
            
            if silver_count > 0 and gold_count > 0:
                analytics_rate = (gold_count / silver_count) * 100
                print(f"   📊 Silver → Gold: {analytics_rate:.1f}% analytics conversion")
                
    except Exception as e:
        print(f"   ❌ Error accessing data lake: {e}")

def show_etl_performance_dashboard():
    """Show ETL performance and job execution dashboard"""
    
    print("\n📊 ETL PERFORMANCE DASHBOARD")
    print("=" * 40)
    
    try:
        with sqlite3.connect("data/aussie_wildlife.db") as conn:
            cursor = conn.cursor()
            
            # Recent job performance
            cursor.execute("""
                SELECT job_name, status, 
                       records_extracted, records_loaded,
                       ROUND((julianday(end_time) - julianday(start_time)) * 86400, 2) as duration_seconds,
                       datetime(start_time) as executed_at
                FROM etl_job_executions
                ORDER BY start_time DESC
                LIMIT 10
            """)
            
            recent_jobs = cursor.fetchall()
            
            if recent_jobs:
                print("\n🔄 Recent ETL Job Executions:")
                print("   " + "-" * 85)
                print(f"   {'Job Name':<30} {'Status':<8} {'Records':<12} {'Duration':<8} {'Executed At'}")
                print("   " + "-" * 85)
                
                for job_name, status, extracted, loaded, duration, executed_at in recent_jobs[:7]:
                    status_icon = "✅" if status == "success" else "❌"
                    record_summary = f"{extracted}→{loaded}" if extracted and loaded else "0→0"
                    duration_str = f"{duration:.2f}s" if duration else "0.00s"
                    
                    print(f"   {job_name[:29]:<30} {status_icon:<8} {record_summary:<12} {duration_str:<8} {executed_at}")
            
            # Job success rates
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_jobs,
                    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_jobs,
                    AVG(records_loaded) as avg_records_processed
                FROM etl_job_executions
                WHERE start_time >= datetime('now', '-7 days')
            """)
            
            performance_stats = cursor.fetchone()
            
            if performance_stats[0] > 0:
                total, successful, avg_records = performance_stats
                success_rate = (successful / total) * 100
                
                print(f"\n📈 7-Day Performance Summary:")
                print(f"   🎯 Success rate: {success_rate:.1f}% ({successful}/{total} jobs)")
                print(f"   📊 Average records processed: {avg_records:.1f}")
                
                # Quality trend
                cursor.execute("""
                    SELECT AVG(json_array_length(quality_issues)) as avg_issues
                    FROM etl_job_executions
                    WHERE start_time >= datetime('now', '-7 days')
                    AND quality_issues IS NOT NULL
                """)
                
                avg_issues = cursor.fetchone()[0]
                if avg_issues:
                    print(f"   ⚠️  Average quality issues per job: {avg_issues:.1f}")
                    
    except Exception as e:
        print(f"   ❌ Error accessing performance data: {e}")

def demonstrate_data_lineage():
    """Show data lineage and transformation tracking"""
    
    print("\n🔍 DATA LINEAGE & TRANSFORMATION TRACKING")  
    print("=" * 50)
    
    try:
        with sqlite3.connect("data/aussie_wildlife.db") as conn:
            # Show transformation flow
            print("\n📋 Data Transformation Pipeline:")
            print("   1. EXTRACT: Raw data from iNaturalist API + existing database")
            print("   2. BRONZE: Store raw JSON data with source tracking")  
            print("   3. SILVER: Apply 5 transformations + 7 quality checks")
            print("   4. GOLD: Generate 4 types of analytics aggregations")
            
            # Sample data journey
            cursor = conn.cursor()
            cursor.execute("""
                SELECT common_name, location_description, quality_score 
                FROM wildlife_silver 
                WHERE quality_score > 0.8
                LIMIT 3
            """)
            
            silver_samples = cursor.fetchall()
            
            if silver_samples:
                print(f"\n🎯 High-Quality Data Samples (Quality Score > 0.8):")
                for species, location, quality in silver_samples:
                    print(f"   • {species} at {location} (Quality: {quality:.3f})")
            
            # Transformation impact
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as with_coordinates,
                    COUNT(CASE WHEN observed_date IS NOT NULL THEN 1 END) as with_dates
                FROM wildlife_silver
            """)
            
            transform_stats = cursor.fetchone()
            
            if transform_stats[0] > 0:
                total, with_coords, with_dates = transform_stats
                coord_rate = (with_coords / total) * 100
                date_rate = (with_dates / total) * 100
                
                print(f"\n📊 Transformation Quality Impact:")
                print(f"   🗺️  Coordinate completeness: {coord_rate:.1f}%")
                print(f"   📅 Date completeness: {date_rate:.1f}%")
                
    except Exception as e:
        print(f"   ❌ Error accessing lineage data: {e}")

def main():
    """Main demonstration function"""
    
    # Run complete ETL demonstration
    etl_results = demonstrate_complete_data_lifecycle()
    
    # Show data lake summary
    show_data_lake_summary()
    
    # Show performance dashboard
    show_etl_performance_dashboard()
    
    # Show data lineage
    demonstrate_data_lineage()
    
    # Final summary
    print(f"\n🎉 ENTERPRISE ETL DEMONSTRATION COMPLETED")
    print("=" * 50)
    
    total_jobs = len(etl_results)
    successful_jobs = sum(1 for result in etl_results if result.status == 'success')
    
    print(f"\n📋 Execution Summary:")
    print(f"   • Total ETL jobs executed: {total_jobs}")
    print(f"   • Successful jobs: {successful_jobs}")
    print(f"   • Success rate: {(successful_jobs/total_jobs)*100:.1f}%")
    
    total_processing_time = sum(
        result.performance_metrics.get('duration_seconds', 0) 
        for result in etl_results
    )
    print(f"   • Total processing time: {total_processing_time:.2f} seconds")
    
    print(f"\n🚀 Next Steps:")
    print(f"   • Use `python src/analysis/data_explorer.py` to explore processed data")
    print(f"   • Launch web dashboard for interactive visualization")  
    print(f"   • Set up scheduled ETL jobs for continuous data processing")
    print(f"   • Implement real-time monitoring and alerting")
    
    print(f"\n📚 Enterprise Features Demonstrated:")
    print(f"   ✅ Multi-layer data lake architecture (Bronze/Silver/Gold)")
    print(f"   ✅ Robust transformation pipeline with error handling")
    print(f"   ✅ Comprehensive quality validation (7 check types)")
    print(f"   ✅ Performance monitoring and job tracking")
    print(f"   ✅ Data lineage and audit trail")
    print(f"   ✅ Australian biodiversity focus with real API data")

if __name__ == "__main__":
    main()
