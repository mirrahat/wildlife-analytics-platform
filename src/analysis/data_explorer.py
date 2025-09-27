#!/usr/bin/env python3
"""
Wildlife Data Explorer
=====================
Interactive analysis and exploration of Australian wildlife observation data.

This module provides:
- Database exploration and summary statistics
- Species distribution analysis
- Temporal pattern analysis
- Location-based insights

For use with the Australian Biodiversity Analytics Platform.
"""

import sqlite3
from datetime import datetime, timedelta
import os

class WildlifeAnalyzer:
    """
    Analyzes wildlife observation data and generates insights.
    Provides various analytical views of the collected data.
    """
    
    def __init__(self, db_path="data/aussie_wildlife.db"):
        """
        Initialize the analyzer with database connection.
        
        Args:
            db_path (str): Path to the wildlife database
        """
        self.db_path = db_path
        
        if not os.path.exists(db_path):
            print(f"Database not found: {db_path}")
            print("Run the data collection script first.")
            return
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report of the database"""
        print("AUSTRALIAN WILDLIFE DATABASE REPORT")
        print("=" * 45)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Basic statistics
                cursor.execute("SELECT COUNT(*) FROM wildlife_observations")
                total_observations = cursor.fetchone()[0]
                
                if total_observations == 0:
                    print("No observations found in database.")
                    print("Run 'python scripts/collect_wildlife_data.py' to gather data.")
                    return
                
                print(f"Total observations: {total_observations}")
                
                # Species diversity
                cursor.execute('''
                    SELECT COUNT(DISTINCT common_name) 
                    FROM wildlife_observations 
                    WHERE common_name != 'Unknown species'
                ''')
                species_count = cursor.fetchone()[0]
                print(f"Unique species: {species_count}")
                
                # Date range
                cursor.execute('''
                    SELECT MIN(observed_date), MAX(observed_date) 
                    FROM wildlife_observations
                ''')
                date_range = cursor.fetchone()
                print(f"Date range: {date_range[0]} to {date_range[1]}")
                
                print("\n" + "=" * 45)
                
                # Species breakdown
                self._show_species_breakdown(cursor)
                
                # Recent activity
                self._show_recent_activity(cursor)
                
                # Location insights
                self._show_location_insights(cursor)
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    def _show_species_breakdown(self, cursor):
        """Show detailed species breakdown"""
        print("\nSPECIES BREAKDOWN:")
        print("-" * 20)
        
        cursor.execute('''
            SELECT common_name, COUNT(*) as count,
                   MIN(observed_date) as first_seen,
                   MAX(observed_date) as last_seen
            FROM wildlife_observations 
            WHERE common_name != 'Unknown species'
            GROUP BY common_name
            ORDER BY count DESC
        ''')
        
        species_data = cursor.fetchall()
        
        for species, count, first_seen, last_seen in species_data:
            print(f"\n{species}: {count} observations")
            print(f"  First recorded: {first_seen}")
            print(f"  Last recorded: {last_seen}")
            
            # Show recent locations for this species
            cursor.execute('''
                SELECT DISTINCT location_description 
                FROM wildlife_observations 
                WHERE common_name = ? AND location_description != 'Unknown location'
                ORDER BY observed_date DESC
                LIMIT 3
            ''', (species,))
            
            locations = cursor.fetchall()
            if locations:
                print(f"  Recent locations: {', '.join([loc[0] for loc in locations])}")
    
    def _show_recent_activity(self, cursor):
        """Show recent observation activity"""
        print(f"\nRECENT OBSERVATIONS (last 10):")
        print("-" * 30)
        
        cursor.execute('''
            SELECT common_name, location_description, observed_date, observer_name
            FROM wildlife_observations 
            ORDER BY observed_date DESC, created_at DESC
            LIMIT 10
        ''')
        
        recent_obs = cursor.fetchall()
        
        for i, (species, location, date, observer) in enumerate(recent_obs, 1):
            print(f"{i}. {species}")
            print(f"   Location: {location}")
            print(f"   Date: {date} (observer: {observer})")
    
    def _show_location_insights(self, cursor):
        """Show location-based insights"""
        print(f"\nTOP OBSERVATION LOCATIONS:")
        print("-" * 28)
        
        cursor.execute('''
            SELECT location_description, COUNT(*) as obs_count,
                   COUNT(DISTINCT common_name) as species_count
            FROM wildlife_observations 
            WHERE location_description != 'Unknown location'
            GROUP BY location_description
            ORDER BY obs_count DESC
            LIMIT 8
        ''')
        
        locations = cursor.fetchall()
        
        for location, obs_count, species_count in locations:
            print(f"{location}:")
            print(f"  {obs_count} observations, {species_count} species")
    
    def analyze_species_trends(self, species_name):
        """Analyze trends for a specific species"""
        print(f"\nANALYSIS FOR: {species_name}")
        print("=" * (15 + len(species_name)))
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT COUNT(*), MIN(observed_date), MAX(observed_date),
                           COUNT(DISTINCT location_description) as location_count
                    FROM wildlife_observations 
                    WHERE common_name = ?
                ''', (species_name,))
                
                result = cursor.fetchone()
                
                if result[0] == 0:
                    print(f"No observations found for {species_name}")
                    return
                
                count, first_date, last_date, location_count = result
                
                print(f"Total observations: {count}")
                print(f"Date range: {first_date} to {last_date}")
                print(f"Locations observed: {location_count}")
                
                # Show all locations for this species
                cursor.execute('''
                    SELECT location_description, COUNT(*) as count
                    FROM wildlife_observations 
                    WHERE common_name = ? AND location_description != 'Unknown location'
                    GROUP BY location_description
                    ORDER BY count DESC
                ''', (species_name,))
                
                locations = cursor.fetchall()
                
                if locations:
                    print(f"\nLocation breakdown:")
                    for location, loc_count in locations:
                        print(f"  {location}: {loc_count} observations")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")

def main():
    """Main function for interactive exploration"""
    analyzer = WildlifeAnalyzer()
    
    # Generate the main summary report
    analyzer.generate_summary_report()
    
    print(f"\n" + "=" * 45)
    print("INTERACTIVE ANALYSIS")
    print("=" * 45)
    print("Available commands:")
    print("  - Type a species name to analyze trends")
    print("  - Type 'quit' to exit")
    print("  - Type 'summary' to see the full report again")
    
    while True:
        try:
            command = input("\nEnter command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            elif command.lower() == 'summary':
                analyzer.generate_summary_report()
            elif command:
                analyzer.analyze_species_trends(command)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
