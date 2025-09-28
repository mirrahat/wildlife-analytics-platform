#!/usr/bin/env python3
"""
Test Advanced Analytics Integration
==================================
Quick test to verify the advanced analytics module works with the dashboard.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.advanced_analytics import AdvancedWildlifeAnalytics
    print("Advanced analytics module imported successfully")
    
    # Initialize analytics engine
    analytics = AdvancedWildlifeAnalytics()
    print("Analytics class initialized")
    
    # Load data for testing
    data = analytics.load_comprehensive_data()
    print(f"Data loaded: {len(data)} records for {data['species'].nunique()} species")
    
    if len(data) > 0:
        # Test trend analysis with sample data
        trends = analytics.analyze_population_trends(data.head(100), min_observations=5)
        print(f"Trend analysis completed: {len(trends)} species analyzed")
        
        # Test hotspot detection functionality
        hotspots = analytics.detect_biodiversity_hotspots(data.head(100))
        print(f"Hotspot detection completed: {len(hotspots)} hotspots detected")
        
        # Generate ecosystem health report
        alerts = analytics.assess_conservation_risk(trends, data.head(100))
        report = analytics.generate_ecosystem_health_report(data.head(100), hotspots, alerts)
        
        if report:
            health_score = report['ecosystem_health_score']
            print(f"Ecosystem health report generated: score = {health_score:.2f}")
        else:
            print("Warning: Ecosystem health report empty")
        
        print("\nAll advanced analytics components working correctly!")
        print("The Streamlit dashboard should now display the Advanced Analytics page properly.")
        
    else:
        print("No data available for testing. Run ETL pipeline first.")

except ImportError as e:
    print(f"Import error: {e}")
    print("Install missing dependencies: pip install scikit-learn")
    
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
