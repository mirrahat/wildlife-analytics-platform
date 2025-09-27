#!/usr/bin/env python3
"""
Test Suite for Australian Wildlife Data Collectors
==================================================
Unit tests for the data collection modules.
"""

import unittest
import sys
import os

# Add src directory to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from collectors.inaturalist_collector import iNaturalistCollector
from database.wildlife_db import AustralianWildlifeDB

class TestDataCollectors(unittest.TestCase):
    """Test cases for data collection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.collector = iNaturalistCollector()
        self.test_db = AustralianWildlifeDB(":memory:")  # In-memory test database
    
    def test_collector_initialization(self):
        """Test that collector initializes correctly"""
        self.assertIsNotNone(self.collector)
        self.assertEqual(self.collector.base_url, "https://api.inaturalist.org/v1/observations")
    
    def test_database_initialization(self):
        """Test that database initializes correctly"""
        self.assertIsNotNone(self.test_db)
        # Test that tables were created
        total_count = self.test_db.get_total_count()
        self.assertEqual(total_count, 0)
    
    def test_api_parameters(self):
        """Test API parameter construction"""
        params = self.collector._build_search_params(
            species="Phascolarctos cinereus",
            location="Australia",
            limit=10
        )
        
        self.assertIn('taxon_name', params)
        self.assertIn('place_id', params)
        self.assertEqual(params['per_page'], 10)

class TestDatabaseOperations(unittest.TestCase):
    """Test cases for database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.test_db = AustralianWildlifeDB(":memory:")
    
    def test_save_sighting(self):
        """Test saving a wildlife sighting"""
        test_sighting = {
            'id': 12345,
            'species_guess': 'Test Koala',
            'taxon': {'name': 'Phascolarctos cinereus'},
            'place_guess': 'Test Location, QLD',
            'observed_on': '2025-09-27',
            'user': {'login': 'test_user'},
            'geojson': {'coordinates': [153.0, -27.5]}
        }
        
        result = self.test_db.save_wildlife_sighting(test_sighting)
        self.assertTrue(result)
        
        # Check that it was saved
        total_count = self.test_db.get_total_count()
        self.assertEqual(total_count, 1)

if __name__ == '__main__':
    unittest.main()
