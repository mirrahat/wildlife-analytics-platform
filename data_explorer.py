#!/usr/bin/env python3
"""
Australian Wildlife Data Explorer
=================================
Interactive tool for exploring and analyzing stored wildlife data.

Browse your collected Australian wildlife observations:
- View species summaries and counts
- See recent sightings and locations  
- Track observation patterns over time
- Generate quick statistics and insights

Works with the database created by database_manager.py
"""

import sqlite3
from datetime import datetime

def explore_wildlife_database(db_name="aussie_wildlife.db"):
    """Explore the wildlife database in a user-friendly way"""
    
    print("AUSTRALIAN WILDLIFE DATABASE EXPLORER")
    print("=" * 45)
    
    try:
        with sqlite3.connect(db_name) as connection:
            cursor = connection.cursor()
            
            # Check if database exists and has data
            cursor.execute("SELECT COUNT(*) FROM wildlife_sightings")
            total_count = cursor.fetchone()[0]
            
            if total_count == 0:
                print("Your database is empty!")
                print("NOTE: Run 'python database_manager.py' first to collect some data")
                return
            
            print(f"Total wildlife sightings: {total_count}")
            print()
            
            # Show species breakdown
            print("SPECIES IN YOUR DATABASE:")
            print("-" * 30)
            cursor.execute('''
                SELECT common_name, COUNT(*) as count, 
                       MIN(observed_date) as first_seen,
                       MAX(observed_date) as last_seen
                FROM wildlife_sightings 
                WHERE common_name != 'Unknown species'
                GROUP BY common_name
                ORDER BY count DESC
            ''')
            
            species_data = cursor.fetchall()
            for species, count, first_seen, last_seen in species_data:
                print(f"   {species}: {count} sightings")
                print(f"      First seen: {first_seen}")
                print(f"      Last seen: {last_seen}")
                print()
            
            # Show recent sightings
            print("RECENT SIGHTINGS:")
            print("-" * 20)
            cursor.execute('''
                SELECT common_name, location_description, observed_date, observer_name
                FROM wildlife_sightings 
                ORDER BY observed_date DESC, created_at DESC
                LIMIT 10
            ''')
            
            recent_sightings = cursor.fetchall()
            for i, (species, location, date, observer) in enumerate(recent_sightings, 1):
                print(f"   {i}. {species}")
                print(f"      Location: {location}")
                print(f"      Date: {date} by {observer}")
                print()
            
            # Show locations
            print("TOP LOCATIONS:")
            print("-" * 17)
            cursor.execute('''
                SELECT location_description, COUNT(*) as sightings
                FROM wildlife_sightings 
                WHERE location_description != 'Unknown location'
                GROUP BY location_description
                ORDER BY sightings DESC
                LIMIT 5
            ''')
            
            locations = cursor.fetchall()
            for location, count in locations:
                print(f"   {location}: {count} sightings")
            
            print()
            print(f"Database file: {db_name}")
            print("NOTE: Run 'python database_manager.py' again to collect more data!")
            
    except sqlite3.Error as e:
        print(f"ERROR: Database error: {e}")
    except FileNotFoundError:
        print(f"ERROR: Database file '{db_name}' not found!")
        print("NOTE: Run 'python database_manager.py' first to create the database")

if __name__ == "__main__":
    explore_wildlife_database()
