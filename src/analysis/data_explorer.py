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

    def explore_etl_layers(self):
        """Explore data across ETL layers (Bronze, Silver, Gold)"""
        print("\nETL DATA LAYERS ANALYSIS")
        print("=" * 30)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Bronze Layer Analysis
                print("\n🥉 BRONZE LAYER (Raw Data):")
                print("-" * 25)
                
                cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
                bronze_count = cursor.fetchone()[0]
                print(f"Total raw records: {bronze_count}")
                
                if bronze_count > 0:
                    cursor.execute('''
                        SELECT source_system, COUNT(*) as count,
                               MIN(datetime(extracted_at)) as first_extraction,
                               MAX(datetime(extracted_at)) as last_extraction
                        FROM wildlife_bronze 
                        GROUP BY source_system
                        ORDER BY count DESC
                    ''')
                    
                    bronze_sources = cursor.fetchall()
                    print("Sources breakdown:")
                    for source, count, first, last in bronze_sources:
                        print(f"  • {source}: {count} records ({first} to {last})")
                
                # Silver Layer Analysis
                print("\n🥈 SILVER LAYER (Cleaned Data):")
                print("-" * 27)
                
                cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
                silver_count = cursor.fetchone()[0]
                print(f"Total cleaned records: {silver_count}")
                
                if silver_count > 0:
                    # Quality score analysis
                    cursor.execute('''
                        SELECT 
                            AVG(quality_score) as avg_quality,
                            MIN(quality_score) as min_quality,
                            MAX(quality_score) as max_quality,
                            COUNT(CASE WHEN quality_score >= 0.8 THEN 1 END) as high_quality_count
                        FROM wildlife_silver
                    ''')
                    
                    quality_stats = cursor.fetchone()
                    avg_qual, min_qual, max_qual, high_qual_count = quality_stats
                    
                    print(f"Quality Score Statistics:")
                    print(f"  • Average quality: {avg_qual:.3f}")
                    print(f"  • Quality range: {min_qual:.3f} to {max_qual:.3f}")
                    print(f"  • High quality records (≥0.8): {high_qual_count} ({high_qual_count/silver_count*100:.1f}%)")
                    
                    # Top species in silver layer
                    cursor.execute('''
                        SELECT common_name, COUNT(*) as count, AVG(quality_score) as avg_quality
                        FROM wildlife_silver 
                        WHERE common_name IS NOT NULL
                        GROUP BY common_name
                        ORDER BY count DESC
                        LIMIT 5
                    ''')
                    
                    silver_species = cursor.fetchall()
                    print(f"\nTop species (by observation count):")
                    for species, count, avg_qual in silver_species:
                        print(f"  • {species}: {count} observations (avg quality: {avg_qual:.3f})")
                
                # Gold Layer Analysis
                print("\n🥇 GOLD LAYER (Analytics Data):")
                print("-" * 28)
                
                cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
                gold_count = cursor.fetchone()[0]
                print(f"Total analytics records: {gold_count}")
                
                if gold_count > 0:
                    cursor.execute('''
                        SELECT aggregation_type, COUNT(*) as count,
                               MIN(datetime(created_at)) as first_created,
                               MAX(datetime(created_at)) as last_created
                        FROM wildlife_gold
                        GROUP BY aggregation_type
                        ORDER BY count DESC
                    ''')
                    
                    gold_aggregations = cursor.fetchall()
                    print("Analytics aggregations:")
                    for agg_type, count, first, last in gold_aggregations:
                        print(f"  • {agg_type}: {count} metrics (created {first} to {last})")
                else:
                    print("No analytics data available. Run ETL pipeline to generate gold layer data.")
                
                # Data Flow Summary
                print(f"\nDATA FLOW SUMMARY:")
                print(f"  Raw Data (Bronze)    → {bronze_count:,} records")
                print(f"  Cleaned Data (Silver) → {silver_count:,} records")  
                print(f"  Analytics (Gold)     → {gold_count:,} metrics")
                
                if bronze_count > 0 and silver_count > 0:
                    processing_rate = (silver_count / bronze_count) * 100
                    print(f"  Processing success rate: {processing_rate:.1f}%")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    def show_etl_job_history(self):
        """Show ETL job execution history"""
        print("\nETL JOB EXECUTION HISTORY")
        print("=" * 30)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT job_name, status, 
                           records_extracted, records_transformed, records_loaded,
                           datetime(start_time) as execution_time,
                           ROUND((julianday(end_time) - julianday(start_time)) * 86400, 2) as duration_seconds
                    FROM etl_job_executions
                    ORDER BY start_time DESC
                    LIMIT 10
                ''')
                
                job_history = cursor.fetchall()
                
                if job_history:
                    print("Recent ETL executions:")
                    for job_name, status, extracted, transformed, loaded, exec_time, duration in job_history:
                        print(f"\n• {job_name}")
                        print(f"  Status: {status}")
                        print(f"  Records: {extracted} → {transformed} → {loaded}")
                        print(f"  Duration: {duration}s at {exec_time}")
                    
                    # Success rate calculation
                    cursor.execute('''
                        SELECT 
                            COUNT(*) as total_jobs,
                            COUNT(CASE WHEN status = 'success' THEN 1 END) as successful_jobs
                        FROM etl_job_executions
                    ''')
                    
                    total, successful = cursor.fetchone()
                    if total > 0:
                        success_rate = (successful / total) * 100
                        print(f"\nOverall ETL Success Rate: {success_rate:.1f}% ({successful}/{total} jobs)")
                
                else:
                    print("No ETL job history found. Run the ETL pipeline first.")
                    
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
