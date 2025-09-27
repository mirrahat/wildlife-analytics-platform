#!/usr/bin/env python3
"""
🦘 STEP 1: Simple Australian Wildlife Data Collector
===================================================
This is your first step! Run this file to see real Australian animal data.

What this does:
1. Connects to a free wildlife API (iNaturalist)
2. Asks for recent Australian animal sightings
3. Shows you real data about koalas, kangaroos, etc.
4. Saves the data to a simple file

This teaches you: How to collect real wildlife data from the internet
"""

import requests
import json
from datetime import datetime
import os

def collect_australian_wildlife():
    """Collect recent Australian wildlife sightings from iNaturalist API"""
    
    print("🦘 AUSTRALIAN WILDLIFE DATA COLLECTOR")
    print("=" * 45)
    print("Step 1: Learning to collect real animal data")
    print()
    
    # This is the API endpoint - like asking a question to a wildlife database
    api_url = "https://api.inaturalist.org/v1/observations"
    
    # These are our search parameters - what we want to find
    params = {
        'place_id': 6744,        # Australia's place ID in iNaturalist
        'per_page': 10,          # Get 10 recent sightings
        'order': 'desc',         # Most recent first
        'order_by': 'created_at' # Sorted by when they were spotted
    }
    
    print("🔍 Searching for recent Australian wildlife sightings...")
    print(f"   API: {api_url}")
    print(f"   Location: Australia (place_id: {params['place_id']})")
    print()
    
    try:
        # Make the request - like asking the API for data
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            observations = data.get('results', [])
            
            print(f"✅ Found {len(observations)} recent wildlife sightings!")
            print()
            
            # Let's look at each animal sighting
            wildlife_data = []
            
            for i, obs in enumerate(observations, 1):
                # Extract the important information
                species_name = "Unknown species"
                if obs.get('taxon') and obs['taxon'].get('name'):
                    species_name = obs['taxon']['name']
                
                common_name = "No common name"
                if obs.get('taxon') and obs['taxon'].get('preferred_common_name'):
                    common_name = obs['taxon']['preferred_common_name']
                
                location = "Unknown location"
                if obs.get('place_guess'):
                    location = obs['place_guess']
                
                date_observed = "Unknown date"
                if obs.get('observed_on'):
                    date_observed = obs['observed_on']
                
                # Create a simple record
                animal_record = {
                    'species_name': species_name,
                    'common_name': common_name,
                    'location': location,
                    'date_observed': date_observed,
                    'observer': obs.get('user', {}).get('login', 'Anonymous')
                }
                
                wildlife_data.append(animal_record)
                
                # Show the user what we found
                print(f"🐾 Sighting #{i}:")
                print(f"   Species: {species_name}")
                print(f"   Common Name: {common_name}")
                print(f"   Location: {location}")
                print(f"   Date: {date_observed}")
                print(f"   Spotted by: {animal_record['observer']}")
                print()
            
            # Save the data to a file so you can see it later
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"australian_wildlife_{timestamp}.json"
            
            with open(filename, 'w') as f:
                json.dump(wildlife_data, f, indent=2)
            
            print(f"💾 Data saved to: {filename}")
            print(f"📁 File location: {os.path.abspath(filename)}")
            print()
            print("🎉 SUCCESS! You just collected real Australian wildlife data!")
            print()
            print("📋 What you learned:")
            print("   • How to connect to wildlife APIs")
            print("   • How to search for Australian animals") 
            print("   • How to extract and organize animal data")
            print("   • How to save data for later use")
            print()
            print("🔄 NEXT STEP: We'll add a database to store this data properly!")
            
            return wildlife_data
            
        else:
            print(f"❌ API request failed with status code: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        print("💡 Check your internet connection and try again")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def show_summary(data):
    """Show a summary of what we collected"""
    if not data:
        return
    
    print("📊 SUMMARY OF WHAT WE COLLECTED:")
    print("-" * 35)
    
    # Count different types of animals
    species_count = {}
    locations = set()
    
    for record in data:
        species = record['common_name']
        if species != "No common name":
            species_count[species] = species_count.get(species, 0) + 1
        locations.add(record['location'])
    
    print(f"🐾 Total sightings: {len(data)}")
    print(f"🌏 Different locations: {len(locations)}")
    print(f"🦎 Different species: {len(species_count)}")
    
    if species_count:
        print("\n🏆 Most commonly spotted:")
        for species, count in sorted(species_count.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   • {species}: {count} sighting(s)")

if __name__ == "__main__":
    print("🚀 Starting your Australian Biodiversity Platform - Step 1")
    print()
    
    # Collect the data
    wildlife_data = collect_australian_wildlife()
    
    # Show summary
    if wildlife_data:
        print()
        show_summary(wildlife_data)
        
        print()
        print("🎯 Ready for Step 2?")
        print("   Next we'll add a database to store all this data properly!")
        print("   Run: python step2_add_database.py (when we create it)")
    
    print()
    input("Press Enter to finish...")
