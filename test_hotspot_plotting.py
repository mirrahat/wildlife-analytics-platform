#!/usr/bin/env python3
"""
Minimal Test for Dashboard Hotspot Plotting
==========================================
Extract just the hotspot plotting code to test in isolation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import sqlite3
import plotly.graph_objects as go
from src.advanced_analytics import AdvancedWildlifeAnalytics

def test_hotspot_plotting():
    """Test the exact hotspot plotting code from the dashboard"""
    
    print("🧪 Testing hotspot plotting code...")
    
    # Initialize analytics
    analytics = AdvancedWildlifeAnalytics()
    
    # Load data
    data = analytics.load_comprehensive_data()
    print(f"✅ Loaded {len(data)} records")
    
    if len(data) > 0:
        # Detect hotspots
        hotspots = analytics.detect_biodiversity_hotspots(data.head(100), 50, 5)
        print(f"✅ Detected {len(hotspots)} hotspots")
        
        if hotspots:
            # Reproduce the EXACT plotting code from the dashboard
            try:
                fig = go.Figure()
                
                # Add hotspots to map
                for hotspot in hotspots:
                    fig.add_trace(go.Scattergeo(
                        lon=[hotspot.center_lon],
                        lat=[hotspot.center_lat],
                        text=f"Species: {hotspot.species_count}<br>Priority: {hotspot.conservation_priority:.2f}",
                        mode='markers',
                        marker=dict(
                            size=10 + hotspot.conservation_priority * 20,
                            color=hotspot.conservation_priority,
                            colorscale='Viridis',
                            showscale=True,
                            colorbar=dict(title="Priority Score")
                        ),
                        name="Biodiversity Hotspots"
                    ))
                
                # This is the exact code from line 1612 in streamlit_dashboard.py
                fig.update_layout(
                    title="🌍 Australian Biodiversity Hotspots",
                    geo=dict(
                        scope='oceania',
                        showland=True,
                        landcolor='lightgray',
                        coastlinecolor='black',
                        projection_type='natural earth'
                    ),
                    height=500
                )
                
                print("✅ Hotspot plotting code works correctly")
                print("🎉 The error must be coming from somewhere else")
                
            except Exception as e:
                print(f"❌ Error in hotspot plotting: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("ℹ️ No hotspots to plot")
    else:
        print("ℹ️ No data to analyze")

if __name__ == "__main__":
    test_hotspot_plotting()
