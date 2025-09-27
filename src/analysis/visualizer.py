#!/usr/bin/env python3
"""
Australian Wildlife Data Visualizer

Creates charts and maps from the collected wildlife data:
- Species count bar charts  
- Location distribution maps
- Sighting trends over time
- Statistical summaries

Uses matplotlib, seaborn, and folium for different visualization types.
"""

import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import folium
from collections import Counter
import os

class WildlifeVisualizer:
    """
    Creates visualizations from Australian wildlife database.
    Generates charts, maps, and statistical plots.
    """
    
    def __init__(self, db_path="aussie_wildlife.db"):
        """Initialize with database path"""
        self.db_path = db_path
        self.output_dir = "visualizations"
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def load_data(self):
        """Load wildlife data from database into pandas DataFrame"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                SELECT common_name, location_description, latitude, longitude, 
                       observed_date, observer_name, data_source
                FROM wildlife_sightings
                WHERE common_name != 'Unknown species'
                """
                df = pd.read_sql_query(query, conn)
                return df
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def create_species_chart(self):
        """Create bar chart showing species counts"""
        df = self.load_data()
        if df is None or len(df) == 0:
            print("No data available for species chart")
            return
        
        # Count species
        species_counts = df['common_name'].value_counts()
        
        # Create bar chart
        plt.figure(figsize=(12, 6))
        species_counts.head(10).plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title('Most Commonly Observed Australian Wildlife Species')
        plt.xlabel('Species')
        plt.ylabel('Number of Sightings')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(self.output_dir, 'species_counts.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"Species chart saved to: {chart_path}")
        plt.close()
    
    def create_location_map(self):
        """Create interactive map showing wildlife sighting locations"""
        df = self.load_data()
        if df is None or len(df) == 0:
            print("No data available for location map")
            return
        
        # Filter data with coordinates
        map_data = df.dropna(subset=['latitude', 'longitude'])
        
        if len(map_data) == 0:
            print("No location coordinates available for mapping")
            return
        
        # Center map on Australia
        center_lat = map_data['latitude'].mean()
        center_lon = map_data['longitude'].mean()
        
        # Create map
        wildlife_map = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add markers for each sighting
        colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        species_colors = {}
        color_index = 0
        
        for _, row in map_data.iterrows():
            species = row['common_name']
            
            # Assign color to species
            if species not in species_colors:
                species_colors[species] = colors[color_index % len(colors)]
                color_index += 1
            
            # Create popup text
            popup_text = f"""
            <b>{species}</b><br>
            Location: {row['location_description']}<br>
            Date: {row['observed_date']}<br>
            Observer: {row['observer_name']}
            """
            
            # Add marker
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                icon=folium.Icon(color=species_colors[species], icon='paw', prefix='fa')
            ).add_to(wildlife_map)
        
        # Add legend
        legend_html = '<div style="position: fixed; top: 10px; right: 10px; z-index:1000; background-color: white; padding: 10px; border: 2px solid grey;"><h4>Species</h4>'
        for species, color in species_colors.items():
            legend_html += f'<p><i class="fa fa-paw" style="color:{color}"></i> {species}</p>'
        legend_html += '</div>'
        wildlife_map.get_root().html.add_child(folium.Element(legend_html))
        
        # Save map
        map_path = os.path.join(self.output_dir, 'wildlife_locations.html')
        wildlife_map.save(map_path)
        print(f"Interactive map saved to: {map_path}")
        print("Open this file in your web browser to view the map")
    
    def create_timeline_chart(self):
        """Create timeline showing sightings over time"""
        df = self.load_data()
        if df is None or len(df) == 0:
            print("No data available for timeline chart")
            return
        
        # Convert date column to datetime
        df['observed_date'] = pd.to_datetime(df['observed_date'])
        
        # Group by date
        daily_counts = df.groupby(df['observed_date'].dt.date).size()
        
        # Create timeline chart
        plt.figure(figsize=(12, 6))
        daily_counts.plot(kind='line', marker='o', linewidth=2, markersize=6)
        plt.title('Australian Wildlife Sightings Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Sightings')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save chart
        chart_path = os.path.join(self.output_dir, 'sightings_timeline.png')
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"Timeline chart saved to: {chart_path}")
        plt.close()
    
    def create_summary_stats(self):
        """Create statistical summary visualization"""
        df = self.load_data()
        if df is None or len(df) == 0:
            print("No data available for summary statistics")
            return
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Australian Wildlife Data Summary Statistics', fontsize=16)
        
        # Species distribution
        species_counts = df['common_name'].value_counts().head(8)
        axes[0, 0].pie(species_counts.values, labels=species_counts.index, autopct='%1.1f%%')
        axes[0, 0].set_title('Species Distribution')
        
        # Observations by data source
        source_counts = df['data_source'].value_counts()
        axes[0, 1].bar(source_counts.index, source_counts.values, color='lightgreen')
        axes[0, 1].set_title('Observations by Data Source')
        axes[0, 1].set_ylabel('Count')
        
        # Top observers
        observer_counts = df['observer_name'].value_counts().head(10)
        axes[1, 0].barh(observer_counts.index, observer_counts.values, color='coral')
        axes[1, 0].set_title('Top Contributors')
        axes[1, 0].set_xlabel('Number of Observations')
        
        # Monthly distribution (if we have enough data)
        df['month'] = pd.to_datetime(df['observed_date']).dt.month
        monthly_counts = df['month'].value_counts().sort_index()
        axes[1, 1].bar(monthly_counts.index, monthly_counts.values, color='gold')
        axes[1, 1].set_title('Observations by Month')
        axes[1, 1].set_xlabel('Month')
        axes[1, 1].set_ylabel('Count')
        
        plt.tight_layout()
        
        # Save summary
        summary_path = os.path.join(self.output_dir, 'summary_statistics.png')
        plt.savefig(summary_path, dpi=300, bbox_inches='tight')
        print(f"Summary statistics saved to: {summary_path}")
        plt.close()
    
    def generate_all_visualizations(self):
        """Generate all visualization types"""
        print("Australian Wildlife Data Visualization")
        print("=" * 40)
        print("Generating charts and maps from your wildlife database...")
        print()
        
        try:
            self.create_species_chart()
            print()
            
            self.create_location_map()
            print()
            
            self.create_timeline_chart()
            print()
            
            self.create_summary_stats()
            print()
            
            print("All visualizations complete!")
            print(f"Check the '{self.output_dir}' folder for generated files")
            
        except Exception as e:
            print(f"Error generating visualizations: {e}")

def main():
    """Main function to run visualizations"""
    visualizer = WildlifeVisualizer()
    visualizer.generate_all_visualizations()

if __name__ == "__main__":
    main()
