#!/usr/bin/env python3
"""
Test Advanced Analytics functionality
"""
import sys
import os
import sqlite3
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_advanced_analytics_import():
    """Test advanced analytics module import and dependencies"""
    print("🤖 Testing Advanced Analytics Module...")
    
    try:
        from src.advanced_analytics import AdvancedWildlifeAnalytics
        print("   ✅ Advanced analytics module imported successfully")
        
        # Test initialization
        analytics = AdvancedWildlifeAnalytics()
        print("   ✅ Analytics instance created")
        
        return analytics
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Tip: Install missing dependencies with 'pip install scikit-learn plotly'")
        return None
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return None

def test_data_loading(analytics):
    """Test comprehensive data loading"""
    print("\n📊 Testing Data Loading...")
    
    try:
        data = analytics.load_comprehensive_data()
        print(f"   ✅ Loaded {len(data)} records for analysis")
        
        if not data.empty:
            print(f"   🔍 Columns: {list(data.columns)}")
            print(f"   🐾 Unique species: {data['species'].nunique()}")
            
            # Check for required columns
            required_cols = ['species', 'latitude', 'longitude', 'observed_date']
            missing_cols = [col for col in required_cols if col not in data.columns]
            
            if missing_cols:
                print(f"   ⚠️  Missing required columns: {missing_cols}")
            else:
                print("   ✅ All required columns present")
            
            # Check data types and ranges
            if 'observed_date' in data.columns:
                data['observed_date'] = pd.to_datetime(data['observed_date'], errors='coerce')
                date_range = f"{data['observed_date'].min()} to {data['observed_date'].max()}"
                print(f"   📅 Date range: {date_range}")
            
            if 'latitude' in data.columns and 'longitude' in data.columns:
                lat_range = f"{data['latitude'].min():.2f} to {data['latitude'].max():.2f}"
                lon_range = f"{data['longitude'].min():.2f} to {data['longitude'].max():.2f}"
                print(f"   🗺️ Coordinate ranges: Lat({lat_range}), Lon({lon_range})")
            
            return data
        else:
            print("   ⚠️  No data loaded")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"   ❌ Data loading error: {e}")
        return pd.DataFrame()

def test_population_trends(analytics, data):
    """Test population trend analysis"""
    print("\n📈 Testing Population Trends Analysis...")
    
    try:
        if data.empty:
            print("   ⚠️  No data available for trend analysis")
            return
        
        trends = analytics.analyze_population_trends(data, min_observations=5)
        
        if trends:
            print(f"   ✅ Analyzed trends for {len(trends)} species")
            
            # Show sample trends
            for i, (species, trend_info) in enumerate(list(trends.items())[:3], 1):
                trend_direction = trend_info.get('trend_direction', 'unknown')
                confidence = trend_info.get('confidence_score', 0)
                print(f"   {i}. {species}: {trend_direction} (confidence: {confidence:.3f})")
            
            print("   ✅ Population trends analysis successful")
        else:
            print("   ⚠️  No trends calculated (insufficient data or missing scikit-learn)")
            
    except Exception as e:
        print(f"   ❌ Population trends error: {e}")

def test_biodiversity_hotspots(analytics, data):
    """Test biodiversity hotspot detection"""
    print("\n🌍 Testing Biodiversity Hotspots...")
    
    try:
        if data.empty:
            print("   ⚠️  No data available for hotspot analysis")
            return
        
        hotspots = analytics.detect_biodiversity_hotspots(data, eps_km=50.0)
        
        if hotspots:
            print(f"   ✅ Detected {len(hotspots)} biodiversity hotspots")
            
            # Show sample hotspots (hotspots is a list, not dict)
            for i, hotspot in enumerate(hotspots[:3], 1):
                if hasattr(hotspot, 'species_count'):
                    species_count = hotspot.species_count
                    center = (hotspot.center_lat, hotspot.center_lon)
                    print(f"   {i}. Hotspot at ({center[0]:.2f}, {center[1]:.2f}): {species_count} species")
                else:
                    print(f"   {i}. Hotspot detected (detailed info structure varies)")
            
            print("   ✅ Biodiversity hotspots analysis successful")
        else:
            print("   ⚠️  No hotspots detected (insufficient data or missing scikit-learn)")
            
    except Exception as e:
        print(f"   ❌ Biodiversity hotspots error: {e}")

