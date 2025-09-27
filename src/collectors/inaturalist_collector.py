#!/usr/bin/env python3
"""
iNaturalist Data Collector
==========================
Collects Australian wildlife observations from the iNaturalist API.

This module handles:
- API authentication and rate limiting
- Species-specific data collection (koalas, kangaroos, etc.)
- Data validation and cleaning
- Error handling for network issues

Part of the Australian Biodiversity Analytics Platform.
"""

import requests
import json
from datetime import datetime
import time

class iNaturalistCollector:
    """
    Collects wildlife observation data from iNaturalist API.
    Focuses on Australian species and locations.
    """
    
    def __init__(self):
        self.base_url = "https://api.inaturalist.org/v1/observations"
        self.australia_place_id = "6744"
        self.request_delay = 1  # Be nice to the API
    
    def collect_species_data(self, scientific_name, common_name, limit=20):
        """
        Collect recent observations for a specific species in Australia.
        
        Args:
            scientific_name (str): Scientific name (e.g., 'Phascolarctos cinereus')
            common_name (str): Common name for logging (e.g., 'Koala')
            limit (int): Maximum number of observations to collect
            
        Returns:
            list: List of observation dictionaries
        """
        print(f"Collecting {common_name} data from iNaturalist...")
        
        params = {
            'taxon_name': scientific_name,
            'place_id': self.australia_place_id,
            'per_page': limit,
            'order': 'desc',
            'order_by': 'observed_on'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                observations = data.get('results', [])
                
                print(f"Retrieved {len(observations)} {common_name} observations")
                
                # Add a small delay to be respectful to the API
                time.sleep(self.request_delay)
                
                return observations
            else:
                print(f"API request failed with status: {response.status_code}")
                return []
                
        except requests.RequestException as e:
            print(f"Network error collecting {common_name} data: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def collect_koala_data(self, limit=20):
        """Collect koala observations from Australia"""
        return self.collect_species_data(
            'Phascolarctos cinereus', 
            'Koala', 
            limit
        )
    
    def collect_kangaroo_data(self, limit=15):
        """Collect kangaroo and wallaby observations from Australia"""
        return self.collect_species_data(
            'Macropus', 
            'Kangaroo/Wallaby', 
            limit
        )
    
    def collect_multiple_species(self, species_list):
        """
        Collect data for multiple species.
        
        Args:
            species_list (list): List of (scientific_name, common_name, limit) tuples
            
        Returns:
            dict: Dictionary with common names as keys and observation lists as values
        """
        all_data = {}
        
        for scientific_name, common_name, limit in species_list:
            observations = self.collect_species_data(scientific_name, common_name, limit)
            all_data[common_name] = observations
        
        return all_data

if __name__ == "__main__":
    # Example usage
    collector = iNaturalistCollector()
    
    print("AUSTRALIAN WILDLIFE DATA COLLECTOR")
    print("=" * 40)
    
    # Collect koala data
    koala_data = collector.collect_koala_data(10)
    
    # Collect kangaroo data
    kangaroo_data = collector.collect_kangaroo_data(10)
    
    print(f"\nCollected {len(koala_data)} koala observations")
    print(f"Collected {len(kangaroo_data)} kangaroo observations")
    
    if koala_data or kangaroo_data:
        print("\nSample recent sightings:")
        for obs in (koala_data + kangaroo_data)[:3]:
            species = obs.get('species_guess', 'Unknown species')
            location = obs.get('place_guess', 'Unknown location')
            date = obs.get('observed_on', 'Unknown date')
            print(f"  {species} in {location} on {date}")
