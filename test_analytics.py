#!/usr/bin/env python3
"""Test the advanced analytics module"""

from src.advanced_analytics import AdvancedWildlifeAnalytics

analytics = AdvancedWildlifeAnalytics()
print("Testing advanced analytics module...")

data = analytics.load_comprehensive_data()
print(f"Loaded {len(data)} records")

if not data.empty:
    print(f"Species count: {data['species'].nunique()}")
    print(f"Data sources: {data['data_source'].value_counts().to_dict()}")
    print("Sample data:")
    print(data.head())
else:
    print("No data loaded")
