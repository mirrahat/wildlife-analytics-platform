#!/usr/bin/env python3
"""
Australian Wildlife Data Visualizer

Creates charts and graphs from your collected wildlife data.
Shows species distributions, location patterns, and trends over time.
"""

import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
import os

class WildlifeVisualizer:
    """Creates visualizations from Australian wildlife database"""
    
    def __init__(self, db_name="aussie_wildlife.db"):
        self.db_name = db_name
        self.output_dir = "data/visualizations"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def load_data_from_db(self):
        """Load wildlife data from database into pandas DataFrame"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                query = """
                SELECT common_name, scientific_name, location_description, 
                       latitude, longitude, observed_date, observer_name
                FROM wildlife_sightings 
                WHERE common_name != 'Unknown species'
                ORDER BY observed_date DESC
                """
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def create_species_chart(self):
        """Create a bar chart showing species counts"""
        df = self.load_data_from_db()
        if df is None or df.empty:
            print("No data available for species chart")
            return
        
        # Count species occurrences
        species_counts = df['common_name'].value_counts().head(10)
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(species_counts)), species_counts.values, 
                      color=['#2E8B57', '#4682B4', '#CD853F', '#9370DB', '#20B2AA',
                             '#FF6347', '#32CD32', '#FFD700', '#FF69B4', '#8FBC8F'])
        
        plt.title('Australian Wildlife Species - Observation Counts', fontsize=16, pad=20)
        plt.xlabel('Species', fontsize=12)
        plt.ylabel('Number of Observations', fontsize=12)
        
        # Rotate species names for better readability
        plt.xticks(range(len(species_counts)), species_counts.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.tight_layout()
        chart_path = os.path.join(self.output_dir, 'species_counts.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Species chart saved to: {chart_path}")
    
    def create_location_chart(self):
        """Create a chart showing top observation locations"""
        df = self.load_data_from_db()
        if df is None or df.empty:
            print("No data available for location chart")
            return
        
        # Extract state/territory from location descriptions
        location_counts = df['location_description'].value_counts().head(8)
        
        plt.figure(figsize=(10, 8))
        
        # Create horizontal bar chart
        bars = plt.barh(range(len(location_counts)), location_counts.values,
                       color=['#228B22', '#4169E1', '#DC143C', '#FF8C00', '#9932CC',
                              '#00CED1', '#FF1493', '#32CD32'])
        
        plt.title('Top Wildlife Observation Locations in Australia', fontsize=16, pad=20)
        plt.xlabel('Number of Observations', fontsize=12)
        plt.ylabel('Location', fontsize=12)
        
        # Set y-axis labels
        plt.yticks(range(len(location_counts)), 
                  [loc[:50] + '...' if len(loc) > 50 else loc for loc in location_counts.index])
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            plt.text(width + 0.1, bar.get_y() + bar.get_height()/2.,
                    f'{int(width)}', ha='left', va='center')
        
        plt.tight_layout()
        chart_path = os.path.join(self.output_dir, 'location_counts.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Location chart saved to: {chart_path}")
    
    def create_timeline_chart(self):
        """Create a timeline showing observations over time"""
        df = self.load_data_from_db()
        if df is None or df.empty:
            print("No data available for timeline chart")
            return
        
        # Convert date column to datetime
        df['observed_date'] = pd.to_datetime(df['observed_date'], errors='coerce')
        df = df.dropna(subset=['observed_date'])
        
        if df.empty:
            print("No valid dates found for timeline")
            return
        
        # Group by date and count observations
        daily_counts = df.groupby(df['observed_date'].dt.date).size()
        
        plt.figure(figsize=(12, 6))
        plt.plot(daily_counts.index, daily_counts.values, 
                marker='o', linewidth=2, markersize=6, color='#2E8B57')
        
        plt.title('Australian Wildlife Observations Over Time', fontsize=16, pad=20)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Number of Observations', fontsize=12)
        
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = os.path.join(self.output_dir, 'timeline.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.show()
        print(f"Timeline chart saved to: {chart_path}")
    
    def create_summary_report(self):
        """Generate a summary report with key statistics"""
        df = self.load_data_from_db()
        if df is None or df.empty:
            print("No data available for summary report")
            return
        
        print("AUSTRALIAN WILDLIFE DATABASE SUMMARY REPORT")
        print("=" * 50)
        print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Basic statistics
        total_observations = len(df)
        unique_species = df['common_name'].nunique()
        unique_locations = df['location_description'].nunique()
        unique_observers = df['observer_name'].nunique()
        
        print(f"Total observations: {total_observations}")
        print(f"Unique species: {unique_species}")
        print(f"Unique locations: {unique_locations}")
        print(f"Citizen scientists contributing: {unique_observers}")
        print()
        
        # Top species
        print("Top 5 most observed species:")
        top_species = df['common_name'].value_counts().head(5)
        for i, (species, count) in enumerate(top_species.items(), 1):
            print(f"  {i}. {species}: {count} observations")
        print()
        
        # Date range
        df['observed_date'] = pd.to_datetime(df['observed_date'], errors='coerce')
        valid_dates = df['observed_date'].dropna()
        if not valid_dates.empty:
            earliest = valid_dates.min().strftime('%Y-%m-%d')
            latest = valid_dates.max().strftime('%Y-%m-%d')
            print(f"Observation period: {earliest} to {latest}")
        print()
        
        print("Charts generated in data/visualizations/ folder")

def main():
    """Generate all visualizations for Australian wildlife data"""
    print("Australian Wildlife Data Visualizer")
    print("=" * 40)
    print("Creating charts and reports from your wildlife database...")
    print()
    
    visualizer = WildlifeVisualizer()
    
    # Check if database exists
    if not os.path.exists(visualizer.db_name):
        print(f"Database '{visualizer.db_name}' not found!")
        print("Run 'python main.py collect' first to gather some data.")
        return
    
    # Generate summary report
    visualizer.create_summary_report()
    print()
    
    # Create visualizations
    print("Generating visualizations...")
    
    try:
        visualizer.create_species_chart()
        print()
        
        visualizer.create_location_chart()
        print()
        
        visualizer.create_timeline_chart()
        print()
        
        print("All visualizations completed!")
        print("Check the data/visualizations/ folder for chart images.")
        
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Install with: pip install matplotlib pandas")
    except Exception as e:
        print(f"Error creating visualizations: {e}")

if __name__ == "__main__":
    main()
