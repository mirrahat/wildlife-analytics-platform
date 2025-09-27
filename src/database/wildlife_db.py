#!/usr/bin/env python3
"""
Wildlife Database Manager
========================
Handles storage and retrieval of Australian wildlife observation data.

This module provides:
- SQLite database setup and management
- Data insertion with duplicate prevention
- Query methods for analysis
- Database maintenance utilities

Designed for the Australian Biodiversity Analytics Platform.
"""

import sqlite3
import os
from datetime import datetime

class WildlifeDatabase:
    """
    Manages the SQLite database for storing wildlife observations.
    Handles all database operations with proper error handling.
    """
    
    def __init__(self, db_path="data/aussie_wildlife.db"):
        """
        Initialize the database connection and create tables if needed.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        
        self.db_path = db_path
        self.setup_database()
    
    def setup_database(self):
        """Create database tables and indexes if they don't exist"""
        print(f"Setting up wildlife database: {self.db_path}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main observations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_observations (
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
                    quality_grade TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_common_name 
                ON wildlife_observations(common_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_observed_date 
                ON wildlife_observations(observed_date)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_location 
                ON wildlife_observations(latitude, longitude)
            ''')
            
            conn.commit()
            print("Database setup complete")
    
    def save_observation(self, observation_data):
        """
        Save a wildlife observation to the database.
        
        Args:
            observation_data (dict): Observation data from API
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            try:
                # Extract relevant fields from the observation data
                common_name = observation_data.get('species_guess', 'Unknown species')
                scientific_name = ''
                if observation_data.get('taxon'):
                    scientific_name = observation_data['taxon'].get('name', '')
                
                location = observation_data.get('place_guess', 'Unknown location')
                
                # Extract coordinates
                latitude = None
                longitude = None
                if observation_data.get('geojson') and observation_data['geojson'].get('coordinates'):
                    coords = observation_data['geojson']['coordinates']
                    longitude = coords[0]
                    latitude = coords[1]
                
                observed_date = observation_data.get('observed_on', '')
                observer = observation_data.get('user', {}).get('login', 'Anonymous')
                
                # Get photo URL if available
                photo_url = ''
                if observation_data.get('photos') and len(observation_data['photos']) > 0:
                    photo_url = observation_data['photos'][0].get('url', '')
                
                external_id = observation_data.get('id')
                quality_grade = observation_data.get('quality_grade', 'unknown')
                
                # Insert the observation (OR IGNORE prevents duplicates)
                cursor.execute('''
                    INSERT OR IGNORE INTO wildlife_observations 
                    (common_name, scientific_name, location_description, latitude, longitude,
                     observed_date, observer_name, photo_url, data_source, external_id, quality_grade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    common_name, scientific_name, location, latitude, longitude,
                    observed_date, observer, photo_url, 'iNaturalist', external_id, quality_grade
                ))
                
                return cursor.rowcount > 0
                
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                return False
    
    def get_species_summary(self):
        """Get a summary of species in the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT common_name, COUNT(*) as count,
                       MIN(observed_date) as first_seen,
                       MAX(observed_date) as last_seen
                FROM wildlife_observations 
                WHERE common_name != 'Unknown species'
                GROUP BY common_name
                ORDER BY count DESC
            ''')
            
            return cursor.fetchall()
    
    def get_recent_observations(self, days=7, limit=20):
        """Get recent observations from the database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT common_name, location_description, observed_date, observer_name
                FROM wildlife_observations 
                WHERE DATE(observed_date) >= DATE('now', '-{} days')
                ORDER BY observed_date DESC, created_at DESC
                LIMIT ?
            '''.format(days), (limit,))
            
            return cursor.fetchall()
    
    def get_location_summary(self, limit=10):
        """Get most active observation locations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT location_description, COUNT(*) as observation_count
                FROM wildlife_observations 
                WHERE location_description != 'Unknown location'
                GROUP BY location_description
                ORDER BY observation_count DESC
                LIMIT ?
            ''', (limit,))
            
            return cursor.fetchall()
    
    def get_total_count(self):
        """Get total number of observations in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM wildlife_observations')
            return cursor.fetchone()[0]
    
    def get_observations_by_species(self, species_name):
        """Get all observations for a specific species"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM wildlife_observations 
                WHERE common_name = ?
                ORDER BY observed_date DESC
            ''', (species_name,))
            
            return cursor.fetchall()

if __name__ == "__main__":
    # Example usage
    db = WildlifeDatabase()
    
    print("WILDLIFE DATABASE MANAGER")
    print("=" * 30)
    
    total = db.get_total_count()
    print(f"Total observations in database: {total}")
    
    if total > 0:
        species = db.get_species_summary()
        print(f"\nSpecies summary:")
        for name, count, first, last in species[:5]:
            print(f"  {name}: {count} observations (first: {first}, last: {last})")
    else:
        print("Database is empty. Run a data collection script first.")
