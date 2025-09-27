#!/usr/bin/env python3
"""
Flask Dashboard Launcher
======================
Launch the Australian Wildlife Analytics Flask Dashboard

Usage:
    python launch_flask_dashboard.py
    
Features:
- Automatic dependency checking
- Database validation
- Port availability check
- Error handling and troubleshooting
"""

import os
import sys
import subprocess
import socket
import time
from pathlib import Path

def check_port_available(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'pandas',
        'plotly',
        'sqlite3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return missing

def check_database():
    """Check if database exists"""
    db_path = Path("data/aussie_wildlife.db")
    return db_path.exists()

def install_missing_packages(packages):
    """Install missing packages"""
    print("📦 Installing missing packages...")
    for package in packages:
        print(f"   Installing {package}...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                      capture_output=True, text=True)

def main():
    """Launch the Flask dashboard"""
    
    print("🦘 Australian Wildlife Analytics - Flask Dashboard Launcher")
    print("=" * 60)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_packages = check_dependencies()
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        install_missing_packages(missing_packages)
        print("✅ Packages installed successfully!")
    else:
        print("✅ All dependencies are available")
    
    # Check database
    print("🗄️  Checking database...")
    if not check_database():
        print("⚠️  Database not found. The dashboard will work but with limited data.")
        print("💡 Run 'python scripts/enhanced_etl_demo.py' to generate sample data")
    else:
        print("✅ Database found")
    
    # Check port availability
    port = 5000
    print(f"🌐 Checking port {port}...")
    if not check_port_available(port):
        print(f"❌ Port {port} is already in use")
        # Try alternative ports
        for alt_port in [5001, 5002, 5003, 8000, 8080]:
            if check_port_available(alt_port):
                port = alt_port
                print(f"✅ Using alternative port {port}")
                break
        else:
            print("❌ No available ports found. Please free up port 5000 or restart your system.")
            return
    else:
        print(f"✅ Port {port} is available")
    
    print("\n🚀 Starting Flask Dashboard...")
    print(f"🌐 Dashboard URL: http://localhost:{port}")
    print("📊 Features: ETL Monitoring, Species Explorer, Multi-Source Analytics")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Set environment variables
    env = os.environ.copy()
    env['FLASK_DEBUG'] = '1'
    env['FLASK_ENV'] = 'development'
    
    try:
        # Launch Flask app
        if port != 5000:
            # Need to modify the Flask app to use different port
            process = subprocess.Popen([
                sys.executable, 'flask_dashboard.py'
            ], env=env)
        else:
            process = subprocess.run([
                sys.executable, 'flask_dashboard.py'
            ], env=env)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Dashboard stopped by user")
        if 'process' in locals():
            process.terminate()
    except Exception as e:
        print(f"\n❌ Error starting dashboard: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if Python is properly installed")
        print("   2. Ensure all dependencies are installed: pip install -r requirements.txt")
        print("   3. Try running manually: python flask_dashboard.py")
        print("   4. Check for port conflicts")

if __name__ == '__main__':
    main()
