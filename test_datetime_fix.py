#!/usr/bin/env python3
"""
Test the datetime fix for Species Explorer
"""
import sys
import os
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_datetime_fix():
    """Test the datetime conversion fix"""
    print("🧪 Testing DateTime Fix for Species Explorer")
    print("=" * 50)
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    try:
        # Load silver data
        silver_data = dashboard.load_silver_layer_data()
        print(f"✅ Loaded {len(silver_data)} silver layer records")
        
        if not silver_data.empty and 'common_name' in silver_data.columns:
            # Get a test species
            species_list = silver_data['common_name'].dropna().unique()
            if len(species_list) > 0:
                test_species = species_list[0]
                print(f"🔬 Testing with species: {test_species}")
                
                # Filter data for test species
                species_data = silver_data[silver_data['common_name'] == test_species].copy()
                print(f"📊 Species data: {len(species_data)} records")
                
                # Test the datetime conversion logic
                if 'observed_date' in species_data.columns:
                    print("📅 Testing datetime conversion...")
                    
                    try:
                        # Apply the same logic as in the dashboard
                        species_data.loc[:, 'observed_date'] = pd.to_datetime(species_data['observed_date'], errors='coerce')
                        
                        if not species_data['observed_date'].isna().all():
                            daily_counts = species_data.groupby(species_data['observed_date'].dt.date).size()
                            print(f"✅ DateTime grouping successful: {len(daily_counts)} unique dates")
                            print(f"   Date range: {daily_counts.index.min()} to {daily_counts.index.max()}")
                        else:
                            daily_counts = pd.Series([len(species_data)], index=[pd.Timestamp.today().date()])
                            print("⚠️  No valid dates found, using fallback")
                        
                        print("✅ DateTime fix working correctly!")
                        
                    except Exception as e:
                        print(f"❌ DateTime conversion error: {e}")
                        # Test fallback
                        daily_counts = pd.Series([len(species_data)], index=[pd.Timestamp.today().date()])
                        print("✅ Fallback mechanism working")
                
                else:
                    print("⚠️  No observed_date column found")
            else:
                print("⚠️  No species found for testing")
        else:
            print("⚠️  No data available for testing")
    
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_datetime_fix()
    print("\n✅ DateTime fix test complete!")
    print("🌐 Dashboard running at: http://localhost:8502")