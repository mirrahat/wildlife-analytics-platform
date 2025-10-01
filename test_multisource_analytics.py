#!/usr/bin/env python3
"""
Test Multi-Source Analytics functionality
"""
import sys
import os
import sqlite3
import pandas as pd
import json

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_multisource_data():
    """Test multi-source data functionality"""
    print("🔗 Testing Multi-Source Analytics...")
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        # Check if multisource table exists and has data
        try:
            multisource_count = conn.execute("SELECT COUNT(*) FROM wildlife_multisource").fetchone()[0]
            print(f"   📊 Multi-source records: {multisource_count}")
            
            if multisource_count > 0:
                # Test source distribution
                sources = conn.execute("""
                    SELECT source, COUNT(*) as count 
                    FROM wildlife_multisource 
                    GROUP BY source
                """).fetchall()
                
                print("   🔌 Data sources:")
                for source, count in sources:
                    print(f"      - {source}: {count} records")
                
                # Test data quality metrics
                quality_metrics = conn.execute("""
                    SELECT 
                        AVG(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100 as geo_completeness,
                        AVG(CASE WHEN scientific_name IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100 as species_completeness,
                        AVG(CASE WHEN observed_date IS NOT NULL THEN 1.0 ELSE 0.0 END) * 100 as date_completeness
                    FROM wildlife_multisource
                """).fetchone()
                
                print(f"   🎯 Data completeness:")
                print(f"      Geographic: {quality_metrics[0]:.1f}%")
                print(f"      Species info: {quality_metrics[1]:.1f}%")
                print(f"      Date info: {quality_metrics[2]:.1f}%")
                
                # Test cross-source validation
                cross_validation = conn.execute("""
                    SELECT 
                        scientific_name,
                        COUNT(DISTINCT source) as source_count,
                        GROUP_CONCAT(DISTINCT source) as sources
                    FROM wildlife_multisource 
                    WHERE scientific_name IS NOT NULL
                    GROUP BY scientific_name
                    HAVING COUNT(DISTINCT source) > 1
                    ORDER BY source_count DESC
                    LIMIT 5
                """).fetchall()
                
                if cross_validation:
                    print(f"   ✅ Cross-source validation: {len(cross_validation)} species in multiple sources")
                    print("   🔍 Top cross-validated species:")
                    for species, count, sources in cross_validation:
                        print(f"      - {species}: {count} sources ({sources})")
                else:
                    print("   ⚠️  No cross-source validated species found")
                
                print("   ✅ Multi-source data analysis successful")
                
            else:
                print("   ⚠️  No multi-source data available - testing data lake setup...")
                
                # Test data lake infrastructure setup
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS wildlife_multisource (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source TEXT NOT NULL,
                        scientific_name TEXT,
                        common_name TEXT,
                        latitude REAL,
                        longitude REAL,
                        observed_date TEXT,
                        location_description TEXT,
                        observer_name TEXT,
                        quality_score REAL,
                        raw_data TEXT,
                        collected_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        processed BOOLEAN DEFAULT 0
                    )
                """)
                conn.commit()
                print("   ✅ Data lake infrastructure ready for ingestion")
                
        except Exception as e:
            print(f"   ❌ Error testing multi-source data: {e}")

def test_data_lake_architecture():
    """Test data lake architecture components"""
    print("\n🏗️ Testing Data Lake Architecture...")
    
    db_path = "data/aussie_wildlife.db"
    
    with sqlite3.connect(db_path) as conn:
        # Test Bronze Layer (Raw ingestion)
        print("   🥉 Testing Bronze Layer...")
        try:
            bronze_stats = conn.execute("""
                SELECT COUNT(*) as total, 
                       COUNT(DISTINCT source_system) as sources,
                       MIN(extracted_at) as earliest,
                       MAX(extracted_at) as latest
                FROM wildlife_bronze
            """).fetchone()
            
            print(f"      Total records: {bronze_stats[0]:,}")
            print(f"      Data sources: {bronze_stats[1]}")
            print(f"      Time range: {bronze_stats[2]} to {bronze_stats[3]}")
            print("   ✅ Bronze layer operational")
            
        except Exception as e:
            print(f"   ❌ Bronze layer error: {e}")
        
        # Test Silver Layer (Standardized)
        print("   🥈 Testing Silver Layer...")
        try:
            silver_stats = conn.execute("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT common_name) as species,
                       AVG(quality_score) as avg_quality,
                       COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as geo_records
                FROM wildlife_silver
            """).fetchone()
            
            print(f"      Total records: {silver_stats[0]:,}")
            print(f"      Species: {silver_stats[1]}")
            print(f"      Average quality: {silver_stats[2]:.3f}")
            print(f"      Geographic records: {silver_stats[3]:,}")
            print("   ✅ Silver layer operational")
            
        except Exception as e:
            print(f"   ❌ Silver layer error: {e}")
        
        # Test Gold Layer (Analytics-ready)
        print("   🥇 Testing Gold Layer...")
        try:
            gold_stats = conn.execute("""
                SELECT COUNT(*) as total,
                       COUNT(DISTINCT aggregation_type) as agg_types,
                       COUNT(DISTINCT metric_name) as metrics
                FROM wildlife_gold
            """).fetchone()
            
            print(f"      Total records: {gold_stats[0]:,}")
            print(f"      Aggregation types: {gold_stats[1]}")
            print(f"      Metrics: {gold_stats[2]}")
            print("   ✅ Gold layer operational")
            
        except Exception as e:
            print(f"   ❌ Gold layer error: {e}")

