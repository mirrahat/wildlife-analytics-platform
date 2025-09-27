#!/usr/bin/env python3
"""
🦘 Australian Wildlife Data Collector - Step by Step Version

This script shows you exactly how to get REAL Australian animal data 
from public APIs. No fake data - everything is live from the internet!

We'll start simple and build up gradually so you understand each piece.
"""

import requests
import json
from datetime import datetime, timedelta
import time

def get_aussie_koalas():
    """
    Get real koala sightings from Australia using iNaturalist API
    This is a public API that researchers actually use!
    """
    print("🐨 Searching for recent koala sightings in Australia...")
    
    # iNaturalist API endpoint for observations
    url = "https://api.inaturalist.org/v1/observations"
    
    # Parameters to get Australian koalas from the last 30 days
    params = {
        'taxon_name': 'Phascolarctos cinereus',  # Scientific name for koala
        'place_id': '6744',  # Australia's place ID in iNaturalist
        'per_page': 10,  # Just get 10 recent sightings
        'order': 'desc',  # Most recent first
        'order_by': 'observed_on'
    }
    
    try:
        # Make the API call
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            koala_sightings = data.get('results', [])
            
            print(f"✅ Found {len(koala_sightings)} recent koala sightings!")
            
            # Show the data in a human-friendly way
            for i, sighting in enumerate(koala_sightings, 1):
                location = sighting.get('place_guess', 'Unknown location')
                date = sighting.get('observed_on', 'Unknown date')
                observer = sighting.get('user', {}).get('login', 'Anonymous')
                
                print(f"  {i}. 🐨 Koala spotted in {location}")
                print(f"     📅 Date: {date}")
                print(f"     👤 Reported by: {observer}")
                print()
            
            return koala_sightings
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return []

def get_aussie_kangaroos():
    """
    Get real kangaroo sightings from Australia
    """
    print("🦘 Searching for recent kangaroo sightings in Australia...")
    
    url = "https://api.inaturalist.org/v1/observations"
    
    # Look for any kangaroo species in Australia
    params = {
        'taxon_name': 'Macropus',  # Kangaroo genus
        'place_id': '6744',  # Australia
        'per_page': 5,
        'order': 'desc',
        'order_by': 'observed_on'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            kangaroo_sightings = data.get('results', [])
            
            print(f"✅ Found {len(kangaroo_sightings)} recent kangaroo sightings!")
            
            for i, sighting in enumerate(kangaroo_sightings, 1):
                species = sighting.get('species_guess', 'Kangaroo species')
                location = sighting.get('place_guess', 'Unknown location')
                date = sighting.get('observed_on', 'Unknown date')
                
                print(f"  {i}. 🦘 {species} in {location}")
                print(f"     📅 Date: {date}")
                print()
            
            return kangaroo_sightings
        else:
            print(f"❌ API request failed with status: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return []

def get_biodiversity_summary():
    """
    Get a quick summary of Australian biodiversity from GBIF API
    GBIF is what real scientists use for biodiversity research
    """
    print("📊 Getting Australian biodiversity summary from GBIF...")
    
    # GBIF species search API
    url = "https://api.gbif.org/v1/species/search"
    
    params = {
        'q': 'Australia',
        'limit': 5,
        'kingdom': 'Animalia'  # Just animals for now
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            species = data.get('results', [])
            
            print(f"✅ Found information about Australian species:")
            
            for i, sp in enumerate(species, 1):
                name = sp.get('scientificName', 'Unknown species')
                common_name = sp.get('vernacularName', 'No common name')
                kingdom = sp.get('kingdom', 'Unknown')
                
                print(f"  {i}. 🔬 {name}")
                if common_name != 'No common name':
                    print(f"     🏷️  Common name: {common_name}")
                print(f"     🌍 Kingdom: {kingdom}")
                print()
            
            return species
        else:
            print(f"❌ GBIF API request failed with status: {response.status_code}")
            return []
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return []

def main():
    """
    Main function - this is what runs when you execute the script
    """
    print("🦘 AUSTRALIAN BIODIVERSITY PLATFORM - LIVE DATA COLLECTOR")
    print("=" * 60)
    print("Getting REAL wildlife data from public APIs...")
    print("No fake data - everything you see is live from the internet!")
    print()
    
    # Collect different types of Australian wildlife data
    all_data = {}
    
    # Step 1: Get koala data
    koala_data = get_aussie_koalas()
    all_data['koalas'] = koala_data
    
    print("-" * 40)
    
    # Step 2: Get kangaroo data  
    kangaroo_data = get_aussie_kangaroos()
    all_data['kangaroos'] = kangaroo_data
    
    print("-" * 40)
    
    # Step 3: Get biodiversity summary
    biodiversity_data = get_biodiversity_summary()
    all_data['biodiversity'] = biodiversity_data
    
    print("-" * 40)
    
    # Summary
    total_sightings = len(koala_data) + len(kangaroo_data)
    print(f"🎉 SUMMARY:")
    print(f"   📊 Total recent sightings collected: {total_sightings}")
    print(f"   🐨 Koala sightings: {len(koala_data)}")
    print(f"   🦘 Kangaroo sightings: {len(kangaroo_data)}")
    print(f"   🔬 Species information: {len(biodiversity_data)}")
    print()
    print("✅ That's REAL Australian wildlife data from live APIs!")
    print("🔄 Next step: We'll add a database to store this data...")
    
    return all_data

if __name__ == "__main__":
    # This runs when you execute: python collect_aussie_wildlife.py
    wildlife_data = main()
    
    # Optional: Save to a simple JSON file for now
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"australian_wildlife_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(wildlife_data, f, indent=2, default=str)
        print(f"📁 Data also saved to: {filename}")
    except Exception as e:
        print(f"⚠️  Couldn't save file: {e}")
