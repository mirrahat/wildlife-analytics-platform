#!/usr/bin/env python3
"""
Dashboard Launcher
=================
Convenient launcher for the Australian Wildlife Analytics Dashboard.

This script:
1. Checks if the database exists
2. Runs the ETL pipeline if needed
3. Launches the Streamlit dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🦘 Australian Wildlife Analytics Dashboard Launcher")
    print("=" * 55)
    
    # Check if database exists
    db_path = Path("data/aussie_wildlife.db")
    
    if not db_path.exists():
        print("⚠️  Database not found! Running ETL pipeline first...")
        print("📊 Collecting data and processing through Bronze → Silver → Gold layers...")
        
        try:
            # Run ETL demo
            result = subprocess.run([sys.executable, "scripts/enhanced_etl_demo.py"], 
                                  capture_output=False, text=True)
            
            if result.returncode == 0:
                print("✅ ETL pipeline completed successfully!")
            else:
                print("❌ ETL pipeline encountered issues, but continuing...")
        
        except Exception as e:
            print(f"⚠️  Error running ETL pipeline: {e}")
            print("Continuing with dashboard launch...")
    
    else:
        print("✅ Database found!")
    
    print("\n🚀 Launching Streamlit Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:8501")
    print("🌐 The dashboard will open automatically in your browser")
    print("\nPress Ctrl+C in the terminal to stop the dashboard")
    print("-" * 55)
    
    try:
        # Launch Streamlit dashboard
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_dashboard.py"])
    
    except KeyboardInterrupt:
        print("\n\n👋 Dashboard stopped. Thanks for using the Australian Wildlife Analytics Platform!")
    
    except Exception as e:
        print(f"\n❌ Error launching dashboard: {e}")
        print("\nTry running manually with: python -m streamlit run streamlit_dashboard.py")

if __name__ == "__main__":
    main()