def test_conservation_alerts(analytics, data):
    """Test conservation alert generation"""
    print("\n🚨 Testing Conservation Alerts...")
    
    try:
        if data.empty:
            print("   ⚠️  No data available for conservation analysis")
            return
        
        # First get trends for conservation analysis
        trends = analytics.analyze_population_trends(data, min_observations=5)
        alerts = analytics.assess_conservation_risk(trends, data)
        
        if alerts:
            print(f"   ✅ Generated {len(alerts)} conservation alerts")
            
            # Group by severity (alerts are objects, not dicts)
            severity_counts = {}
            for alert in alerts:
                severity = getattr(alert, 'severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            print("   📊 Alert severity distribution:")
            for severity, count in severity_counts.items():
                print(f"      {severity}: {count} alerts")
            
            # Show sample alerts
            print("   🔍 Sample alerts:")
            for i, alert in enumerate(alerts[:2], 1):
                species = getattr(alert, 'species_name', 'Unknown')
                severity = getattr(alert, 'severity', 'unknown')
                issue = getattr(alert, 'issue_type', 'unknown')
                print(f"   {i}. {species}: {severity} - {issue}")
            
            print("   ✅ Conservation alerts analysis successful")
        else:
            print("   ⚠️  No conservation alerts generated")
            
    except Exception as e:
        print(f"   ❌ Conservation alerts error: {e}")

def test_ecosystem_health(analytics, data):
    """Test ecosystem health report"""
    print("\n🌿 Testing Ecosystem Health Report...")
    
    try:
        if data.empty:
            print("   ⚠️  No data available for ecosystem analysis")
            return
        
        # Get required data for ecosystem health report
        trends = analytics.analyze_population_trends(data, min_observations=5)
        hotspots = analytics.detect_biodiversity_hotspots(data, eps_km=50.0)
        alerts = analytics.assess_conservation_risk(trends, data)
        report = analytics.generate_ecosystem_health_report(data, hotspots, alerts)
        
        if report:
            print("   ✅ Ecosystem health report generated")
            
            # Show key metrics
            overall_score = report.get('overall_health_score', 0)
            print(f"   🎯 Overall health score: {overall_score:.3f}")
            
            biodiversity_index = report.get('biodiversity_index', 0)
            print(f"   🌱 Biodiversity index: {biodiversity_index:.3f}")
            
            data_coverage = report.get('data_coverage_score', 0)
            print(f"   📊 Data coverage score: {data_coverage:.3f}")
            
            # Show recommendations if available
            recommendations = report.get('recommendations', [])
            if recommendations:
                print(f"   💡 Recommendations: {len(recommendations)} items")
                for i, rec in enumerate(recommendations[:2], 1):
                    print(f"      {i}. {rec}")
            
            print("   ✅ Ecosystem health analysis successful")
        else:
            print("   ⚠️  No ecosystem health report generated")
            
    except Exception as e:
        print(f"   ❌ Ecosystem health error: {e}")

def test_ml_configuration():
    """Test ML model configuration and capabilities"""
    print("\n⚙️ Testing ML Configuration...")
    
    try:
        # Test scikit-learn availability
        try:
            import sklearn
            print(f"   ✅ scikit-learn available (version {sklearn.__version__})")
            
            # Test key ML components
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.cluster import DBSCAN
            from sklearn.preprocessing import StandardScaler
            print("   ✅ Random Forest, DBSCAN, and StandardScaler available")
            
        except ImportError:
            print("   ❌ scikit-learn not available")
        
        # Test Plotly availability
        try:
            import plotly
            print(f"   ✅ Plotly available (version {plotly.__version__})")
        except ImportError:
            print("   ❌ Plotly not available")
        
        print("   ✅ ML configuration check complete")
        
    except Exception as e:
        print(f"   ❌ ML configuration error: {e}")

if __name__ == "__main__":
    # Test advanced analytics functionality
    analytics = test_advanced_analytics_import()
    
    if analytics:
        data = test_data_loading(analytics)
        test_population_trends(analytics, data)
        test_biodiversity_hotspots(analytics, data)
        test_conservation_alerts(analytics, data)
        test_ecosystem_health(analytics, data)
    
    test_ml_configuration()
    print("\n✅ Advanced Analytics tests complete!")