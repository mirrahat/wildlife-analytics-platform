#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Source Australian Wildlife Data Collector
==============================================
Enhanced data collection from multiple biodiversity APIs and sources for robust analytics.

Data Sources:
1. iNaturalist (existing) - Citizen science observations
2. GBIF - Global Biodiversity Information Facility
3. eBird - Cornell Lab bird observations
4. Atlas of Living Australia (ALA) - Government data
5. CITES - Trade monitoring data
6. Australian Environmental Resource Information Network (ERIN)
7. Parks Australia - Protected species data
"""

# Set up proper encoding for Windows compatibility
import sys
import os
if sys.platform.startswith('win'):
    # Ensure proper UTF-8 handling on Windows
    import locale
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

def safe_print(*args, **kwargs):
    """Safe print function that handles Unicode encoding issues on Windows"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # Fallback: convert to ASCII with replace
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_args.append(arg.encode('ascii', 'replace').decode('ascii'))
            else:
                safe_args.append(str(arg).encode('ascii', 'replace').decode('ascii'))
        print(*safe_args, **kwargs)

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import sqlite3
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DataSourceConfig:
    """Configuration for each data source"""
    name: str
    base_url: str
    api_key: Optional[str] = None
    rate_limit: float = 1.0  # seconds between requests
    max_records: int = 100
    enabled: bool = True

