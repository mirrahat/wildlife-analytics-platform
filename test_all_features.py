#!/usr/bin/env python3
"""
Comprehensive test of all dashboard features
"""
import sys
import os
import sqlite3
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_all_features():
    """Run comprehensive tests on all dashboard features"""
    print("🧪 COMPREHENSIVE FEATURE TEST REPORT")
    print("=" * 50)
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    # Test results summary
    results = {
        'Database Status': False,
        'Main Dashboard': False,
        'ETL Monitoring': False,
        'Data Quality': False,
        'Species Explorer': False,
        'Multi-Source Analytics': False,
        'Advanced Analytics': False
    }
    
    # 1. Database Status
    print("\n1️⃣ DATABASE STATUS")
    try:
        conn = dashboard.get_connection()
        if conn:
            # Check all tables
            tables = ['wildlife_observations', 'wildlife_bronze', 'wildlife_silver', 
                     'wildlife_gold', 'wildlife_multisource', 'etl_job_executions']
            
            table_counts = {}
            for table in tables:
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                table_counts[table] = count
            
            conn.close()
            
            print("   ✅ Database connection successful")
            print("   📊 Table status:")
            for table, count in table_counts.items():
                status = "✅" if count > 0 else "⚠️ "
                print(f"      {table}: {count:,} records {status}")
            
            results['Database Status'] = True
        else:
            print("   ❌ Database connection failed")
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    
    # 2. Main Dashboard Functions
    print("\n2️⃣ MAIN DASHBOARD")
    try:
        # Test key dashboard functions
        wildlife_data = dashboard.load_wildlife_observations()
        etl_summary = dashboard.load_etl_layers_summary()
        silver_data = dashboard.load_silver_layer_data()
        
        print(f"   ✅ Wildlife observations: {len(wildlife_data)} records")
        print(f"   ✅ ETL summary: {len(etl_summary)} metrics")
        print(f"   ✅ Silver layer data: {len(silver_data)} records")
        
        # Check for mapping data
        if not silver_data.empty and 'latitude' in silver_data.columns:
            geo_count = silver_data[['latitude', 'longitude']].notna().all(axis=1).sum()
            print(f"   🗺️ Geographic records for mapping: {geo_count}")
        
        results['Main Dashboard'] = True
    except Exception as e:
        print(f"   ❌ Main dashboard error: {e}")
    
    # 3. ETL Monitoring
    print("\n3️⃣ ETL MONITORING")
    try:
        etl_history = dashboard.load_etl_job_history()
        print(f"   ✅ ETL job history: {len(etl_history)} jobs")
        
        if not etl_history.empty:
            success_rate = (etl_history['status'] == 'success').mean() * 100
            print(f"   📈 Success rate: {success_rate:.1f}%")
        
        results['ETL Monitoring'] = True
    except Exception as e:
        print(f"   ❌ ETL monitoring error: {e}")
    
    # 4. Data Quality
    print("\n4️⃣ DATA QUALITY")
    try:
        silver_data = dashboard.load_silver_layer_data()
        
        if not silver_data.empty:
            # Calculate completeness for key fields
            key_fields = ['common_name', 'scientific_name', 'latitude', 'longitude']
            completeness = {}
            
            for field in key_fields:
                if field in silver_data.columns:
                    completeness[field] = (silver_data[field].notna().sum() / len(silver_data)) * 100
            
            print("   ✅ Data completeness analysis:")
            for field, percentage in completeness.items():
                print(f"      {field}: {percentage:.1f}%")
            
            # Quality score analysis
            if 'quality_score' in silver_data.columns:
                avg_quality = silver_data['quality_score'].mean()
                print(f"   🎯 Average quality score: {avg_quality:.3f}")
        
        results['Data Quality'] = True
    except Exception as e:
        print(f"   ❌ Data quality error: {e}")
    
    # 5. Species Explorer
    print("\n5️⃣ SPECIES EXPLORER")
    try:
        silver_data = dashboard.load_silver_layer_data()
        
        if not silver_data.empty:
            species_count = silver_data['common_name'].nunique()
            print(f"   ✅ Species catalog: {species_count} species")
            
            # Test species analysis capability
            if species_count > 0:
                top_species = silver_data['common_name'].value_counts().head(3)
                print("   🔍 Top species by observations:")
                for species, count in top_species.items():
                    print(f"      {species}: {count} observations")
        
        results['Species Explorer'] = True
    except Exception as e:
        print(f"   ❌ Species explorer error: {e}")
    
    # 6. Multi-Source Analytics
    print("\n6️⃣ MULTI-SOURCE ANALYTICS")
    try:
        db_path = "data/aussie_wildlife.db"
        with sqlite3.connect(db_path) as conn:
            multisource_count = conn.execute("SELECT COUNT(*) FROM wildlife_multisource").fetchone()[0]
            print(f"   ✅ Multi-source records: {multisource_count}")
            
            if multisource_count > 0:
                sources = conn.execute("SELECT DISTINCT source FROM wildlife_multisource").fetchall()
                print(f"   🔌 Data sources: {len(sources)} ({', '.join([s[0] for s in sources])})")
        
        results['Multi-Source Analytics'] = True
    except Exception as e:
        print(f"   ❌ Multi-source analytics error: {e}")
    
    # 7. Advanced Analytics
    print("\n7️⃣ ADVANCED ANALYTICS")
    try:
        from src.advanced_analytics import AdvancedWildlifeAnalytics
        analytics = AdvancedWildlifeAnalytics()
        
        data = analytics.load_comprehensive_data()
        print(f"   ✅ Advanced analytics data: {len(data)} records")
        
        if not data.empty:
            # Test ML capabilities
            try:
                import sklearn
                print(f"   🤖 ML capabilities: Available (scikit-learn {sklearn.__version__})")
                
                # Quick functionality test
                if len(data) > 10:
                    trends = analytics.analyze_population_trends(data, min_observations=5)
                    print(f"   📈 Population trends: {len(trends)} species analyzed")
                    
                    hotspots = analytics.detect_biodiversity_hotspots(data, eps_km=50.0)
                    print(f"   🌍 Biodiversity hotspots: {len(hotspots)} detected")
                
            except ImportError:
                print("   ⚠️  ML capabilities: Limited (missing scikit-learn)")
        
        results['Advanced Analytics'] = True
    except Exception as e:
        print(f"   ❌ Advanced analytics error: {e}")
    
    # Summary Report
    print("\n" + "=" * 50)
    print("📋 FEATURE TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for feature, status in results.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {feature}")
    
    print(f"\n🎯 Overall Status: {passed}/{total} features working ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL FEATURES OPERATIONAL!")
        print("   Dashboard is ready for production use.")
    elif passed >= total * 0.8:
        print("🟡 MOSTLY OPERATIONAL")
        print("   Core features working, minor issues detected.")
    else:
        print("🔴 ISSUES DETECTED")
        print("   Multiple features need attention.")
    
    return results

if __name__ == "__main__":
    test_all_features()
    print("\n✅ Comprehensive testing complete!")
    print("\n🌐 Access the dashboard at: http://localhost:8501")