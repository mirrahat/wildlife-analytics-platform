#!/usr/bin/env python3
"""
Wildlife Data ETL Pipeline
=========================
Extract, Transform, Load pipeline for Australian wildlife observation data.

This module implements a comprehensive ETL pipeline with:
- Extract: Data collection from multiple sources (APIs, files, databases)
- Transform: Data cleaning, validation, standardization, and enrichment  
- Load: Multi-layered data lake storage (Bronze, Silver, Gold)

Features:
- Configurable transformation rules
- Data quality validation at each stage
- Incremental processing support
- Error handling and retry logic
- Performance monitoring and logging
"""

import sqlite3
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ETLJob:
    """Configuration for an ETL job"""
    job_name: str
    source_type: str  # 'api', 'database', 'file'
    source_config: Dict[str, Any]
    target_layer: str  # 'bronze', 'silver', 'gold'
    transformations: List[str]
    quality_checks: List[str]
    schedule: Optional[str] = None
    incremental: bool = True
    enabled: bool = True

@dataclass
class ETLResult:
    """Results of an ETL job execution"""
    job_name: str
    start_time: datetime
    end_time: datetime
    status: str  # 'success', 'failed', 'partial'
    records_extracted: int
    records_transformed: int
    records_loaded: int
    quality_issues: List[str]
    performance_metrics: Dict[str, Any]

