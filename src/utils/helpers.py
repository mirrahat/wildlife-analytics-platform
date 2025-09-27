"""
Utility functions for the Australian Biodiversity Platform
==========================================================
Common helper functions used across the platform.
"""

import json
from datetime import datetime
import os

def log_message(message, level="INFO"):
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def save_json_data(data, filename_prefix="wildlife_data"):
    """Save data to a timestamped JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        log_message(f"Data saved to {filename}")
        return filename
    except Exception as e:
        log_message(f"Failed to save data: {e}", "ERROR")
        return None

def validate_australian_coordinates(latitude, longitude):
    """Check if coordinates are within Australian boundaries"""
    if not latitude or not longitude:
        return False
    
    # Rough Australian bounding box
    # Latitude: -44 to -10 (south to north)
    # Longitude: 113 to 154 (west to east)
    if -44 <= latitude <= -10 and 113 <= longitude <= 154:
        return True
    return False

def format_species_name(scientific_name, common_name=None):
    """Format species name for display"""
    if common_name and common_name != "Unknown species":
        return f"{common_name} ({scientific_name})"
    return scientific_name or "Unknown species"

def clean_location_name(location_string):
    """Clean and standardize location names"""
    if not location_string or location_string == "Unknown location":
        return "Location not specified"
    
    # Remove extra whitespace and standardize
    cleaned = " ".join(location_string.split())
    
    # Common abbreviations for Australian states
    state_mappings = {
        " QLD,": " Queensland,",
        " NSW,": " New South Wales,", 
        " VIC,": " Victoria,",
        " SA,": " South Australia,",
        " WA,": " Western Australia,",
        " TAS,": " Tasmania,",
        " NT,": " Northern Territory,",
        " ACT,": " Australian Capital Territory,"
    }
    
    for abbrev, full_name in state_mappings.items():
        cleaned = cleaned.replace(abbrev, full_name)
    
    return cleaned

def calculate_data_freshness(observed_date):
    """Calculate how fresh the observation data is"""
    if not observed_date:
        return "Unknown"
    
    try:
        if isinstance(observed_date, str):
            obs_date = datetime.fromisoformat(observed_date.replace('Z', '+00:00'))
        else:
            obs_date = observed_date
        
        now = datetime.now()
        diff = now - obs_date.replace(tzinfo=None)
        
        if diff.days == 0:
            return "Today"
        elif diff.days == 1:
            return "Yesterday"
        elif diff.days < 7:
            return f"{diff.days} days ago"
        elif diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        else:
            months = diff.days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
    
    except Exception:
        return "Unknown"
