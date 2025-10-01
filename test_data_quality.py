#!/usr/bin/env python3
"""
Test Data Quality Dashboard functionality
"""
import sys
import os
import sqlite3
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_quality_features():
    """Test data quality dashboard features"""
    print("🔍 Testing Data Quality Dashboard...")
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    # Load silver layer data for quality analysis
    print("\n📊 Testing Silver Layer Data Loading...")
    try:
        silver_data = dashboard.load_silver_layer_data()
        print(f"   ✅ Loaded {len(silver_data)} silver layer records")
        
        if not silver_data.empty:
            print(f"   🔍 Columns: {list(silver_data.columns)}")
            
            # Test data completeness analysis
            print("\n📈 Testing Data Completeness Analysis...")
            completeness_fields = ['common_name', 'scientific_name', 'location_description', 
                                 'latitude', 'longitude', 'observed_date', 'observer_name']
            
            completeness_data = []
            for field in completeness_fields:
                if field in silver_data.columns:
                    completeness = (silver_data[field].notna().sum() / len(silver_data)) * 100
                    completeness_data.append({'Field': field, 'Completeness (%)': completeness})
                    print(f"      {field}: {completeness:.1f}% complete")
                else:
                    print(f"      {field}: Column not found")
            
            if completeness_data:
                print("   ✅ Data completeness analysis successful")
            
            # Test quality score distribution
            print("\n🎯 Testing Quality Score Analysis...")
            if 'quality_score' in silver_data.columns:
                quality_stats = silver_data['quality_score'].describe()
                print(f"      Average quality: {quality_stats['mean']:.3f}")
                print(f"      Min quality: {quality_stats['min']:.3f}")
                print(f"      Max quality: {quality_stats['max']:.3f}")
                print("   ✅ Quality score analysis successful")
            else:
                print("   ⚠️  No quality_score column found")
            
            # Test data source breakdown
            print("\n📊 Testing Data Source Analysis...")
            if 'data_source' in silver_data.columns:
                source_counts = silver_data['data_source'].value_counts()
                print("      Data sources:")
                for source, count in source_counts.items():
                    print(f"         {source}: {count} records ({count/len(silver_data)*100:.1f}%)")
                print("   ✅ Data source analysis successful")
            else:
                print("   ⚠️  No data_source column found")
            
            # Test geographic data quality
            print("\n🗺️ Testing Geographic Data Quality...")
            geo_complete = silver_data[['latitude', 'longitude']].notna().all(axis=1)
            geo_completeness = (geo_complete.sum() / len(silver_data)) * 100
            print(f"      Geographic completeness: {geo_completeness:.1f}%")
            
            if geo_completeness > 0:
                valid_coords = silver_data[geo_complete]
                lat_range = f"{valid_coords['latitude'].min():.2f} to {valid_coords['latitude'].max():.2f}"
                lon_range = f"{valid_coords['longitude'].min():.2f} to {valid_coords['longitude'].max():.2f}"
                print(f"      Latitude range: {lat_range}")
                print(f"      Longitude range: {lon_range}")
                
                # Check for Australian coordinates
                aus_coords = valid_coords[
                    (valid_coords['latitude'].between(-44, -10)) & 
                    (valid_coords['longitude'].between(113, 154))
                ]
                aus_percentage = (len(aus_coords) / len(valid_coords)) * 100
                print(f"      Australian coordinates: {aus_percentage:.1f}%")
                
            print("   ✅ Geographic data quality analysis successful")
            
        else:
            print("   ❌ No silver layer data available")
            
    except Exception as e:
        print(f"   ❌ Error in data quality testing: {e}")

def test_data_validation():
    """Test data validation and integrity checks"""
    print("\n🔧 Testing Data Validation...")
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        # Test for duplicate records
        try:
            duplicate_check = conn.execute("""
                SELECT COUNT(*) as duplicates FROM (
                    SELECT scientific_name, latitude, longitude, observed_date, COUNT(*) as cnt
                    FROM wildlife_silver 
                    WHERE scientific_name IS NOT NULL
                    GROUP BY scientific_name, latitude, longitude, observed_date
                    HAVING COUNT(*) > 1
                )
            """).fetchone()[0]
            print(f"   📊 Potential duplicates: {duplicate_check}")
        except Exception as e:
            print(f"   ⚠️  Duplicate check failed: {e}")
        
        # Test for data consistency between layers
        try:
            bronze_count = conn.execute("SELECT COUNT(*) FROM wildlife_bronze").fetchone()[0]
            silver_count = conn.execute("SELECT COUNT(*) FROM wildlife_silver").fetchone()[0]
            gold_count = conn.execute("SELECT COUNT(*) FROM wildlife_gold").fetchone()[0]
            
            print(f"   📈 Layer progression: Bronze({bronze_count}) → Silver({silver_count}) → Gold({gold_count})")
            
            if silver_count >= bronze_count:
                print("   ⚠️  Silver layer has more records than Bronze (data enrichment occurred)")
            else:
                print("   ✅ Normal data flow: Bronze → Silver filtering")
                
        except Exception as e:
            print(f"   ❌ Layer consistency check failed: {e}")

if __name__ == "__main__":
    test_data_quality_features()
    test_data_validation()
    print("\n✅ Data Quality Dashboard tests complete!")