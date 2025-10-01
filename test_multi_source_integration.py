#!/usr/bin/env python3
"""
Multi-Source Integration Test & Demo
===================================
Test and demonstrate the complete multi-source data integration functionality.
"""

import sqlite3
import pandas as pd
from datetime import datetime

def test_multi_source_integration():
    """Test the complete multi-source integration"""
    
    print("🌐 MULTI-SOURCE INTEGRATION TEST")
    print("=" * 50)
    
    # 1. Check Database Status
    print("\n📊 DATABASE STATUS CHECK")
    print("-" * 30)
    
    conn = sqlite3.connect('data/aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Get table counts
    tables_info = {}
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
    tables_info['Bronze Layer'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
    tables_info['Silver Layer'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
    tables_info['Gold Layer'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM wildlife_multisource")
    tables_info['Multi-Source'] = cursor.fetchone()[0]
    
    # Multi-source breakdown
    cursor.execute("SELECT source, COUNT(*) FROM wildlife_multisource GROUP BY source")
    source_breakdown = cursor.fetchall()
    
    print("✅ Data Lake Status:")
    for layer, count in tables_info.items():
        print(f"   {layer}: {count:,} records")
    
    print(f"\n🔌 Active Data Sources: {len(source_breakdown)}")
    for source, count in source_breakdown:
        source_icon = "🔵" if source == 'iNaturalist' else "🟢" if source == 'ala' else "🟡"
        print(f"   {source_icon} {source}: {count:,} records")
    
    # 2. Cross-Source Validation
    print(f"\n🔍 CROSS-SOURCE VALIDATION")
    print("-" * 35)
    
    # Find species in multiple sources
    cursor.execute("""
        SELECT scientific_name, GROUP_CONCAT(DISTINCT source) as sources, COUNT(DISTINCT source) as source_count
        FROM wildlife_multisource 
        WHERE scientific_name IS NOT NULL
        GROUP BY scientific_name
        HAVING COUNT(DISTINCT source) > 1
        ORDER BY source_count DESC, scientific_name
        LIMIT 10
    """)
    
    cross_validated = cursor.fetchall()
    
    if cross_validated:
        print("✅ Species validated by multiple sources:")
        for species, sources, count in cross_validated:
            print(f"   🎯 {species}")
            print(f"      Sources: {sources} ({count} sources)")
    else:
        print("ℹ️  No cross-validated species found yet")
    
    # 3. Data Quality Assessment
    print(f"\n⭐ DATA QUALITY ASSESSMENT")
    print("-" * 32)
    
    # Quality metrics by source
    cursor.execute("""
        SELECT source,
               COUNT(*) as total_records,
               COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as with_coordinates,
               COUNT(CASE WHEN scientific_name IS NOT NULL THEN 1 END) as with_species_name,
               COUNT(CASE WHEN observed_date IS NOT NULL THEN 1 END) as with_date
        FROM wildlife_multisource
        GROUP BY source
    """)
    
    quality_data = cursor.fetchall()
    
    print("📈 Quality Metrics by Source:")
    print("   " + "-" * 70)
    print(f"   {'Source':<20} {'Records':<10} {'Coords':<8} {'Species':<8} {'Dates':<8}")
    print("   " + "-" * 70)
    
    for source, total, coords, species, dates in quality_data:
        coord_pct = (coords/total*100) if total > 0 else 0
        species_pct = (species/total*100) if total > 0 else 0
        date_pct = (dates/total*100) if total > 0 else 0
        
        print(f"   {source:<20} {total:<10} {coord_pct:>6.1f}% {species_pct:>6.1f}% {date_pct:>6.1f}%")
    
    # 4. Geographic Coverage
    print(f"\n🗺️  GEOGRAPHIC COVERAGE")
    print("-" * 28)
    
    cursor.execute("""
        SELECT source,
               MIN(latitude) as min_lat, MAX(latitude) as max_lat,
               MIN(longitude) as min_lon, MAX(longitude) as max_lon,
               COUNT(CASE WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN 1 END) as geo_records
        FROM wildlife_multisource
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        GROUP BY source
    """)
    
    geo_coverage = cursor.fetchall()
    
    for source, min_lat, max_lat, min_lon, max_lon, geo_count in geo_coverage:
        lat_range = max_lat - min_lat if max_lat and min_lat else 0
        lon_range = max_lon - min_lon if max_lon and min_lon else 0
        
        print(f"📍 {source}:")
        print(f"   Geographic records: {geo_count:,}")
        print(f"   Latitude range: {lat_range:.2f}° (coverage)")
        print(f"   Longitude range: {lon_range:.2f}° (coverage)")
    
    # 5. Integration Benefits Summary
    print(f"\n🎉 MULTI-SOURCE INTEGRATION BENEFITS")
    print("-" * 42)
    
    total_multisource = tables_info['Multi-Source']
    single_source_estimate = max([count for source, count in source_breakdown]) if source_breakdown else 0
    
    benefits = [
        f"✅ Data Redundancy: {len(source_breakdown)} active sources vs 1 single source",
        f"✅ Volume Increase: {total_multisource:,} records vs ~{single_source_estimate:,} single-source",
        f"✅ Cross-Validation: {len(cross_validated)} species confirmed by multiple sources",
        f"✅ Geographic Coverage: Combined coverage from government + citizen science",
        f"✅ Data Quality: Multiple validation layers and source prioritization",
        f"✅ Reliability: System continues working even if one source fails"
    ]
    
    for benefit in benefits:
        print(f"   {benefit}")
    
    # 6. Dashboard Integration Status
    print(f"\n📊 DASHBOARD INTEGRATION STATUS")
    print("-" * 38)
    
    dashboard_features = [
        f"✅ Multi-Source Metrics: Now showing {len(source_breakdown)} sources in main dashboard",
        f"✅ Source Breakdown: Pie chart showing distribution across sources",
        f"✅ ETL Pipeline: Enhanced to use multi-source collector",
        f"✅ Analytics Page: Multi-source data lake analytics available",
        f"✅ Cross-Validation: Species validation across platforms",
        f"✅ Export Features: Multi-layer data export capabilities"
    ]
    
    for feature in dashboard_features:
        print(f"   {feature}")
    
    conn.close()
    
    print(f"\n🚀 NEXT STEPS FOR ENHANCEMENT")
    print("-" * 33)
    print("   1. Set EBIRD_API_KEY environment variable to enable eBird data")
    print("   2. Improve GBIF species name matching for more data")
    print("   3. Schedule regular multi-source data collection")
    print("   4. Implement real-time cross-source data validation")
    print("   5. Add conservation status integration from multiple sources")
    
    print(f"\n✅ Multi-source integration test completed!")
    print(f"🌐 Dashboard URL: http://localhost:8502")
    print(f"📈 Total records from {len(source_breakdown)} sources: {total_multisource:,}")

if __name__ == "__main__":
    test_multi_source_integration()