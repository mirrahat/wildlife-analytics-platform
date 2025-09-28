#!/usr/bin/env python3
"""
Step 2: Australian Wildlife Database

Now we'll add a simple database to store the live wildlife data we collect.
This way we can:
- Keep track of koala sightings over time
- See patterns in where animals are spotted
- Build up our own research database
- Query the data later for analysis

We're using SQLite because it's simple and comes built into Python!
"""

import sqlite3
import requests
import json
from datetime import datetime
import os

class AustralianWildlifeDB:
    """
    A simple database class for storing Australian wildlife sightings.
    Written in plain English so you can understand exactly what's happening.
    """
    
    def __init__(self, database_name="aussie_wildlife.db"):
        """Set up our wildlife database"""
        self.db_name = database_name
        print(f"Setting up Australian wildlife database: {database_name}")
        self.create_tables()
    
    def create_tables(self):
        """Create the database tables where we'll store wildlife sightings"""
        
        # Connect to the database (creates it if it doesn't exist)
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            # Create a table for wildlife sightings
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_sightings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    common_name TEXT NOT NULL,
                    scientific_name TEXT,
                    location_description TEXT,
                    latitude REAL,
                    longitude REAL,
                    observed_date TEXT,
                    observer_name TEXT,
                    photo_url TEXT,
                    data_source TEXT,
                    external_id INTEGER UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create an index to make searches faster
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_common_name 
                ON wildlife_sightings(common_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_observed_date 
                ON wildlife_sightings(observed_date)
            ''')
            
            connection.commit()
            print("Database tables created successfully!")
    
    def save_wildlife_sighting(self, sighting_data):
        """
        Save a wildlife sighting to our database.
        This prevents duplicates by using the external_id.
        """
        
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            try:
                # Extract the data we need from the API response
                common_name = sighting_data.get('species_guess', 'Unknown species')
                scientific_name = ''
                if sighting_data.get('taxon'):
                    scientific_name = sighting_data['taxon'].get('name', '')
                
                location = sighting_data.get('place_guess', 'Unknown location')
                
                # Get coordinates if available
                latitude = None
                longitude = None
                if sighting_data.get('geojson') and sighting_data['geojson'].get('coordinates'):
                    coords = sighting_data['geojson']['coordinates']
                    longitude = coords[0]  # Note: GeoJSON is [lng, lat]
                    latitude = coords[1]
                
                observed_date = sighting_data.get('observed_on', '')
                observer = sighting_data.get('user', {}).get('login', 'Anonymous')
                
                # Get photo URL if available
                photo_url = ''
                if sighting_data.get('photos') and len(sighting_data['photos']) > 0:
                    photo_url = sighting_data['photos'][0].get('url', '')
                
                external_id = sighting_data.get('id')
                
                # Insert into database (OR IGNORE prevents duplicates)
                cursor.execute('''
                    INSERT OR IGNORE INTO wildlife_sightings 
                    (common_name, scientific_name, location_description, latitude, longitude,
                     observed_date, observer_name, photo_url, data_source, external_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    common_name,
                    scientific_name,
                    location,
                    latitude,
                    longitude,
                    observed_date,
                    observer,
                    photo_url,
                    'iNaturalist',
                    external_id
                ))
                
                # Check if we actually inserted something new
                if cursor.rowcount > 0:
                    return True
                else:
                    return False  # Already existed
                    
            except sqlite3.Error as e:
                print(f"WARNING: Database error saving sighting: {e}")
                return False
    
    def get_recent_sightings(self, days=7, limit=10):
        """Get recent wildlife sightings from our database"""
        
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT common_name, location_description, observed_date, observer_name
                FROM wildlife_sightings 
                WHERE DATE(observed_date) >= DATE('now', '-{} days')
                ORDER BY observed_date DESC
                LIMIT ?
            '''.format(days), (limit,))
            
            return cursor.fetchall()
    
    def get_species_summary(self):
        """Get a summary of what species we've recorded"""
        
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT common_name, COUNT(*) as sighting_count
                FROM wildlife_sightings 
                WHERE common_name != 'Unknown species'
                GROUP BY common_name
                ORDER BY sighting_count DESC
            ''')
            
            return cursor.fetchall()
    
    def get_total_count(self):
        """Get total number of sightings in our database"""
        
        with sqlite3.connect(self.db_name) as connection:
            cursor = connection.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM wildlife_sightings')
            return cursor.fetchone()[0]

