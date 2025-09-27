#!/usr/bin/env python3
"""
Wildlife Data Collection Script with Lifecycle Management
=========================================================
Enterprise-grade data collection for Australian wildlife observations.

Features complete data lifecycle management:
- Data ingestion with validation and standardization
- Data quality assurance and monitoring
- Application of data standards and schema enforcement
- Quality-assured data delivery

Usage:
    python collect_wildlife_data.py
"""

import sys
import os
import requests
from datetime import datetime

# Add the src directory to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_lifecycle_manager import DataIngestionManager, DataDeliveryManager
from collectors.inaturalist_collector import iNaturalistCollector

def collect_and_store_data():
    """
    Main function to collect wildlife data using enterprise data lifecycle management
    Demonstrates complete data governance from ingestion to delivery
    """
    
    print("AUSTRALIAN WILDLIFE DATA COLLECTION WITH LIFECYCLE MANAGEMENT")
    print("=" * 65)
    print("Enterprise-grade data management across the complete lifecycle:")
    print("• Data ingestion with validation")
    print("• Quality assurance and monitoring")  
    print("• Data standards enforcement")
    print("• Quality-assured delivery")
    print()
    # Initialize enterprise data lifecycle management
    ingestion_manager = DataIngestionManager()
    delivery_manager = DataDeliveryManager()
    
    print("PHASE 1: DATA INGESTION")
    print("-" * 25)
    
    # Collect raw data from iNaturalist API  
    all_records = []
    
    # Collect koala data
    print("Collecting koala observations from iNaturalist API...")
    koala_records = collect_species_from_api('Phascolarctos cinereus', 25)
    if koala_records:
        all_records.extend(koala_records)
        print(f"Retrieved {len(koala_records)} koala records")
    
    # Collect kangaroo data
    print("Collecting kangaroo observations from iNaturalist API...")
    kangaroo_records = collect_species_from_api('Macropus', 20)
    if kangaroo_records:
        all_records.extend(kangaroo_records)
        print(f"Retrieved {len(kangaroo_records)} kangaroo records")
    
    if not all_records:
        print("No data retrieved from API. Check your internet connection.")
        return
    
    print(f"\nTotal records collected from API: {len(all_records)}")
    
    print(f"\nPHASE 2: DATA LIFECYCLE MANAGEMENT")
    print("-" * 35)
    
    # Process data through enterprise lifecycle management
    ingestion_result = ingestion_manager.ingest_batch(all_records, 'iNaturalist')
    
    print(f"Ingestion Results:")
    print(f"  Batch ID: {ingestion_result['batch_id']}")
    print(f"  Records Received: {ingestion_result['records_received']}")
    print(f"  Records Processed: {ingestion_result['records_processed']}")
    print(f"  Records Accepted: {ingestion_result['records_accepted']}")
    print(f"  Records Rejected: {ingestion_result['records_rejected']}")
    print(f"  Processing Time: {ingestion_result['processing_duration_seconds']:.2f} seconds")
    
    # Show quality issues if any
    quality_issues = [qr for qr in ingestion_result['quality_results'] if not qr.passed]
    if quality_issues:
        print(f"\nData Quality Issues Found: {len(quality_issues)}")
        error_issues = [qi for qi in quality_issues if qi.severity == 'error']
        warning_issues = [qi for qi in quality_issues if qi.severity == 'warning']
        
        if error_issues:
            print(f"  Errors: {len(error_issues)} (records rejected)")
        if warning_issues:
            print(f"  Warnings: {len(warning_issues)} (records accepted with notes)")
    
    print(f"\nPHASE 3: QUALITY-ASSURED DATA DELIVERY")
    print("-" * 40)
    
    # Demonstrate quality-assured data delivery
    quality_dataset = delivery_manager.get_quality_assured_dataset(quality_level="standard")
    
    print(f"Quality-Assured Dataset Generated:")
    print(f"  Total Records: {quality_dataset['metadata']['total_records']}")
    print(f"  Quality Level: {quality_dataset['metadata']['quality_level']}")
    print(f"  Data Standards Version: {quality_dataset['metadata']['data_standards_version']}")
    
    # Show data completeness metrics
    completeness = quality_dataset['metadata']['quality_metrics']['data_completeness']
    if completeness:
        print(f"\nData Completeness:")
        for field, percentage in completeness.items():
            print(f"  {field}: {percentage:.1f}%")
    
    # Show sample quality-assured records
    if quality_dataset['records']:
        print(f"\nSample Quality-Assured Records:")
        for i, record in enumerate(quality_dataset['records'][:3], 1):
            print(f"  {i}. {record['common_name']} at {record['location_description']}")
            print(f"     Date: {record['observed_date']} | Observer: {record['observer_name']}")

def collect_species_from_api(taxon_name: str, per_page: int = 20) -> list:
    """
    Collect species observations from iNaturalist API
    
    Args:
        taxon_name: Scientific name of the species/genus to collect
        per_page: Number of records to retrieve
    
    Returns:
        List of observation records from the API
    """
    url = "https://api.inaturalist.org/v1/observations"
    
    params = {
        'taxon_name': taxon_name,
        'place_id': '6744',  # Australia
        'per_page': per_page,
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('results', [])
        else:
            print(f"API request failed with status: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        print(f"Network error: {e}")
        return []
    print("Run 'python explore_data.py' to analyze your data!")

if __name__ == "__main__":
    try:
        collect_and_store_data()
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"Error during collection: {e}")
        print("Check your internet connection and try again.")
