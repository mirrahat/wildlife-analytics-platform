#!/usr/bin/env python3
"""
Wildlife Data Collection Script
==============================
Main script for collecting Australian wildlife data from iNaturalist.

This script:
- Collects fresh observations from iNaturalist API
- Stores data in the local SQLite database
- Provides summary statistics after collection
- Can be run regularly to build up historical data

Usage:
    python collect_wildlife_data.py
"""

import sys
import os

# Add the src directory to Python path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from collectors.inaturalist_collector import iNaturalistCollector
from database.wildlife_db import WildlifeDatabase

def collect_and_store_data():
    """Main function to collect wildlife data and store it in the database"""
    
    print("AUSTRALIAN WILDLIFE DATA COLLECTION")
    print("=" * 40)
    print("Collecting fresh wildlife observations from iNaturalist...")
    print()
    
    # Initialize our data collector and database
    collector = iNaturalistCollector()
    db = WildlifeDatabase()
    
    # Count how many new observations we save
    total_new = 0
    
    # Collect koala data
    print("Collecting koala observations...")
    koala_data = collector.collect_koala_data(25)
    
    koala_new = 0
    for observation in koala_data:
        if db.save_observation(observation):
            koala_new += 1
    
    print(f"Saved {koala_new} new koala observations")
    total_new += koala_new
    
    # Collect kangaroo/wallaby data
    print("\nCollecting kangaroo and wallaby observations...")
    kangaroo_data = collector.collect_kangaroo_data(20)
    
    kangaroo_new = 0
    for observation in kangaroo_data:
        if db.save_observation(observation):
            kangaroo_new += 1
    
    print(f"Saved {kangaroo_new} new kangaroo/wallaby observations")
    total_new += kangaroo_new
    
    # Show summary
    print(f"\n" + "=" * 40)
    print("COLLECTION SUMMARY")
    print("=" * 40)
    print(f"New observations added: {total_new}")
    print(f"Total observations in database: {db.get_total_count()}")
    
    # Show species breakdown
    species_summary = db.get_species_summary()
    if species_summary:
        print(f"\nCurrent species in database:")
        for species, count, first_seen, last_seen in species_summary:
            print(f"  {species}: {count} observations")
    
    # Show recent observations
    recent = db.get_recent_observations(days=1, limit=5)
    if recent:
        print(f"\nMost recent observations:")
        for species, location, date, observer in recent:
            print(f"  {species} in {location} on {date}")
    
    print(f"\nDatabase location: {db.db_path}")
    print("Run 'python explore_data.py' to analyze your data!")

if __name__ == "__main__":
    try:
        collect_and_store_data()
    except KeyboardInterrupt:
        print("\nCollection interrupted by user")
    except Exception as e:
        print(f"Error during collection: {e}")
        print("Check your internet connection and try again.")