def collect_and_store_koala_data():
    """
    Collect fresh koala data from iNaturalist API and store it in our database
    """
    print("Collecting fresh koala data from Australia...")
    
    # Set up our database
    db = AustralianWildlifeDB()
    
    # Call the iNaturalist API for Australian koalas
    api_url = "https://api.inaturalist.org/v1/observations"
    
    params = {
        'taxon_name': 'Phascolarctos cinereus',  # Scientific name for koala
        'place_id': '6744',  # Australia's place ID
        'per_page': 20,  # Get 20 recent sightings
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    try:
        print("Making API call to iNaturalist...")
        response = requests.get(api_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            koala_sightings = data.get('results', [])
            
            print(f"Retrieved {len(koala_sightings)} koala sightings from API")
            
            # Save each sighting to our database
            new_sightings = 0
            for sighting in koala_sightings:
                if db.save_wildlife_sighting(sighting):
                    new_sightings += 1
            
            print(f"Saved {new_sightings} new koala sightings to database")
            
            return db
            
        else:
            print(f"ERROR: API request failed with status: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        print(f"ERROR: Network error: {e}")
        return None
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")
        return None

def collect_and_store_kangaroo_data(db):
    """
    Collect fresh kangaroo/wallaby data and add it to our database
    """
    print("Collecting fresh kangaroo data from Australia...")
    
    api_url = "https://api.inaturalist.org/v1/observations"
    
    params = {
        'taxon_name': 'Macropus',  # Kangaroo genus
        'place_id': '6744',  # Australia
        'per_page': 15,
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    try:
        response = requests.get(api_url, params=params, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            kangaroo_sightings = data.get('results', [])
            
            print(f"Retrieved {len(kangaroo_sightings)} kangaroo sightings from API")
            
            # Save each sighting to our database
            new_sightings = 0
            for sighting in kangaroo_sightings:
                if db.save_wildlife_sighting(sighting):
                    new_sightings += 1
            
            print(f"Saved {new_sightings} new kangaroo sightings to database")
            
        else:
            print(f"ERROR: API request failed with status: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"ERROR: Network error: {e}")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

def show_database_summary(db):
    """Show a summary of what's in our wildlife database"""
    
    print("\nAUSTRALIAN WILDLIFE DATABASE SUMMARY")
    print("=" * 45)
    
    # Total count
    total_sightings = db.get_total_count()
    print(f"Total sightings in database: {total_sightings}")
    
    # Species breakdown
    species_summary = db.get_species_summary()
    if species_summary:
        print(f"\nSpecies in our database:")
        for species, count in species_summary[:5]:  # Show top 5
            print(f"   - {species}: {count} sightings")
    
    # Recent sightings
    recent_sightings = db.get_recent_sightings(7, 5)
    if recent_sightings:
        print(f"\nRecent sightings (last 7 days):")
        for species, location, date, observer in recent_sightings:
            print(f"   - {species} in {location}")
            print(f"     Date: {date} by {observer}")
    
    print(f"\nDatabase file: {db.db_name}")

def main():
    """Main function - collect data and store it in our database"""
    
    print("STEP 2: AUSTRALIAN WILDLIFE DATABASE")
    print("=" * 45)
    print("Collecting live wildlife data and storing it in a database")
    print("This way we can build up our own research database over time!")
    print()
    
    # Step 1: Collect and store koala data
    db = collect_and_store_koala_data()
    
    if db:
        print()
        
        # Step 2: Collect and store kangaroo data
        collect_and_store_kangaroo_data(db)
        
        print()
        
        # Step 3: Show what we've collected
        show_database_summary(db)
        
        print()
        print("SUCCESS! You now have a personal Australian wildlife database!")
        print("Next step: We'll add data analysis and visualization...")
        print()
        print("NOTE: Try running this script multiple times to build up more data!")
    
    else:
        print("ERROR: Failed to set up database. Check your internet connection.")

if __name__ == "__main__":
    main()
