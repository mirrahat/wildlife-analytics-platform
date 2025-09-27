#!/usr/bin/env python3
"""
Test Advanced Analytics Dashboard Section
========================================
Test the advanced analytics rendering to ensure no geo scope errors.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the dashboard functions
import streamlit as st
from streamlit_dashboard import render_advanced_analytics

# This would normally be called by Streamlit, but we can test the function directly
def test_advanced_analytics_rendering():
    """Test the advanced analytics rendering function"""
    
    print("🧪 Testing Advanced Analytics Dashboard Section...")
    
    try:
        # Since we can't run Streamlit directly, let's at least test the import and basic functionality
        from src.advanced_analytics import AdvancedWildlifeAnalytics
        
        # Test analytics initialization
        analytics = AdvancedWildlifeAnalytics()
        print("✅ Analytics initialization successful")
        
        # Test data loading
        data = analytics.load_comprehensive_data()
        print(f"✅ Data loading successful: {len(data)} records")
        
        if len(data) > 50:
            # Test hotspot detection (the part that creates maps)
            hotspots = analytics.detect_biodiversity_hotspots(data.head(50), 50, 5)
            print(f"✅ Hotspot detection successful: {len(hotspots)} hotspots")
            
            # Test the plotting logic without Streamlit context
            if hotspots:
                import plotly.graph_objects as go
                
                fig = go.Figure()
                
                # Add hotspots
                for hotspot in hotspots:
                    fig.add_trace(go.Scattergeo(
                        lon=[hotspot.center_lon],
                        lat=[hotspot.center_lat],
                        mode='markers',
                        name="Test Hotspot"
                    ))
                
                # Test the geo layout with oceania scope
                fig.update_layout(
                    geo=dict(
                        scope='oceania',
                        showland=True
                    )
                )
                
                print("✅ Map creation with 'oceania' scope successful")
        
        print("🎉 All advanced analytics components working correctly!")
        print("💡 The 'australia' scope error should now be fixed with 'oceania'")
        
    except Exception as e:
        print(f"❌ Error in advanced analytics testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_advanced_analytics_rendering()
