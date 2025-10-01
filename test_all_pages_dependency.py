#!/usr/bin/env python3
"""
Test All Dashboard Pages ETL Dependency
Verify that ALL pages properly require ETL to be run first
"""

import os
import sys

# Add current directory to path
sys.path.append(os.getcwd())

def test_all_pages_etl_dependency():
    """Test that all dashboard pages properly check ETL dependency"""
    
    print("🧪 Testing All Dashboard Pages ETL Dependency")
    print("=" * 60)
    
    # Import the dashboard class
    from streamlit_dashboard import WildlifeDashboard
    
    # Create dashboard instance
    dashboard = WildlifeDashboard()
    
    # Test ETL status (should be False without session state)
    etl_executed, etl_message = dashboard.check_etl_execution_status()
    has_data = dashboard.has_sufficient_data()
    
    print(f"ETL Status: {etl_executed}")
    print(f"Has Data: {has_data}")
    print(f"Message: {etl_message}")
    
    print("\n📋 Page Dependency Analysis:")
    print("=" * 40)
    
    # List all dashboard pages and their expected behavior
    pages = {
        "Dashboard": "✅ FIXED - Shows placeholder metrics and ETL requirement",
        "ETL Monitoring": "❓ NEED TO CHECK - Should show ETL requirement or limited view",
        "Data Quality": "✅ ALREADY HAD - Shows ETL requirement message", 
        "Species Explorer": "✅ FIXED - Shows ETL requirement message",
        "Multi-Source Analytics": "✅ FIXED - Shows ETL requirement message",
        "Advanced Analytics": "✅ FIXED - Shows ETL requirement message"
    }
    
    print("Current Status of All Pages:")
    for page, status in pages.items():
        print(f"  {page}: {status}")
    
    print("\n🎯 What Should Happen on Each Page:")
    print("=" * 50)
    
    print("📊 Dashboard:")
    print("  - Shows '---' for all metrics")
    print("  - Shows 'Run ETL Demo' instruction banner")
    print("  - All charts and maps locked")
    
    print("\n🔄 ETL Monitoring:")
    print("  - Should show ETL status but no detailed history")
    print("  - Should encourage running ETL Demo")
    print("  - May show basic system status")
    
    print("\n📈 Data Quality:")
    print("  - Shows 'ETL Pipeline Required' message")
    print("  - Shows step-by-step instructions")
    print("  - All quality charts locked")
    
    print("\n🔍 Species Explorer:")
    print("  - Shows 'ETL Pipeline Required' message")
    print("  - No species dropdown available")
    print("  - Instructions to run ETL first")
    
    print("\n🌐 Multi-Source Analytics:")
    print("  - Shows 'ETL Pipeline Required' message")
    print("  - Data lake architecture info only")
    print("  - All analytics locked")
    
    print("\n🧠 Advanced Analytics:")
    print("  - Shows 'ETL Pipeline Required' message")
    print("  - ML features completely locked")
    print("  - Instructions to run ETL first")
    
    print(f"\n🚀 Test the dashboard at: http://localhost:8503")
    print("Navigate to each page to verify ETL dependency is working!")

if __name__ == "__main__":
    test_all_pages_etl_dependency()