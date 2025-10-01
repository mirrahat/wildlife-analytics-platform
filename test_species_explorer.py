#!/usr/bin/env python3
"""
Test Species Explorer functionality
"""
import sys
import os
import sqlite3
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_species_explorer():
    """Test Species Explorer features"""
    print("🐾 Testing Species Explorer...")
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    # Load silver layer data
    print("\n📊 Loading species data...")
    try:
        silver_data = dashboard.load_silver_layer_data()
        print(f"   ✅ Loaded {len(silver_data)} records")
        
        if not silver_data.empty:
            # Test species list generation
            print("\n🔍 Testing species list generation...")
            species_list = sorted(silver_data['common_name'].dropna().unique())
            print(f"   ✅ Found {len(species_list)} unique species")
            
            # Show top species
            species_counts = silver_data['common_name'].value_counts()
            print("   📈 Top 5 most observed species:")
            for i, (species, count) in enumerate(species_counts.head(5).items(), 1):
                print(f"      {i}. {species}: {count} observations")
            
            # Test individual species analysis
            if len(species_list) > 0:
                test_species = species_list[0]  # Use the first species alphabetically
                print(f"\n🔬 Testing analysis for: {test_species}")
                
                species_data = silver_data[silver_data['common_name'] == test_species]
                print(f"   📊 Species data: {len(species_data)} records")
                
                # Test metrics calculation
                unique_locations = species_data['location_description'].nunique()
                avg_quality = species_data['quality_score'].mean()
                date_range = species_data['observed_date'].nunique()
                
                print(f"   📍 Unique locations: {unique_locations}")
                print(f"   🎯 Average quality: {avg_quality:.3f}")
                print(f"   📅 Observation days: {date_range}")
                
                # Test location analysis
                print("\n🗺️ Testing location analysis...")
                location_counts = species_data['location_description'].value_counts().head(5)
                print("   📍 Top locations:")
                for location, count in location_counts.items():
                    print(f"      - {location}: {count} observations")
                
                # Test temporal analysis
                print("\n⏰ Testing temporal analysis...")
                if 'observed_date' in species_data.columns:
                    species_data_temp = species_data.copy()
                    species_data_temp['observed_date'] = pd.to_datetime(species_data_temp['observed_date'])
                    
                    if not species_data_temp['observed_date'].isna().all():
                        date_range_str = f"{species_data_temp['observed_date'].min().date()} to {species_data_temp['observed_date'].max().date()}"
                        print(f"   📅 Date range: {date_range_str}")
                        
                        # Group by date for timeline
                        daily_counts = species_data_temp.groupby(species_data_temp['observed_date'].dt.date).size()
                        print(f"   📊 Daily observation counts: {len(daily_counts)} unique days")
                        print("   ✅ Temporal analysis successful")
                    else:
                        print("   ⚠️  No valid dates found")
                
                # Test recent observations
                print("\n📝 Testing recent observations display...")
                recent_cols = ['location_description', 'observed_date', 'observer_name', 'quality_score']
                available_cols = [col for col in recent_cols if col in species_data.columns]
                
                if available_cols:
                    recent_observations = species_data[available_cols].head(3)
                    print(f"   ✅ Recent observations table: {len(recent_observations)} rows, {len(available_cols)} columns")
                    print("   📋 Sample recent observation:")
                    if len(recent_observations) > 0:
                        sample = recent_observations.iloc[0]
                        for col in available_cols:
                            print(f"      {col}: {sample[col]}")
                else:
                    print("   ⚠️  No columns available for recent observations")
                
            else:
                print("   ❌ No species found for testing")
                
        else:
            print("   ❌ No species data available")
            
    except Exception as e:
        print(f"   ❌ Error in species explorer testing: {e}")

def test_species_data_integrity():
    """Test data integrity for species exploration"""
    print("\n🔍 Testing species data integrity...")
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        try:
            # Check for species with valid scientific names
            valid_species = conn.execute("""
                SELECT COUNT(DISTINCT common_name) as species_count
                FROM wildlife_silver 
                WHERE common_name IS NOT NULL 
                AND scientific_name IS NOT NULL
            """).fetchone()[0]
            print(f"   🧬 Species with valid scientific names: {valid_species}")
            
            # Check geographic distribution
            geo_coverage = conn.execute("""
                SELECT 
                    COUNT(DISTINCT common_name) as species_with_coords,
                    MIN(latitude) as min_lat,
                    MAX(latitude) as max_lat,
                    MIN(longitude) as min_lon,
                    MAX(longitude) as max_lon
                FROM wildlife_silver 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            """).fetchone()
            
            if geo_coverage[0] > 0:
                print(f"   🗺️ Species with coordinates: {geo_coverage[0]}")
                print(f"   📍 Coordinate bounds: Lat({geo_coverage[1]:.2f}, {geo_coverage[2]:.2f}), Lon({geo_coverage[3]:.2f}, {geo_coverage[4]:.2f})")
            
            # Check temporal distribution
            temporal_range = conn.execute("""
                SELECT 
                    MIN(observed_date) as earliest,
                    MAX(observed_date) as latest,
                    COUNT(DISTINCT DATE(observed_date)) as unique_dates
                FROM wildlife_silver 
                WHERE observed_date IS NOT NULL
            """).fetchone()
            
            if temporal_range[0]:
                print(f"   ⏰ Temporal range: {temporal_range[0]} to {temporal_range[1]}")
                print(f"   📅 Unique observation dates: {temporal_range[2]}")
            
            print("   ✅ Species data integrity check complete")
            
        except Exception as e:
            print(f"   ❌ Error in data integrity check: {e}")

if __name__ == "__main__":
    test_species_explorer()
    test_species_data_integrity()
    print("\n✅ Species Explorer tests complete!")