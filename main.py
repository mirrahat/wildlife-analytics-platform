#!/usr/bin/env python3
"""
Australian Biodiversity Platform - Main Entry Point
===================================================
Simple command-line interface for the Australian wildlife data platform.

Usage:
    python main.py collect    # Collect fresh wildlife data
    python main.py explore    # Explore existing data
    python main.py --help     # Show help
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.collect_wildlife_data import collect_and_store_data as collect_data
from scripts.explore_data import main as explore_data

def show_help():
    """Display usage information"""
    print("Australian Biodiversity Platform")
    print("=" * 35)
    print()
    print("Commands:")
    print("  collect    Collect fresh Australian wildlife data from APIs")
    print("  explore    Explore and analyze collected wildlife data")
    print("  help       Show this help message")
    print()
    print("Examples:")
    print("  python main.py collect")
    print("  python main.py explore")

def main():
    """Main command dispatcher"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'collect':
        print("Starting Australian wildlife data collection...")
        collect_data()
    elif command == 'explore':
        print("Opening wildlife data explorer...")
        explore_data()
    elif command in ['help', '--help', '-h']:
        show_help()
    else:
        print(f"Unknown command: {command}")
        print("Use 'python main.py help' for usage information")

if __name__ == "__main__":
    main()