class WildlifeETLPipeline:
    """
    Comprehensive ETL pipeline for Australian wildlife data
    """
    
    def __init__(self, db_path: str = "data/aussie_wildlife.db"):
        self.db_path = db_path
        self.setup_etl_infrastructure()
        self.register_transformations()
        self.register_quality_checks()
        
    def setup_etl_infrastructure(self):
        """Setup database tables for ETL tracking and data layers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # ETL job execution tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS etl_job_executions (
                    execution_id TEXT PRIMARY KEY,
                    job_name TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL,
                    records_extracted INTEGER DEFAULT 0,
                    records_transformed INTEGER DEFAULT 0,
                    records_loaded INTEGER DEFAULT 0,
                    quality_issues TEXT,
                    performance_metrics TEXT,
                    error_details TEXT
                )
            ''')
            
            # Bronze layer - raw data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_bronze (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    raw_data TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    batch_id TEXT,
                    record_hash TEXT UNIQUE
                )
            ''')
            
            # Silver layer - cleaned and validated data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_silver (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    common_name TEXT,
                    scientific_name TEXT,
                    location_description TEXT,
                    latitude REAL,
                    longitude REAL,
                    observed_date DATE,
                    observer_name TEXT,
                    data_source TEXT,
                    external_id INTEGER,
                    photo_url TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    bronze_id INTEGER,
                    quality_score REAL DEFAULT 1.0,
                    validation_flags TEXT,
                    FOREIGN KEY (bronze_id) REFERENCES wildlife_bronze (id)
                )
            ''')
            
            # Gold layer - analytics-ready aggregated data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS wildlife_gold (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aggregation_type TEXT NOT NULL,
                    dimension_1 TEXT,
                    dimension_2 TEXT,
                    dimension_3 TEXT,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    record_count INTEGER DEFAULT 0,
                    period_start DATE,
                    period_end DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            conn.commit()
            logger.info("ETL infrastructure setup completed")
    
    def register_transformations(self):
        """Register available transformation functions"""
        self.transformations = {
            'standardize_species_names': self._standardize_species_names,
            'validate_coordinates': self._validate_coordinates,
            'normalize_dates': self._normalize_dates,
            'clean_locations': self._clean_locations,
            'add_quality_flags': self._add_quality_flags,
            'calculate_biodiversity_metrics': self._calculate_biodiversity_metrics,
            'aggregate_by_location': self._aggregate_by_location,
            'aggregate_by_time': self._aggregate_by_time,
            'detect_rare_species': self._detect_rare_species
        }
    
    def register_quality_checks(self):
        """Register quality validation functions"""
        self.quality_checks = {
            'check_required_fields': self._check_required_fields,
            'validate_australian_bounds': self._validate_australian_bounds,
            'check_date_ranges': self._check_date_ranges,
            'validate_species_names': self._validate_species_names,
            'check_data_freshness': self._check_data_freshness,
            'detect_duplicates': self._detect_duplicates,
            'validate_observer_data': self._validate_observer_data
        }
    
    # EXTRACT METHODS
    def extract_from_existing_table(self, table_name: str, incremental: bool = True, 
                                  last_extracted: Optional[datetime] = None) -> pd.DataFrame:
        """Extract data from existing wildlife_observations table"""
        with sqlite3.connect(self.db_path) as conn:
            query = f"SELECT * FROM {table_name}"
            
            if incremental and last_extracted:
                query += f" WHERE created_at > '{last_extracted.isoformat()}'"
            
            df = pd.read_sql_query(query, conn)
            logger.info(f"Extracted {len(df)} records from {table_name}")
            return df
    
    def extract_from_api(self, api_config: Dict[str, Any]) -> pd.DataFrame:
        """Extract data from API sources"""
        # This would integrate with your existing collectors
        try:
            from collectors.inaturalist_collector import iNaturalistCollector
            
            collector = iNaturalistCollector()
            species_list = api_config.get('species_list', ['koala', 'kangaroo'])
            limit = api_config.get('limit_per_species', 10)
            
            all_records = []
            for species in species_list:
                records = collector.collect_species_data(species, species.title(), limit)
                all_records.extend(records)
            
            df = pd.DataFrame(all_records)
            
            # Map API field names to standard field names for consistency
            if not df.empty:
                field_mapping = {
                    'species': 'common_name',
                    'species_name': 'common_name', 
                    'name': 'common_name',
                    'location': 'location_description',
                    'place': 'location_description',
                    'date': 'observed_date',
                    'observation_date': 'observed_date',
                    'created_at': 'observed_date',
                    'observer': 'observer_name',
                    'user': 'observer_name',
                    'username': 'observer_name',
                    'lat': 'latitude',
                    'lng': 'longitude',
                    'lon': 'longitude'
                }
                
                # Apply field mapping
                for old_field, new_field in field_mapping.items():
                    if old_field in df.columns and new_field not in df.columns:
                        df[new_field] = df[old_field]
                
                # Ensure required fields exist (even if empty)
                required_fields = ['common_name', 'location_description', 'observed_date', 'observer_name']
                for field in required_fields:
                    if field not in df.columns:
                        df[field] = None
                
                # Add metadata
                df['data_source'] = api_config.get('source_name', 'API')
                
                logger.info(f"Extracted {len(df)} records from API with field mapping applied")
            else:
                logger.warning("No records returned from API")
            
            return df
            
        except Exception as e:
            logger.error(f"API extraction failed: {e}")
            return pd.DataFrame()
    
    # TRANSFORM METHODS
    def _standardize_species_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize species name formatting"""
        if 'common_name' in df.columns:
            df['common_name'] = df['common_name'].str.title().str.strip()
            df['common_name'] = df['common_name'].replace('', 'Unknown Species')
        
        if 'scientific_name' in df.columns:
            df['scientific_name'] = df['scientific_name'].str.strip()
            # Capitalize genus, lowercase species
            df['scientific_name'] = df['scientific_name'].apply(
                lambda x: ' '.join([part.capitalize() if i == 0 else part.lower() 
                                  for i, part in enumerate(str(x).split())]) if pd.notna(x) else x
            )
        
        logger.info("Applied species name standardization")
        return df
    
    def _validate_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean coordinate data for Australian bounds"""
        if 'latitude' in df.columns and 'longitude' in df.columns:
            # Australian mainland bounds: lat -45 to -9, lng 112 to 154
            invalid_lat = (df['latitude'] < -45) | (df['latitude'] > -9)
            invalid_lng = (df['longitude'] < 112) | (df['longitude'] > 154)
            
            # Set invalid coordinates to None
            df.loc[invalid_lat, 'latitude'] = None
            df.loc[invalid_lng, 'longitude'] = None
            
            # Add coordinate quality flag
            df['has_valid_coordinates'] = (
                df['latitude'].notna() & df['longitude'].notna()
            )
            
            invalid_count = (invalid_lat | invalid_lng).sum()
            logger.info(f"Cleaned {invalid_count} invalid coordinates")
        
        return df
    
    def _normalize_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize date formats and validate date ranges"""
        if 'observed_date' in df.columns:
            # Convert to datetime
            df['observed_date'] = pd.to_datetime(df['observed_date'], errors='coerce')
            
            # Remove future dates
            future_dates = df['observed_date'] > pd.Timestamp.now()
            df.loc[future_dates, 'observed_date'] = None
            
            # Remove very old dates (before 1900)
            old_dates = df['observed_date'] < pd.Timestamp('1900-01-01')
            df.loc[old_dates, 'observed_date'] = None
            
            # Convert back to date format for storage
            df['observed_date'] = df['observed_date'].dt.date
            
            logger.info("Applied date normalization")
        
        return df
    
    def _clean_locations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize location descriptions"""
        if 'location_description' in df.columns:
            # Remove extra whitespace
            df['location_description'] = df['location_description'].str.strip()
            
            # Replace empty strings with standard value
            df['location_description'] = df['location_description'].replace('', 'Unknown Location')
            
            # Standardize Australian state abbreviations
            state_mapping = {
                'queensland': 'QLD', 'qld': 'QLD',
                'new south wales': 'NSW', 'nsw': 'NSW',
                'victoria': 'VIC', 'vic': 'VIC',
                'south australia': 'SA', 'sa': 'SA',
                'western australia': 'WA', 'wa': 'WA',
                'tasmania': 'TAS', 'tas': 'TAS',
                'northern territory': 'NT', 'nt': 'NT',
                'australian capital territory': 'ACT', 'act': 'ACT'
            }
            
            for full_name, abbrev in state_mapping.items():
                df['location_description'] = df['location_description'].str.replace(
                    full_name, abbrev, case=False, regex=False
                )
            
            logger.info("Applied location cleaning")
        
        return df
    
    def _add_quality_flags(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add data quality flags and calculate quality scores"""
        quality_flags = {}
        
        # Check for complete species information
        quality_flags['has_common_name'] = df['common_name'].notna() & (df['common_name'] != 'Unknown Species')
        quality_flags['has_scientific_name'] = df['scientific_name'].notna() & (df['scientific_name'] != '')
        
        # Check for location information
        quality_flags['has_location_desc'] = df['location_description'].notna() & (df['location_description'] != 'Unknown Location')
        quality_flags['has_coordinates'] = df.get('has_valid_coordinates', False)
        
        # Check for temporal information
        quality_flags['has_observed_date'] = df['observed_date'].notna()
        
        # Check for observer information
        quality_flags['has_observer'] = df['observer_name'].notna() & (df['observer_name'] != '')
        
        # Calculate overall quality score (0-1)
        quality_components = list(quality_flags.values())
        df['quality_score'] = sum(quality_components) / len(quality_components)
        
        # Add individual flags as JSON
        df['validation_flags'] = pd.Series(quality_flags).to_dict()
        df['validation_flags'] = df['validation_flags'].apply(json.dumps)
        
        logger.info("Added quality flags and scores")
        return df
    
    def _calculate_biodiversity_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate biodiversity metrics for gold layer"""
        if df is None or df.empty:
            logger.warning("Empty dataframe provided for biodiversity metrics calculation")
            return pd.DataFrame()
        
        metrics = []
        
        # Check for required columns
        required_columns = {'common_name', 'location_description'}
        missing_columns = required_columns - set(df.columns)
        
        if missing_columns:
            logger.error(f"Missing required columns for biodiversity metrics: {missing_columns}")
            # Return empty metrics with proper structure
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Filter out null values for calculations
        valid_data = df.dropna(subset=['common_name'])
        
        if valid_data.empty:
            logger.warning("No valid species data available for metrics calculation")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Species richness by location
        if 'location_description' in valid_data.columns:
            location_data = valid_data.dropna(subset=['location_description'])
            if not location_data.empty:
                location_richness = location_data.groupby('location_description')['common_name'].nunique().reset_index()
                location_richness['metric_name'] = 'species_richness'
                location_richness['aggregation_type'] = 'location_biodiversity'
                location_richness['dimension_2'] = None
                location_richness.rename(columns={
                    'location_description': 'dimension_1',
                    'common_name': 'metric_value'
                }, inplace=True)
                metrics.append(location_richness)
        
        # Observation abundance by species
        species_abundance = valid_data.groupby('common_name').size().reset_index()
        species_abundance['metric_name'] = 'observation_count'
        species_abundance['aggregation_type'] = 'species_abundance'
        species_abundance['dimension_2'] = None
        species_abundance.rename(columns={
            'common_name': 'dimension_1',
            0: 'metric_value'
        }, inplace=True)
        metrics.append(species_abundance)
        
        # Monthly observation trends
        if 'observed_date' in valid_data.columns:
            date_data = valid_data.dropna(subset=['observed_date'])
            if not date_data.empty:
                date_data['year_month'] = pd.to_datetime(date_data['observed_date'], errors='coerce').dt.to_period('M')
                monthly_data = date_data.dropna(subset=['year_month'])
                if not monthly_data.empty:
                    monthly_counts = monthly_data.groupby(['year_month', 'common_name']).size().reset_index()
                    monthly_counts['metric_name'] = 'monthly_observations'
                    monthly_counts['aggregation_type'] = 'temporal_trends'
                    monthly_counts.rename(columns={
                        'year_month': 'dimension_1',
                        'common_name': 'dimension_2',
                        0: 'metric_value'
                    }, inplace=True)
                    metrics.append(monthly_counts)
        
        # Combine all metrics
        if metrics:
            result_df = pd.concat(metrics, ignore_index=True)
            result_df['created_at'] = datetime.now()
            logger.info(f"Calculated {len(result_df)} biodiversity metrics")
            return result_df
        else:
            logger.warning("No metrics could be calculated")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
    
    def _aggregate_by_location(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create location-based aggregations"""
        if df is None or df.empty or 'location_description' not in df.columns:
            logger.warning("Cannot create location aggregations: missing location_description column")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Filter out null locations
        valid_data = df.dropna(subset=['location_description'])
        
        if valid_data.empty:
            logger.warning("No valid location data for aggregation")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Count observations by location
        location_counts = valid_data.groupby('location_description').size().reset_index()
        location_counts.columns = ['location_description', 'observation_count']
        
        # Transform to gold layer format
        location_aggs = pd.DataFrame({
            'aggregation_type': 'location_summary',
            'dimension_1': location_counts['location_description'],
            'dimension_2': None,
            'metric_name': 'observation_count',
            'metric_value': location_counts['observation_count'],
            'created_at': datetime.now()
        })
        
        logger.info(f"Created location aggregations for {len(location_aggs)} locations")
        return location_aggs
    
    def _aggregate_by_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based aggregations"""
        if df is None or df.empty or 'observed_date' not in df.columns:
            logger.warning("Cannot create temporal aggregations: missing observed_date column")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Filter out null dates
        valid_data = df.dropna(subset=['observed_date'])
        
        if valid_data.empty:
            logger.warning("No valid date data for temporal aggregation")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Convert to period
        valid_data['year_month'] = pd.to_datetime(valid_data['observed_date'], errors='coerce').dt.to_period('M')
        period_data = valid_data.dropna(subset=['year_month'])
        
        if period_data.empty:
            logger.warning("No valid period data for temporal aggregation")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
        
        # Count observations by period
        temporal_counts = period_data.groupby('year_month').size().reset_index()
        temporal_counts.columns = ['period', 'observation_count']
        
        # Transform to gold layer format
        temporal_aggs = pd.DataFrame({
            'aggregation_type': 'temporal_summary',
            'dimension_1': temporal_counts['period'].astype(str),
            'dimension_2': None,
            'metric_name': 'observation_count',
            'metric_value': temporal_counts['observation_count'],
            'created_at': datetime.now()
        })
        
        logger.info(f"Created temporal aggregations for {len(temporal_aggs)} periods")
        return temporal_aggs
    
    def _detect_rare_species(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify rare species based on observation frequency"""
        if df is None or df.empty or 'common_name' not in df.columns:
            logger.warning("Cannot detect rare species: missing common_name column")
            return df
        
        # Filter out null species names
        valid_species_df = df.dropna(subset=['common_name'])
        
        if valid_species_df.empty:
            logger.warning("No valid species names for rare species detection")
            return df
        
        species_counts = valid_species_df.groupby('common_name').size()
        
        if len(species_counts) < 2:
            logger.info("Not enough species diversity for rare species analysis")
            return df
        
        rare_threshold = species_counts.quantile(0.1)  # Bottom 10% by observation count
        rare_species = species_counts[species_counts <= rare_threshold]
        
        if not rare_species.empty:
            rare_df = pd.DataFrame({
                'dimension_1': rare_species.index,
                'metric_value': rare_species.values,
                'metric_name': 'rarity_score',
                'aggregation_type': 'rare_species_detection',
                'dimension_2': None,
                'created_at': datetime.now()
            })
            
            # Calculate rarity scores
            rare_df['metric_value'] = 1 - (rare_df['metric_value'] / species_counts.max())
            
            logger.info(f"Identified {len(rare_df)} rare species")
            return rare_df
        else:
            logger.info("No rare species identified")
            return pd.DataFrame(columns=[
                'aggregation_type', 'dimension_1', 'dimension_2', 'metric_name', 
                'metric_value', 'created_at'
            ])
    
    # QUALITY CHECK METHODS
    def _check_required_fields(self, df: pd.DataFrame) -> List[str]:
        """Check for required fields"""
        issues = []
        required_fields = ['common_name', 'location_description', 'observed_date']
        
        for field in required_fields:
            if field not in df.columns:
                issues.append(f"CRITICAL: Missing required field '{field}'")
            elif df[field].isnull().all():
                issues.append(f"CRITICAL: Field '{field}' is completely empty")
            elif df[field].isnull().mean() > 0.5:
                issues.append(f"WARNING: Field '{field}' has >50% missing values")
        
        return issues
    
    def _validate_australian_bounds(self, df: pd.DataFrame) -> List[str]:
        """Validate coordinates are within Australian bounds"""
        issues = []
        
        if 'latitude' in df.columns and 'longitude' in df.columns:
            coord_data = df[df['latitude'].notna() & df['longitude'].notna()]
            
            if len(coord_data) > 0:
                invalid_coords = coord_data[
                    (coord_data['latitude'] < -45) | (coord_data['latitude'] > -9) |
                    (coord_data['longitude'] < 112) | (coord_data['longitude'] > 154)
                ]
                
                if len(invalid_coords) > 0:
                    pct_invalid = len(invalid_coords) / len(coord_data) * 100
                    issues.append(f"WARNING: {len(invalid_coords)} records ({pct_invalid:.1f}%) have coordinates outside Australia")
        
        return issues
    
    def _check_date_ranges(self, df: pd.DataFrame) -> List[str]:
        """Check for valid date ranges"""
        issues = []
        
        if 'observed_date' in df.columns:
            date_data = df[df['observed_date'].notna()]
            
            if len(date_data) > 0:
                dates = pd.to_datetime(date_data['observed_date'])
                
                # Check for future dates
                future_dates = dates > pd.Timestamp.now()
                if future_dates.any():
                    issues.append(f"WARNING: {future_dates.sum()} records have future observation dates")
                
                # Check for very old dates
                old_dates = dates < pd.Timestamp('1800-01-01')
                if old_dates.any():
                    issues.append(f"WARNING: {old_dates.sum()} records have suspiciously old dates")
        
        return issues
    
    def _validate_species_names(self, df: pd.DataFrame) -> List[str]:
        """Validate species name quality"""
        issues = []
        
        if 'common_name' in df.columns:
            unknown_species = df['common_name'].isin(['Unknown Species', '', None]).sum()
            if unknown_species > 0:
                pct_unknown = unknown_species / len(df) * 100
                issues.append(f"INFO: {unknown_species} records ({pct_unknown:.1f}%) have unknown species names")
        
        return issues
    
    def _check_data_freshness(self, df: pd.DataFrame) -> List[str]:
        """Check data freshness"""
        issues = []
        
        if 'observed_date' in df.columns and len(df) > 0:
            # Convert dates and handle timezone issues
            observed_dates = pd.to_datetime(df['observed_date'], errors='coerce', utc=True)
            cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=30)
            
            # Filter for recent data
            recent_data = df[observed_dates > cutoff_date]
            
            if len(recent_data) == 0:
                issues.append("WARNING: No observations from the last 30 days")
            elif len(recent_data) / len(df) < 0.1:
                issues.append("INFO: Less than 10% of data is from the last 30 days")
        
        return issues
    
    def _detect_duplicates(self, df: pd.DataFrame) -> List[str]:
        """Detect potential duplicate records"""
        issues = []
        
        # Check for exact duplicates
        exact_duplicates = df.duplicated().sum()
        if exact_duplicates > 0:
            issues.append(f"WARNING: {exact_duplicates} exact duplicate records found")
        
        # Check for potential duplicates based on key fields
        if all(col in df.columns for col in ['common_name', 'location_description', 'observed_date', 'observer_name']):
            key_duplicates = df.duplicated(subset=['common_name', 'location_description', 'observed_date', 'observer_name']).sum()
            if key_duplicates > 0:
                issues.append(f"INFO: {key_duplicates} potential duplicate observations (same species, location, date, observer)")
        
        return issues
    
    def _validate_observer_data(self, df: pd.DataFrame) -> List[str]:
        """Validate observer information"""
        issues = []
        
        if 'observer_name' in df.columns:
            missing_observers = df['observer_name'].isnull().sum()
            if missing_observers > 0:
                pct_missing = missing_observers / len(df) * 100
                issues.append(f"INFO: {missing_observers} records ({pct_missing:.1f}%) missing observer information")
        
        return issues
    
    # LOAD METHODS
    def load_to_bronze(self, df: pd.DataFrame, source_system: str, batch_id: str) -> int:
        """Load raw data to bronze layer"""
        with sqlite3.connect(self.db_path) as conn:
            records_loaded = 0
            
            for _, row in df.iterrows():
                raw_data = json.dumps(row.to_dict(), default=str)
                record_hash = hash(raw_data)
                
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO wildlife_bronze 
                        (raw_data, source_system, batch_id, record_hash)
                        VALUES (?, ?, ?, ?)
                    ''', (raw_data, source_system, batch_id, str(record_hash)))
                    
                    if cursor.rowcount > 0:
                        records_loaded += 1
                
                except sqlite3.Error as e:
                    logger.error(f"Error loading record to bronze: {e}")
            
            conn.commit()
            logger.info(f"Loaded {records_loaded} records to bronze layer")
            return records_loaded
    
    def load_to_silver(self, df: pd.DataFrame) -> int:
        """Load transformed data to silver layer"""
        with sqlite3.connect(self.db_path) as conn:
            # Prepare data for silver layer
            silver_columns = [
                'common_name', 'scientific_name', 'location_description', 
                'latitude', 'longitude', 'observed_date', 'observer_name',
                'data_source', 'external_id', 'photo_url', 'quality_score', 'validation_flags'
            ]
            
            # Ensure all required columns exist
            for col in silver_columns:
                if col not in df.columns:
                    df[col] = None
            
            # Select and insert data
            silver_df = df[silver_columns].copy()
            records_loaded = silver_df.to_sql('wildlife_silver', conn, if_exists='append', index=False)
            
            logger.info(f"Loaded {len(silver_df)} records to silver layer")
            return len(silver_df)
    
    def load_to_gold(self, df: pd.DataFrame) -> int:
        """Load aggregated data to gold layer"""
        with sqlite3.connect(self.db_path) as conn:
            records_loaded = df.to_sql('wildlife_gold', conn, if_exists='append', index=False)
            logger.info(f"Loaded {len(df)} records to gold layer")
            return len(df)
    
    # MAIN ETL EXECUTION
    def run_etl_job(self, job: ETLJob) -> ETLResult:
        """Execute a complete ETL job"""
        start_time = datetime.now()
        execution_id = f"{job.job_name}_{start_time.strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Starting ETL job: {job.job_name}")
        
        try:
            # EXTRACT
            if job.source_type == 'database':
                df = self.extract_from_existing_table(**job.source_config)
            elif job.source_type == 'api':
                df = self.extract_from_api(job.source_config)
            else:
                raise ValueError(f"Unsupported source type: {job.source_type}")
            
            records_extracted = len(df)
            
            if records_extracted == 0:
                logger.warning("No records extracted - ending job")
                return ETLResult(
                    job_name=job.job_name,
                    start_time=start_time,
                    end_time=datetime.now(),
                    status='success',
                    records_extracted=0,
                    records_transformed=0,
                    records_loaded=0,
                    quality_issues=[],
                    performance_metrics={}
                )
            
            # TRANSFORM
            for transformation in job.transformations:
                if transformation in self.transformations:
                    df = self.transformations[transformation](df)
                else:
                    logger.warning(f"Unknown transformation: {transformation}")
            
            records_transformed = len(df)
            
            # QUALITY CHECKS
            quality_issues = []
            for check in job.quality_checks:
                if check in self.quality_checks:
                    issues = self.quality_checks[check](df)
                    quality_issues.extend(issues)
                else:
                    logger.warning(f"Unknown quality check: {check}")
            
            # LOAD
            batch_id = execution_id
            
            if job.target_layer == 'bronze':
                records_loaded = self.load_to_bronze(df, job.source_config.get('source_name', 'unknown'), batch_id)
            elif job.target_layer == 'silver':
                records_loaded = self.load_to_silver(df)
            elif job.target_layer == 'gold':
                records_loaded = self.load_to_gold(df)
            else:
                raise ValueError(f"Unknown target layer: {job.target_layer}")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Calculate performance metrics
            performance_metrics = {
                'duration_seconds': duration,
                'records_per_second': records_extracted / duration if duration > 0 else 0,
                'transformation_success_rate': records_transformed / records_extracted if records_extracted > 0 else 0,
                'load_success_rate': records_loaded / records_transformed if records_transformed > 0 else 0
            }
            
            # Determine job status
            critical_issues = [issue for issue in quality_issues if 'CRITICAL' in issue]
            status = 'failed' if critical_issues else 'success'
            
            result = ETLResult(
                job_name=job.job_name,
                start_time=start_time,
                end_time=end_time,
                status=status,
                records_extracted=records_extracted,
                records_transformed=records_transformed,
                records_loaded=records_loaded,
                quality_issues=quality_issues,
                performance_metrics=performance_metrics
            )
            
            # Log execution results
            self._log_etl_execution(execution_id, result)
            
            logger.info(f"ETL job completed: {job.job_name} - Status: {status}")
            return result
            
        except Exception as e:
            end_time = datetime.now()
            logger.error(f"ETL job failed: {job.job_name} - Error: {e}")
            
            result = ETLResult(
                job_name=job.job_name,
                start_time=start_time,
                end_time=end_time,
                status='failed',
                records_extracted=0,
                records_transformed=0,
                records_loaded=0,
                quality_issues=[f"CRITICAL: {str(e)}"],
                performance_metrics={}
            )
            
            self._log_etl_execution(execution_id, result, str(e))
            return result
    
    def _log_etl_execution(self, execution_id: str, result: ETLResult, error_details: str = None):
        """Log ETL execution results to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO etl_job_executions
                (execution_id, job_name, start_time, end_time, status,
                 records_extracted, records_transformed, records_loaded,
                 quality_issues, performance_metrics, error_details)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                execution_id,
                result.job_name,
                result.start_time.isoformat(),
                result.end_time.isoformat(),
                result.status,
                result.records_extracted,
                result.records_transformed,
                result.records_loaded,
                json.dumps(result.quality_issues),
                json.dumps(result.performance_metrics),
                error_details
            ))
            
            conn.commit()

def main():
    """Demonstrate ETL pipeline usage"""
    print("WILDLIFE DATA ETL PIPELINE")
    print("=" * 30)
    
    # Initialize ETL pipeline
    etl = WildlifeETLPipeline()
    
    # Example 1: Process existing data from bronze to silver
    bronze_to_silver_job = ETLJob(
        job_name="bronze_to_silver_cleanup",
        source_type="database",
        source_config={
            "table_name": "wildlife_observations",
            "incremental": False
        },
        target_layer="silver",
        transformations=[
            "standardize_species_names",
            "validate_coordinates", 
            "normalize_dates",
            "clean_locations",
            "add_quality_flags"
        ],
        quality_checks=[
            "check_required_fields",
            "validate_australian_bounds",
            "check_date_ranges",
            "detect_duplicates"
        ]
    )
    
    # Example 2: Collect fresh API data and load to bronze
    api_to_bronze_job = ETLJob(
        job_name="api_fresh_data_collection",
        source_type="api",
        source_config={
            "species_list": ["koala", "kangaroo", "echidna"],
            "limit_per_species": 5,
            "source_name": "iNaturalist_API"
        },
        target_layer="bronze",
        transformations=[],  # Minimal transformation for bronze
        quality_checks=[
            "check_required_fields",
            "check_data_freshness"
        ]
    )
    
    # Example 3: Create analytics aggregations for gold layer
    silver_to_gold_job = ETLJob(
        job_name="analytics_aggregations",
        source_type="database", 
        source_config={
            "table_name": "wildlife_silver",
            "incremental": False
        },
        target_layer="gold",
        transformations=[
            "calculate_biodiversity_metrics",
            "detect_rare_species"
        ],
        quality_checks=[
            "validate_species_names"
        ]
    )
    
    # Execute ETL jobs
    jobs = [api_to_bronze_job, bronze_to_silver_job, silver_to_gold_job]
    
    for job in jobs:
        print(f"\nExecuting ETL job: {job.job_name}")
        result = etl.run_etl_job(job)
        
        print(f"Status: {result.status}")
        print(f"Records: {result.records_extracted} → {result.records_transformed} → {result.records_loaded}")
        print(f"Duration: {result.performance_metrics.get('duration_seconds', 0):.2f} seconds")
        
        if result.quality_issues:
            print(f"Quality issues: {len(result.quality_issues)}")
            for issue in result.quality_issues[:3]:  # Show first 3 issues
                print(f"  • {issue}")
    
    print(f"\nETL pipeline execution completed!")

if __name__ == "__main__":
    main()
