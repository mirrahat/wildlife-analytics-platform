#!/usr/bin/env python3
"""
Wildlife Data Explorer Script
============================
Interactive script for exploring and analyzing collected wildlife data.

This script provides:
- Database summary and statistics
- Species-specific analysis
- Interactive exploration interface
- Location and temporal insights

Usage:
    python explore_data.py
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from analysis.data_explorer import WildlifeAnalyzer

def main():
    """Main exploration interface"""
    
    print("AUSTRALIAN WILDLIFE DATA EXPLORER")
    print("=" * 40)
    print("Exploring your collected wildlife observation data...")
    print()
    
    # Initialize the analyzer
    analyzer = WildlifeAnalyzer()
    
    # Show the main summary report
    analyzer.generate_summary_report()
    
    # Interactive mode
    print(f"\n" + "=" * 40)
    print("INTERACTIVE MODE")
    print("=" * 40)
    print("Available commands:")
    print("  - Type a species name (e.g., 'Koala') to see detailed analysis")
    print("  - Type 'summary' to see the full report again")
    print("  - Type 'help' to see these commands again")
    print("  - Type 'quit' to exit")
    
    while True:
        try:
            command = input("\nEnter command > ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                print("Thanks for exploring Australian wildlife data!")
                break
                
            elif command.lower() == 'summary':
                print()
                analyzer.generate_summary_report()
                
            elif command.lower() == 'help':
                print("\nAvailable commands:")
                print("  - Species name: Analyze specific species (e.g., 'Koala', 'Eastern Grey Kangaroo')")
                print("  - 'summary': Show full database report")
                print("  - 'help': Show this help message")
                print("  - 'quit': Exit the explorer")
                
            elif command:
                print()
                analyzer.analyze_species_trends(command)
                
        except KeyboardInterrupt:
            print("\nThanks for exploring Australian wildlife data!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print("Type 'help' for available commands.")

if __name__ == "__main__":
    main()
