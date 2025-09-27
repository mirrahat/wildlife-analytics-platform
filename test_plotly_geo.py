#!/usr/bin/env python3
"""
Test Plotly Geo Scope Issue
=============================
Test to isolate the 'australia' scope error in Plotly.
"""

import plotly.graph_objects as go

# Test creating a simple map with different scope values
print("Testing Plotly geo scopes...")

# Test with 'oceania' (should work)
try:
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lon=[-25],
        lat=[135],
        mode='markers',
        name="Test Point"
    ))
    
    fig.update_layout(
        title="Test Map with Oceania Scope",
        geo=dict(
            scope='oceania',
            showland=True,
            landcolor='lightgray'
        )
    )
    print("✅ 'oceania' scope works correctly")
    
except Exception as e:
    print(f"❌ Error with 'oceania' scope: {e}")

# Test with 'australia' (should fail)
try:
    fig2 = go.Figure()
    fig2.add_trace(go.Scattergeo(
        lon=[-25],
        lat=[135],
        mode='markers',
        name="Test Point"
    ))
    
    fig2.update_layout(
        title="Test Map with Australia Scope",
        geo=dict(
            scope='australia',  # This should fail
            showland=True,
            landcolor='lightgray'
        )
    )
    print("✅ 'australia' scope works (unexpected)")
    
except Exception as e:
    print(f"❌ Error with 'australia' scope (expected): {e}")

print("\nPlotly version info:")
import plotly
print(f"Plotly version: {plotly.__version__}")

print("\nValid geo scopes according to Plotly:")
print("['africa', 'antarctica', 'asia', 'europe', 'north america', 'oceania', 'south america', 'usa', 'world']")
