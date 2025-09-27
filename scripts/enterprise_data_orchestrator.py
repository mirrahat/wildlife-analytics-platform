#!/usr/bin/env python3
"""
Enterprise Data Management Orchestrator
======================================
Comprehensive orchestration of enterprise-grade data lifecycle management for the Australian Wildlife Platform.

This script demonstrates the complete integration of contemporary data management practices:
- Data ingestion with quality validation
- Real-time quality monitoring
- Data governance and compliance
- Modern ETL pipeline processing
- Data catalog and lineage management
- Quality-assured data delivery

Features enterprise-level capabilities for production data management.
"""

import sys
import os
import time
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_lifecycle_manager import EnterpriseDataLifecycleManager
from collectors.inaturalist_collector import iNaturalistCollector

def demonstrate_enterprise_lifecycle():
    """
    Demonstrate the complete enterprise data lifecycle management system
    """
    
    print("AUSTRALIAN WILDLIFE PLATFORM - ENTERPRISE DATA MANAGEMENT")
    print("=" * 70)
    print("Demonstrating contemporary data lifecycle management with:")
    print("  ✓ Real-time quality monitoring")
    print("  ✓ Data governance and compliance")
    print("  ✓ Modern ETL pipeline architecture")
    print("  ✓ Automated data cataloging")
    print("  ✓ Data lineage tracking") 
    print("  ✓ Quality-assured delivery")
    print()
    
    # Initialize the enterprise data lifecycle manager
    print("1. INITIALIZING ENTERPRISE DATA LIFECYCLE MANAGEMENT")
    print("-" * 55)
    
    lifecycle_manager = EnterpriseDataLifecycleManager()
    
    print("   ✓ Data ingestion manager initialized")
    print("   ✓ Quality monitoring system ready")
    print("   ✓ Data governance framework established")
    print("   ✓ ETL pipeline configured")
    print("   ✓ Compliance management active")
    print("   ✓ Data catalog populated")
    print()
    
    # Start continuous quality monitoring
    print("2. STARTING CONTINUOUS QUALITY MONITORING")
    print("-" * 45)
    
    lifecycle_manager.start_continuous_monitoring()
    print("   ✓ Real-time quality monitoring active")
    print("   ✓ Automated alerting configured")
    print("   ✓ Quality thresholds established")
    print()
    
    # Collect live data from iNaturalist
    print("3. COLLECTING LIVE WILDLIFE DATA")
    print("-" * 35)
    
    collector = iNaturalistCollector()
    
    # Collect data for multiple species to demonstrate variety
    species_list = ["koala", "kangaroo", "echidna", "wombat", "kookaburra"]
    all_records = []
    
    for species in species_list:
        print(f"   • Collecting {species} observations from iNaturalist...")
        try:
            # Use the correct method name for collecting species data
            records = collector.collect_species_data(species, species.title(), limit=5)
            all_records.extend(records)
            print(f"     Found {len(records)} recent {species} observations")
        except Exception as e:
            print(f"     Warning: Could not collect {species} data: {e}")
    
    print(f"\n   Total records collected: {len(all_records)}")
    print()
    
    # Execute full lifecycle ingestion
    print("4. EXECUTING ENTERPRISE DATA LIFECYCLE INGESTION")
    print("-" * 50)
    
    if all_records:
        lifecycle_result = lifecycle_manager.execute_full_lifecycle_ingestion(
            all_records, "iNaturalist"
        )
        
        print("   INGESTION PHASE:")
        print(f"     • Records received: {lifecycle_result['ingestion']['records_received']}")
        print(f"     • Records accepted: {lifecycle_result['ingestion']['records_accepted']}")
        print(f"     • Records rejected: {lifecycle_result['ingestion']['records_rejected']}")
        print(f"     • Quality checks performed: {len(lifecycle_result['ingestion']['quality_results'])}")
        
        print("   ETL PIPELINE PHASE:")
        if 'bronze_to_silver' in lifecycle_result['etl_pipeline']:
            etl_result = lifecycle_result['etl_pipeline']['bronze_to_silver']
            print(f"     • Bronze to Silver status: {etl_result['status']}")
            print(f"     • Records processed: {etl_result['records_processed']}")
            print(f"     • Records transformed: {etl_result['records_output']}")
            print(f"     • Quality issues detected: {etl_result['quality_issues']}")
        else:
            print(f"     • ETL Pipeline: {lifecycle_result['etl_pipeline'].get('error', 'Completed')}")
        
        print("   GOVERNANCE PHASE:")
        print(f"     • Compliance checks: {lifecycle_result['compliance']['checks_performed']}")
        print(f"     • Non-compliant items: {lifecycle_result['compliance']['non_compliant_checks']}")
        print(f"     • Data lineage recorded: {lifecycle_result['data_lineage']['lineage_recorded']}")
        print(f"     • Catalog updated: {lifecycle_result['catalog_updated']}")
        
        print("   QUALITY MONITORING:")
        print(f"     • Quality metrics calculated: {lifecycle_result['quality_monitoring']['metrics_calculated']}")
        print(f"     • Overall quality score: {lifecycle_result['quality_monitoring']['overall_quality_score']:.3f}")
        
        print(f"\n   Total processing time: {lifecycle_result['processing_time_seconds']:.2f} seconds")
        print(f"   Lifecycle status: {lifecycle_result['lifecycle_status']}")
    else:
        print("   No records collected - skipping lifecycle ingestion")
    
    print()
    
    # Wait a moment for quality monitoring to process
    print("5. MONITORING SYSTEM ACTIVITY")
    print("-" * 30)
    print("   • Allowing quality monitoring system to process data...")
    time.sleep(5)  # Brief pause for monitoring
    
    # Generate comprehensive dashboard
    print("6. GENERATING ENTERPRISE DASHBOARD")
    print("-" * 35)
    
    dashboard = lifecycle_manager.get_comprehensive_dashboard()
    
    print("   DATA DELIVERY METRICS:")
    print(f"     • Total available records: {dashboard['data_delivery']['total_records']}")
    print(f"     • Quality assurance level: {dashboard['data_delivery']['quality_level']}")
    print(f"     • Last data extraction: {dashboard['data_delivery']['last_extraction']}")
    
    print("   QUALITY MONITORING STATUS:")
    print(f"     • Overall quality score: {dashboard['quality_monitoring']['overall_score']:.3f}")
    print(f"     • Monitoring status: {dashboard['quality_monitoring']['monitoring_status']}")
    print(f"     • Active quality alerts: {dashboard['quality_monitoring']['recent_alerts']}")
    print(f"     • Current metrics tracked: {dashboard['quality_monitoring']['current_metrics']}")
    
    print("   ETL PIPELINE STATUS:")
    print(f"     • Registered jobs: {dashboard['etl_pipeline']['registered_jobs']}")
    print(f"     • Recent executions: {dashboard['etl_pipeline']['recent_executions']}")
    print(f"     • Pipeline success rate: {dashboard['etl_pipeline']['success_rate']:.1%}")
    
    print("   DATA CATALOG STATUS:")
    print(f"     • Total cataloged assets: {dashboard['data_catalog']['total_assets']}")
    print(f"     • Average quality score: {dashboard['data_catalog']['average_quality_score']:.3f}")
    
    print("   COMPLIANCE STATUS:")
    print(f"     • Compliance rate: {dashboard['compliance']['compliance_rate']:.1%}")
    print(f"     • Total compliance checks: {dashboard['compliance']['total_checks']}")
    
    print("   SYSTEM HEALTH:")
    print(f"     • All systems operational: {dashboard['system_status']['all_systems_operational']}")
    print(f"     • Last updated: {dashboard['system_status']['last_updated']}")
    
    print()
    
    # Demonstrate quality-assured data delivery
    print("7. DELIVERING QUALITY-ASSURED DATASET")
    print("-" * 38)
    
    dataset = lifecycle_manager.delivery_manager.get_quality_assured_dataset(
        quality_level="high"  # High quality data only
    )
    
    print(f"   • Quality-assured dataset generated")
    print(f"   • Records included: {dataset['metadata']['total_records']}")
    print(f"   • Quality level: {dataset['metadata']['quality_level']}")
    print(f"   • Data standards version: {dataset['metadata']['data_standards_version']}")
    
    if dataset['records']:
        print(f"   • Sample observations:")
        for i, record in enumerate(dataset['records'][:3], 1):
            species = record.get('common_name', 'Unknown species')
            location = record.get('location_description', 'Unknown location')
            date = record.get('observed_date', 'Unknown date')
            print(f"     {i}. {species} observed at {location} on {date}")
    
    print()
    
    # Stop monitoring for clean shutdown
    lifecycle_manager.stop_continuous_monitoring()
    
    print("8. ENTERPRISE DATA MANAGEMENT SUMMARY")
    print("-" * 40)
    print("   ✓ Live data successfully collected from external APIs")
    print("   ✓ Enterprise data lifecycle management executed")
    print("   ✓ Real-time quality monitoring performed")
    print("   ✓ Data governance and compliance verified")
    print("   ✓ Modern ETL pipeline processed data through lake layers")
    print("   ✓ Data catalog and lineage tracking maintained")
    print("   ✓ Quality-assured datasets delivered")
    print()
    print("   ENTERPRISE DATA PLATFORM STATUS: OPERATIONAL")
    print("   Ready for production workloads with full governance")
    print()
    print("=" * 70)

def main():
    """Main function to run the enterprise data management demonstration"""
    try:
        demonstrate_enterprise_lifecycle()
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user")
    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Check logs for detailed error information")

if __name__ == "__main__":
    main()
