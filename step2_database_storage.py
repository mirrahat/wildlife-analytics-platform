#!/usr/bin/env python3
"""
🦘 Step 2: Add Simple Database Storage

Now that we can collect live Australian wildlife data, 
let's store it in a simple database so we can:
- Keep track of sightings over time
- Avoid duplicates
- Query the data later
- Build up a personal research database

We'll use SQLite (comes with Python) - no complex setup needed!
"""

import sqlite3
import requests
import json
from datetime import datetime
import os

class AussieWildlifeDB:
    """
    A simple database for storing Australian wildlife sightings.
    Written like a human would write it - clear and understandable.
    """
    
    def __init__(self, db_name="aussie_wildlife.db"):
        """Set up our wildlife database"""
        self.db_name = db_name
        self.setup_database()
    
    def setup_database(self):
        """Create the database tables if they don't exist"""
        print("🗄️  Setting up wildlife database...")
        
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            # Create a table for wildlife sightings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_sightings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species_name TEXT NOT NULL,
                    common_name TEXT,
                    location TEXT,
                    latitude REAL,
                    longitude REAL,
                    observed_date TEXT,
                    observer TEXT,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    inaturalist_id INTEGER UNIQUE
                )
            ''')
            
            conn.commit()
            print("✅ Database ready!")
    
    def save_koala_sighting(self, sighting_data):
        """Save a koala sighting to the database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO wildlife_sightings 
                    (species_name, common_name, location, latitude, longitude, 
                     observed_date, observer, source, inaturalist_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    'Phascolarctos cinereus',  # Scientific name
                    'Koala',  # Common name
                    sighting_data.get('place_guess', 'Unknown'),
                    sighting_data.get('location', [None, None])[1] if sighting_data.get('location') else None,  # lat
                    sighting_data.get('location', [None, None])[0] if sighting_data.get('location') else None,  # lng
                    sighting_data.get('observed_on'),
                    sighting_data.get('user', {}).get('login', 'Anonymous'),
                    'iNaturalist',
                    sighting_data.get('id')
                ))
                return True
            except sqlite3.Error as e:
                print(f"⚠️  Database error: {e}")
                return False
    
    def save_kangaroo_sighting(self, sighting_data):
        """Save a kangaroo/wallaby sighting to the database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO wildlife_sightings 
                    (species_name, common_name, location, latitude, longitude, 
                     observed_date, observer, source, inaturalist_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    sighting_data.get('taxon', {}).get('name', 'Macropus species'),
                    sighting_data.get('species_guess', 'Kangaroo/Wallaby'),
                    sighting_data.get('place_guess', 'Unknown'),
                    sighting_data.get('location', [None, None])[1] if sighting_data.get('location') else None,
                    sighting_data.get('location', [None, None])[0] if sighting_data.get('location') else None,
                    sighting_data.get('observed_on'),
                    sighting_data.get('user', {}).get('login', 'Anonymous'),
                    'iNaturalist',
                    sighting_data.get('id')
                ))
                return True
            except sqlite3.Error as e:
                print(f"⚠️  Database error: {e}")
                return False
    
    def get_recent_sightings(self, days=7):
        """Get recent wildlife sightings from our database"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT common_name, location, observed_date, observer
                FROM wildlife_sightings 
                WHERE DATE(observed_date) >= DATE('now', '-{} days')
                ORDER BY observed_date DESC
            '''.format(days))
            
            return cursor.fetchall()
    
    def get_species_count(self):
        """Count how many different species we've recorded"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT common_name, COUNT(*) as sightings
                FROM wildlife_sightings 
                GROUP BY common_name
                ORDER BY sightings DESC
            ''')
            
            return cursor.fetchall()

def collect_and_store_data():
    """
    Collect live Australian wildlife data and store it in our database.
    This combines our Step 1 (data collection) with Step 2 (database storage).
    """
    print("🦘 STEP 2: COLLECTING AND STORING AUSTRALIAN WILDLIFE DATA")
    print("=" * 60)
    
    # Initialize our database
    db = AussieWildlifeDB()
    
    # Get koala data from iNaturalist (same as Step 1)
    print("🐨 Collecting fresh koala data...")
    url = "https://api.inaturalist.org/v1/observations"
    params = {
        'taxon_name': 'Phascolarctos cinereus',
        'place_id': '6744',  # Australia
        'per_page': 20,  # Get more this time
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    koala_count = 0
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            koala_sightings = data.get('results', [])
            
            # Save each sighting to our database
            for sighting in koala_sightings:
                if db.save_koala_sighting(sighting):
                    koala_count += 1
            
            print(f"✅ Saved {koala_count} koala sightings to database")
        else:
            print(f"❌ Failed to get koala data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error collecting koala data: {e}")
    
    # Get kangaroo data
    print("🦘 Collecting fresh kangaroo data...")
    params = {
        'taxon_name': 'Macropus',
        'place_id': '6744',  # Australia
        'per_page': 15,
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    kangaroo_count = 0
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            kangaroo_sightings = data.get('results', [])
            
            # Save each sighting to our database
            for sighting in kangaroo_sightings:
                if db.save_kangaroo_sighting(sighting):
                    kangaroo_count += 1
            
            print(f"✅ Saved {kangaroo_count} kangaroo sightings to database")
        else:
            print(f"❌ Failed to get kangaroo data: {response.status_code}")
    except Exception as e:
        print(f"❌ Error collecting kangaroo data: {e}")
    
    # Show what we've collected
    print("\n📊 DATABASE SUMMARY:")
    print("-" * 30)
    
    # Show species counts
    species_counts = db.get_species_count()
    for species, count in species_counts:
        print(f"  🔢 {species}: {count} sightings")
    
    # Show recent sightings
    print(f"\n📅 RECENT SIGHTINGS (last 7 days):")
    recent = db.get_recent_sightings(7)
    for i, (species, location, date, observer) in enumerate(recent[:5], 1):
        print(f"  {i}. {species} in {location}")
        print(f"     📅 {date} by {observer}")
    
    if len(recent) > 5:
        print(f"     ... and {len(recent) - 5} more sightings")
    
    print(f"\n🎉 SUCCESS! You now have a personal Australian wildlife database!")
    print(f"📁 Database file: {db.db_name}")
    print(f"🔄 Next step: We'll add data analysis and visualization...")

if __name__ == "__main__":
    collect_and_store_data()
