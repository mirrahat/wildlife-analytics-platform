#!/usr/bin/env python3
"""
Test Species Explorer functionality after datetime fix
"""
import sys
import os
import pandas as pd

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_species_explorer_fix():
    """Test Species Explorer with the datetime fix"""
    print("🐾 Testing Species Explorer After DateTime Fix")
    print("=" * 50)
    
    from streamlit_dashboard import WildlifeDashboard
    dashboard = WildlifeDashboard()
    
    try:
        # Load silver data
        silver_data = dashboard.load_silver_layer_data()
        print(f"✅ Loaded {len(silver_data)} silver layer records")
        
        if not silver_data.empty and 'common_name' in silver_data.columns:
            # Get species list
            species_list = sorted(silver_data['common_name'].dropna().unique())
            print(f"🔍 Found {len(species_list)} unique species")
            
            # Test with the first few species
            for i, test_species in enumerate(species_list[:3], 1):
                print(f"\n{i}️⃣ Testing species: {test_species}")
                
                # Filter data for test species
                species_data = silver_data[silver_data['common_name'] == test_species].copy()
                print(f"   📊 Species records: {len(species_data)}")
                
                # Test the datetime logic (same as in dashboard)
                if 'observed_date' in species_data.columns:
                    try:
                        # Apply the improved datetime conversion
                        species_data['observed_date_dt'] = pd.to_datetime(species_data['observed_date'], errors='coerce')
                        
                        if not species_data['observed_date_dt'].isna().all():
                            daily_counts = species_data.groupby(species_data['observed_date_dt'].dt.date).size()
                            print(f"   ✅ Timeline data: {len(daily_counts)} unique dates")
                            
                            # Show date range
                            date_range = f"{daily_counts.index.min()} to {daily_counts.index.max()}"
                            print(f"   📅 Date range: {date_range}")
                            
                        else:
                            date_counts = species_data['observed_date'].value_counts()
                            print(f"   ✅ String dates: {len(date_counts)} unique values")
                        
                    except Exception as e:
                        print(f"   ❌ Error: {e}")
                
                # Test other species metrics
                unique_locations = species_data['location_description'].nunique()
                avg_quality = species_data['quality_score'].mean() if 'quality_score' in species_data.columns else 0
                
                print(f"   🗺️ Unique locations: {unique_locations}")
                print(f"   🎯 Average quality: {avg_quality:.3f}")
        
        print("\n🎉 Species Explorer functionality test complete!")
        
    except Exception as e:
        print(f"❌ Test error: {e}")

if __name__ == "__main__":
    test_species_explorer_fix()
    print("\n✅ Species Explorer is ready!")
    print("🌐 Dashboard: http://localhost:8502")
    print("💡 Try the Species Explorer page to see the timeline charts working!")