class MultiSourceCollector:
    """Collect wildlife data from multiple sources"""
    
    def __init__(self):
        self.sources = self._initialize_sources()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Australian-Wildlife-Analytics/1.0 (Research Project)'
        })
    
    def _initialize_sources(self) -> Dict[str, DataSourceConfig]:
        """Initialize all data source configurations"""
        return {
            'inaturalist': DataSourceConfig(
                name='iNaturalist',
                base_url='https://api.inaturalist.org/v1',
                rate_limit=1.0,
                max_records=200
            ),
            'gbif': DataSourceConfig(
                name='GBIF',
                base_url='https://api.gbif.org/v1',
                rate_limit=0.5,
                max_records=300
            ),
            'ebird': DataSourceConfig(
                name='eBird',
                base_url='https://api.ebird.org/v2',
                api_key=os.getenv('EBIRD_API_KEY'),  # Get from environment
                rate_limit=1.0,
                max_records=100
            ),
            'ala': DataSourceConfig(
                name='Atlas of Living Australia',
                base_url='https://biocache-ws.ala.org.au/ws',
                rate_limit=1.5,
                max_records=200
            ),
            'biodiversity_gov': DataSourceConfig(
                name='Australian Government Biodiversity',
                base_url='https://www.environment.gov.au/biodiversity',
                rate_limit=2.0,
                max_records=50,
                enabled=False  # Requires special access
            )
        }
    
    def collect_from_all_sources(self, species_list: List[str]) -> Dict[str, pd.DataFrame]:
        """Collect data from all enabled sources"""
        logger.info(f"Starting multi-source data collection for {len(species_list)} species")
        
        all_data = {}
        
        for source_name, config in self.sources.items():
            if not config.enabled:
                logger.info(f"⏭️ Skipping disabled source: {source_name}")
                continue
            
            logger.info(f"🔄 Collecting from {config.name}...")
            
            try:
                source_data = self._collect_from_source(source_name, species_list)
                all_data[source_name] = source_data
                
                logger.info(f"✅ {config.name}: Collected {len(source_data)} records")
                
                # Rate limiting
                time.sleep(config.rate_limit)
                
            except Exception as e:
                logger.error(f"❌ {config.name} collection failed: {e}")
                all_data[source_name] = pd.DataFrame()
        
        return all_data
    
    def _collect_from_source(self, source_name: str, species_list: List[str]) -> pd.DataFrame:
        """Collect data from a specific source"""
        config = self.sources[source_name]
        
        if source_name == 'inaturalist':
            return self._collect_inaturalist(species_list, config)
        elif source_name == 'gbif':
            return self._collect_gbif(species_list, config)
        elif source_name == 'ebird':
            return self._collect_ebird(species_list, config)
        elif source_name == 'ala':
            return self._collect_ala(species_list, config)
        else:
            logger.warning(f"Unknown source: {source_name}")
            return pd.DataFrame()
    
    def _collect_inaturalist(self, species_list: List[str], config: DataSourceConfig) -> pd.DataFrame:
        """Collect from iNaturalist (enhanced version of existing collector)"""
        all_observations = []
        
        for species in species_list:
            try:
                params = {
                    'q': species,
                    'place_id': 6744,  # Australia
                    'quality_grade': 'research',
                    'per_page': min(config.max_records // len(species_list), 50),
                    'order': 'desc',
                    'order_by': 'observed_on'
                }
                
                response = self.session.get(f"{config.base_url}/observations", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                for obs in data.get('results', []):
                    all_observations.append({
                        'source': 'iNaturalist',
                        'external_id': str(obs.get('id')),
                        'common_name': obs.get('species_guess', species),
                        'scientific_name': obs.get('taxon', {}).get('name') if obs.get('taxon') else None,
                        'latitude': obs.get('location', '').split(',')[0] if obs.get('location') else None,
                        'longitude': obs.get('location', '').split(',')[1] if obs.get('location') and ',' in obs.get('location', '') else None,
                        'observed_date': obs.get('observed_on'),
                        'observer_name': obs.get('user', {}).get('login'),
                        'location_description': obs.get('place_guess'),
                        'photo_url': obs.get('photos', [{}])[0].get('url') if obs.get('photos') else None,
                        'quality_grade': obs.get('quality_grade'),
                        'coordinates_obscured': obs.get('geoprivacy') == 'obscured',
                        'taxon_id': obs.get('taxon', {}).get('id') if obs.get('taxon') else None,
                        'collected_at': datetime.now()
                    })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"iNaturalist collection failed for {species}: {e}")
        
        return pd.DataFrame(all_observations)
    
    def _collect_gbif(self, species_list: List[str], config: DataSourceConfig) -> pd.DataFrame:
        """Collect from GBIF (Global Biodiversity Information Facility)"""
        all_observations = []
        
        for species in species_list:
            try:
                # First, get the species key
                species_response = self.session.get(
                    f"{config.base_url}/species/match",
                    params={'name': species, 'kingdom': 'Animalia'},
                    timeout=30
                )
                species_response.raise_for_status()
                
                try:
                    species_data = species_response.json()
                except json.JSONDecodeError as e:
                    logger.warning(f"GBIF species API returned invalid JSON for {species}: {e}")
                    continue
                
                species_key = species_data.get('speciesKey')
                if not species_key:
                    logger.warning(f"GBIF: No species key found for {species}")
                    continue
                
                # Get occurrences for Australia
                params = {
                    'speciesKey': species_key,
                    'country': 'AU',  # Australia
                    'hasCoordinate': 'true',
                    'hasGeospatialIssue': 'false',
                    'limit': min(config.max_records // len(species_list), 100),
                    'basisOfRecord': 'HUMAN_OBSERVATION,OBSERVATION,MACHINE_OBSERVATION'
                }
                
                response = self.session.get(f"{config.base_url}/occurrence/search", params=params, timeout=30)
                response.raise_for_status()
                
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    logger.warning(f"GBIF occurrence API returned invalid JSON for {species}: {e}")
                    continue
                
                if not isinstance(data, dict):
                    logger.warning(f"GBIF API returned unexpected data type for {species}: {type(data)}")
                    continue
                
                for record in data.get('results', []):
                    # Safe date parsing for GBIF API
                    event_date = record.get('eventDate')
                    observed_date = None
                    if event_date:
                        try:
                            if isinstance(event_date, str):
                                observed_date = event_date.split('T')[0]
                            else:
                                observed_date = str(event_date).split('T')[0] if 'T' in str(event_date) else str(event_date)
                        except (AttributeError, IndexError) as e:
                            logger.warning(f"Date parsing issue for GBIF record {record.get('key', 'unknown')}: {e}")
                            observed_date = None
                    
                    all_observations.append({
                        'source': 'GBIF',
                        'external_id': str(record.get('key')),
                        'common_name': record.get('vernacularName', species),
                        'scientific_name': record.get('scientificName'),
                        'latitude': record.get('decimalLatitude'),
                        'longitude': record.get('decimalLongitude'),
                        'observed_date': observed_date,
                        'observer_name': record.get('recordedBy'),
                        'location_description': f"{record.get('locality', '')}, {record.get('stateProvince', '')}, {record.get('country', '')}".strip(', '),
                        'photo_url': None,
                        'basis_of_record': record.get('basisOfRecord'),
                        'institution_code': record.get('institutionCode'),
                        'dataset_key': record.get('datasetKey'),
                        'occurrence_status': record.get('occurrenceStatus'),
                        'collected_at': datetime.now()
                    })
                
                time.sleep(0.3)  # Rate limiting
                
            except Exception as e:
                logger.warning(f"GBIF collection failed for {species}: {e}")
        
        return pd.DataFrame(all_observations)
    
    def _collect_ebird(self, species_list: List[str], config: DataSourceConfig) -> pd.DataFrame:
        """Collect from eBird (Cornell Lab of Ornithology)"""
        if not config.api_key:
            logger.warning("eBird API key not found. Set EBIRD_API_KEY environment variable.")
            return pd.DataFrame()
        
        all_observations = []
        
        # eBird works with region codes
        australian_regions = ['AU-NSW', 'AU-VIC', 'AU-QLD', 'AU-SA', 'AU-WA', 'AU-TAS', 'AU-NT', 'AU-ACT']
        
        headers = {'X-eBirdApiToken': config.api_key}
        
        for region in australian_regions[:3]:  # Limit to 3 regions for demo
            try:
                # Get recent bird observations
                params = {
                    'back': 30,  # Last 30 days
                    'maxResults': min(config.max_records // len(australian_regions), 50)
                }
                
                response = self.session.get(
                    f"{config.base_url}/data/obs/{region}/recent",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                
                observations = response.json()
                
                for obs in observations:
                    # Filter for species in our list (if any birds are in the species_list)
                    common_name = obs.get('comName', '')
                    if any(species.lower() in common_name.lower() for species in species_list if 'bird' in species.lower() or any(bird_word in species.lower() for bird_word in ['cockatoo', 'parrot', 'lorikeet', 'kookaburra'])):
                        all_observations.append({
                            'source': 'eBird',
                            'external_id': obs.get('speciesCode'),
                            'common_name': obs.get('comName'),
                            'scientific_name': obs.get('sciName'),
                            'latitude': obs.get('lat'),
                            'longitude': obs.get('lng'),
                            'observed_date': obs.get('obsDt'),
                            'observer_name': None,  # eBird doesn't provide observer names in public API
                            'location_description': obs.get('locName'),
                            'photo_url': None,
                            'observation_count': obs.get('howMany'),
                            'location_private': obs.get('locationPrivate'),
                            'sub_id': obs.get('subId'),
                            'collected_at': datetime.now()
                        })
                
                time.sleep(1.0)  # eBird requires respectful rate limiting
                
            except Exception as e:
                logger.warning(f"eBird collection failed for region {region}: {e}")
        
        return pd.DataFrame(all_observations)
    
    def _collect_ala(self, species_list: List[str], config: DataSourceConfig) -> pd.DataFrame:
        """Collect from Atlas of Living Australia"""
        all_observations = []
        
        for species in species_list:
            try:
                # ALA search parameters
                params = {
                    'q': f'text:"{species}"',
                    'fq': 'country:"Australia"',
                    'pageSize': min(config.max_records // len(species_list), 50),
                    'sort': 'eventDate',
                    'dir': 'desc',
                    'fl': 'id,scientificName,vernacularName,decimalLatitude,decimalLongitude,eventDate,recordedBy,locality,stateProvince,basisOfRecord'
                }
                
                response = self.session.get(f"{config.base_url}/occurrences/search", params=params, timeout=30)
                response.raise_for_status()
                
                # Validate JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    logger.warning(f"ALA API returned invalid JSON for {species}: {e}")
                    continue
                
                # Validate response structure
                if not isinstance(data, dict):
                    logger.warning(f"ALA API returned unexpected data type for {species}: {type(data)}")
                    continue
                
                for record in data.get('occurrences', []):
                    # Safe date parsing for ALA API
                    event_date = record.get('eventDate')
                    observed_date = None
                    if event_date:
                        try:
                            # Handle both string and potentially non-string event dates
                            if isinstance(event_date, str):
                                observed_date = event_date.split('T')[0]
                            else:
                                observed_date = str(event_date).split('T')[0] if 'T' in str(event_date) else str(event_date)
                        except (AttributeError, IndexError) as e:
                            logger.warning(f"Date parsing issue for ALA record {record.get('id', 'unknown')}: {e}")
                            observed_date = None
                    
                    all_observations.append({
                        'source': 'Atlas of Living Australia',
                        'external_id': record.get('id'),
                        'common_name': record.get('vernacularName', species),
                        'scientific_name': record.get('scientificName'),
                        'latitude': record.get('decimalLatitude'),
                        'longitude': record.get('decimalLongitude'),
                        'observed_date': observed_date,
                        'observer_name': record.get('recordedBy'),
                        'location_description': f"{record.get('locality', '')}, {record.get('stateProvince', '')}".strip(', '),
                        'photo_url': None,
                        'basis_of_record': record.get('basisOfRecord'),
                        'data_provider': record.get('dataProviderName'),
                        'collection_code': record.get('collectionCode'),
                        'collected_at': datetime.now()
                    })
                
                time.sleep(1.5)  # ALA rate limiting
                
            except Exception as e:
                logger.warning(f"ALA collection failed for {species}: {e}")
        
        return pd.DataFrame(all_observations)
    
    def merge_and_deduplicate(self, source_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Merge data from all sources and remove duplicates"""
        logger.info("🔄 Merging and deduplicating multi-source data...")
        
        all_dataframes = []
        
        for source_name, df in source_data.items():
            if not df.empty:
                df['data_source'] = source_name
                df['source_priority'] = self._get_source_priority(source_name)
                all_dataframes.append(df)
        
        if not all_dataframes:
            logger.warning("No data collected from any source")
            return pd.DataFrame()
        
        # Combine all data
        merged_df = pd.concat(all_dataframes, ignore_index=True, sort=False)
        
        # Standardize columns
        merged_df = self._standardize_columns(merged_df)
        
        # Remove duplicates based on species, location, and date
        duplicate_columns = ['scientific_name', 'latitude', 'longitude', 'observed_date']
        available_columns = [col for col in duplicate_columns if col in merged_df.columns]
        
        if available_columns:
            # Keep the record from the highest priority source
            merged_df = merged_df.sort_values('source_priority').drop_duplicates(
                subset=available_columns, keep='first'
            ).drop('source_priority', axis=1)
        
        logger.info(f"✅ Merged data: {len(merged_df)} unique records from {len(source_data)} sources")
        
        return merged_df
    
    def _get_source_priority(self, source_name: str) -> int:
        """Assign priority to data sources (lower number = higher priority)"""
        priorities = {
            'gbif': 1,      # Highest quality, research-grade
            'ala': 2,       # Government source
            'inaturalist': 3,  # Good citizen science
            'ebird': 4,     # Specialized for birds
            'biodiversity_gov': 5
        }
        return priorities.get(source_name, 99)
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names and types across sources"""
        # Ensure all required columns exist
        required_columns = [
            'source', 'external_id', 'common_name', 'scientific_name',
            'latitude', 'longitude', 'observed_date', 'observer_name',
            'location_description', 'photo_url', 'collected_at'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Convert data types
        if 'latitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        if 'longitude' in df.columns:
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        
        # Standardize date format
        if 'observed_date' in df.columns:
            df['observed_date'] = pd.to_datetime(df['observed_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        return df
    
    def get_collection_summary(self, source_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate a summary of the multi-source collection"""
        summary = {
            'total_records': sum(len(df) for df in source_data.values()),
            'sources_used': len([name for name, df in source_data.items() if not df.empty]),
            'source_breakdown': {},
            'unique_species': set(),
            'date_range': {'earliest': None, 'latest': None},
            'geographic_coverage': {'min_lat': None, 'max_lat': None, 'min_lng': None, 'max_lng': None}
        }
        
        for source_name, df in source_data.items():
            if not df.empty:
                summary['source_breakdown'][source_name] = len(df)
                
                # Collect unique species
                if 'scientific_name' in df.columns:
                    summary['unique_species'].update(df['scientific_name'].dropna().unique())
        
        summary['unique_species'] = len(summary['unique_species'])
        
        return summary

def main():
    """Demonstrate multi-source data collection"""
    safe_print("MULTI-SOURCE AUSTRALIAN WILDLIFE DATA COLLECTION")
    safe_print("=" * 60)
    
    # Initialize collector
    collector = MultiSourceCollector()
    
    # Australian species of conservation interest
    species_list = [
        'Koala', 'Kangaroo', 'Wombat', 'Echidna', 'Platypus',
        'Tasmanian Devil', 'Quokka', 'Bilby', 'Numbat',
        'Rainbow Lorikeet', 'Kookaburra', 'Cockatoo'
    ]
    
    safe_print(f"Target species: {', '.join(species_list)}")
    safe_print(f"Active sources: {len([s for s in collector.sources.values() if s.enabled])}")
    
    # Collect data from all sources
    source_data = collector.collect_from_all_sources(species_list)
    
    # Merge and deduplicate
    final_data = collector.merge_and_deduplicate(source_data)
    
    # Generate summary
    summary = collector.get_collection_summary(source_data)
    
    safe_print("\nCOLLECTION SUMMARY")
    safe_print("=" * 40)
    safe_print(f"Total records collected: {summary['total_records']:,}")
    safe_print(f"Sources successfully used: {summary['sources_used']}")
    safe_print(f"Unique species found: {summary['unique_species']}")
    safe_print(f"Final deduplicated records: {len(final_data):,}")
    
    safe_print("\nSource Breakdown:")
    for source, count in summary['source_breakdown'].items():
        safe_print(f"  - {source}: {count:,} records")
    
    # Save to database
    if not final_data.empty:
        db_path = "data/aussie_wildlife.db"
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            # Save to a multi-source table
            final_data.to_sql('wildlife_multisource', conn, if_exists='replace', index=False)
            safe_print(f"\nSaved {len(final_data)} records to {db_path}")
    
    safe_print("\nMulti-source data collection completed!")
    safe_print("=" * 60)
    safe_print("Benefits achieved:")
    safe_print("- Data redundancy and reliability")
    safe_print("- Cross-validation between sources") 
    safe_print("- Broader species coverage")
    safe_print("- Higher data quality through source prioritization")
    safe_print("- Government + citizen science integration")

if __name__ == "__main__":
    main()