def test_export_functionality():
    """Test data export capabilities"""
    print("\n📁 Testing Export Functionality...")
    
    db_path = "data/aussie_wildlife.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Test CSV export capability
            test_data = pd.read_sql_query("""
                SELECT common_name, scientific_name, location_description, 
                       latitude, longitude, observed_date
                FROM wildlife_silver 
                LIMIT 5
            """, conn)
            
            if not test_data.empty:
                # Test CSV generation
                csv_content = test_data.to_csv(index=False)
                print(f"   📄 CSV export: {len(csv_content)} characters generated")
                
                # Test JSON export
                json_content = test_data.to_json(orient='records', indent=2)
                print(f"   📄 JSON export: {len(json_content)} characters generated")
                
                # Test data catalog generation
                catalog_data = {
                    'export_info': {
                        'timestamp': pd.Timestamp.now().isoformat(),
                        'record_count': len(test_data),
                        'columns': list(test_data.columns)
                    },
                    'sample_data': test_data.head(2).to_dict('records')
                }
                
                catalog_json = json.dumps(catalog_data, indent=2, default=str)
                print(f"   📋 Data catalog: {len(catalog_json)} characters generated")
                
                print("   ✅ Export functionality operational")
            else:
                print("   ⚠️  No data available for export testing")
                
    except Exception as e:
        print(f"   ❌ Export functionality error: {e}")

def test_regional_analysis():
    """Test regional data analysis capabilities"""
    print("\n🗺️ Testing Regional Analysis...")
    
    db_path = "data/aussie_wildlife.db"
    
    try:
        with sqlite3.connect(db_path) as conn:
            # Test Australian region classification
            regional_data = conn.execute("""
                SELECT latitude, longitude, location_description
                FROM wildlife_silver 
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                LIMIT 10
            """).fetchall()
            
            if regional_data:
                print(f"   📍 Testing with {len(regional_data)} geographic records")
                
                # Simulate region classification logic
                aus_regions = {
                    'Western Australia': 0,
                    'Victoria/NSW': 0,
                    'Queensland': 0,
                    'South Australia': 0,
                    'Tasmania': 0,
                    'Northern Territory': 0,
                    'Other/International': 0
                }
                
                for lat, lon, location in regional_data:
                    if -28 <= lat <= -17 and 113 <= lon <= 123:
                        aus_regions['Western Australia'] += 1
                    elif -38 <= lat <= -28 and 140 <= lon <= 150:
                        aus_regions['Victoria/NSW'] += 1
                    elif -28 <= lat <= -17 and 138 <= lon <= 150:
                        aus_regions['Queensland'] += 1
                    elif -35 <= lat <= -26 and 129 <= lon <= 141:
                        aus_regions['South Australia'] += 1
                    elif -44 <= lat <= -35 and 143 <= lon <= 148:
                        aus_regions['Tasmania'] += 1
                    elif -26 <= lat <= -12 and 129 <= lon <= 138:
                        aus_regions['Northern Territory'] += 1
                    else:
                        aus_regions['Other/International'] += 1
                
                print("   🏞️ Regional distribution (sample):")
                for region, count in aus_regions.items():
                    if count > 0:
                        print(f"      {region}: {count} records")
                
                print("   ✅ Regional analysis functional")
            else:
                print("   ⚠️  No geographic data for regional analysis")
                
    except Exception as e:
        print(f"   ❌ Regional analysis error: {e}")

if __name__ == "__main__":
    test_multisource_data()
    test_data_lake_architecture()
    test_export_functionality()
    test_regional_analysis()
    print("\n✅ Multi-Source Analytics tests complete!")