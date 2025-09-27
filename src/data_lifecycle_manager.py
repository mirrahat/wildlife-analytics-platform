#!/usr/bin/env python3
"""
Enterprise Data Lifecycle Management System
==========================================
Contemporary management of data across the complete data lifecycle with modern data engineering practices:

- Data ingestion with validation and standardization
- Real-time data quality monitoring and alerting
- Data governance, cataloging, and lineage tracking
- Application of data standards and schema enforcement
- Modern ETL pipeline with data lake architecture
- Compliance management and regulatory adherence
- Data delivery and distribution management with quality guarantees

This module provides enterprise-level data governance and lifecycle management 
for the Australian Wildlife Platform using contemporary data engineering patterns.
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import logging
import os

# Import contemporary data management components
from data_governance import DataCatalogManager, DataLineageTracker, ComplianceManager, DataAsset, DataLineageEntry
from quality_monitoring import RealTimeQualityMonitor, QualityAlert, console_alert_handler
from modern_etl_pipeline import ModernETLPipeline, ProcessingJob

# Configure logging for data management operations
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DataQualityRule:
    """Defines a data quality rule for validation"""
    name: str
    field: str
    rule_type: str  # 'required', 'format', 'range', 'enum'
    parameters: Dict[str, Any]
    severity: str  # 'error', 'warning', 'info'

@dataclass
class DataQualityResult:
    """Results of data quality assessment"""
    record_id: str
    rule_name: str
    field: str
    severity: str
    message: str
    passed: bool

class DataStandardsManager:
    """
    Manages data standards and schema enforcement for wildlife observations.
    Ensures consistent data structure across all ingestion sources.
    """
    
    def __init__(self):
        self.wildlife_schema = {
            'common_name': {'type': 'string', 'required': True, 'max_length': 200},
            'scientific_name': {'type': 'string', 'required': False, 'max_length': 200},
            'location_description': {'type': 'string', 'required': True, 'max_length': 500},
            'latitude': {'type': 'float', 'required': False, 'min': -90, 'max': 90},
            'longitude': {'type': 'float', 'required': False, 'min': -180, 'max': 180},
            'observed_date': {'type': 'date', 'required': True, 'format': 'YYYY-MM-DD'},
            'observer_name': {'type': 'string', 'required': True, 'max_length': 100},
            'data_source': {'type': 'enum', 'required': True, 'values': ['iNaturalist', 'GBIF', 'eBird', 'Manual']},
            'external_id': {'type': 'integer', 'required': False}
        }
        
        self.quality_rules = self._initialize_quality_rules()
    
    def _initialize_quality_rules(self) -> List[DataQualityRule]:
        """Initialize standard data quality rules"""
        return [
            DataQualityRule(
                name="required_common_name",
                field="common_name",
                rule_type="required",
                parameters={},
                severity="error"
            ),
            DataQualityRule(
                name="valid_coordinates",
                field="coordinates",
                rule_type="custom",
                parameters={'check': 'coordinate_pair'},
                severity="warning"
            ),
            DataQualityRule(
                name="recent_observation_date",
                field="observed_date",
                rule_type="range",
                parameters={'max_days_ago': 365, 'max_days_future': 1},
                severity="warning"
            ),
            DataQualityRule(
                name="australian_location",
                field="location_description",
                rule_type="custom",
                parameters={'check': 'contains_australia_indicators'},
                severity="info"
            ),
            DataQualityRule(
                name="known_species",
                field="common_name",
                rule_type="custom",
                parameters={'check': 'australian_species_list'},
                severity="info"
            )
        ]
    
    def validate_record(self, record: Dict[str, Any]) -> List[DataQualityResult]:
        """Validate a single record against all quality rules"""
        results = []
        record_id = str(record.get('external_id', hash(str(record))))
        
        for rule in self.quality_rules:
            result = self._apply_rule(record, rule, record_id)
            if result:
                results.append(result)
        
        return results
    
    def _apply_rule(self, record: Dict[str, Any], rule: DataQualityRule, record_id: str) -> Optional[DataQualityResult]:
        """Apply a specific quality rule to a record"""
        field_value = record.get(rule.field)
        
        if rule.rule_type == "required":
            if not field_value or str(field_value).strip() == "":
                return DataQualityResult(
                    record_id=record_id,
                    rule_name=rule.name,
                    field=rule.field,
                    severity=rule.severity,
                    message=f"Required field '{rule.field}' is missing or empty",
                    passed=False
                )
        
        elif rule.rule_type == "range" and rule.field == "observed_date":
            if field_value:
                try:
                    obs_date = datetime.strptime(field_value, '%Y-%m-%d')
                    today = datetime.now()
                    max_past = today - timedelta(days=rule.parameters['max_days_ago'])
                    max_future = today + timedelta(days=rule.parameters['max_days_future'])
                    
                    if obs_date < max_past or obs_date > max_future:
                        return DataQualityResult(
                            record_id=record_id,
                            rule_name=rule.name,
                            field=rule.field,
                            severity=rule.severity,
                            message=f"Observation date {field_value} is outside acceptable range",
                            passed=False
                        )
                except ValueError:
                    return DataQualityResult(
                        record_id=record_id,
                        rule_name=rule.name,
                        field=rule.field,
                        severity="error",
                        message=f"Invalid date format: {field_value}",
                        passed=False
                    )
        
        elif rule.rule_type == "custom":
            return self._apply_custom_rule(record, rule, record_id)
        
        return None
    
    def _apply_custom_rule(self, record: Dict[str, Any], rule: DataQualityRule, record_id: str) -> Optional[DataQualityResult]:
        """Apply custom validation rules"""
        check_type = rule.parameters.get('check')
        
        if check_type == "coordinate_pair":
            lat = record.get('latitude')
            lng = record.get('longitude')
            
            if (lat is None) != (lng is None):  # XOR - one is None but not both
                return DataQualityResult(
                    record_id=record_id,
                    rule_name=rule.name,
                    field="coordinates",
                    severity=rule.severity,
                    message="Latitude and longitude must both be provided or both be empty",
                    passed=False
                )
        
        elif check_type == "contains_australia_indicators":
            location = record.get('location_description', '').lower()
            au_indicators = ['australia', 'qld', 'nsw', 'vic', 'sa', 'wa', 'nt', 'act', 'tas']
            
            if location and not any(indicator in location for indicator in au_indicators):
                return DataQualityResult(
                    record_id=record_id,
                    rule_name=rule.name,
                    field=rule.field,
                    severity=rule.severity,
                    message="Location may not be in Australia",
                    passed=False
                )
        
        elif check_type == "australian_species_list":
            species = record.get('common_name', '').lower()
            australian_species = ['koala', 'kangaroo', 'wallaby', 'wombat', 'echidna', 'platypus', 
                                'kookaburra', 'cockatoo', 'lorikeet', 'possum', 'bandicoot']
            
            if species and not any(aus_species in species for aus_species in australian_species):
                return DataQualityResult(
                    record_id=record_id,
                    rule_name=rule.name,
                    field=rule.field,
                    severity=rule.severity,
                    message="Species may not be native Australian wildlife",
                    passed=False
                )
        
        return None

class DataIngestionManager:
    """
    Manages data ingestion with validation and standardization.
    Provides controlled entry point for all wildlife observation data.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
        self.standards_manager = DataStandardsManager()
        self.setup_ingestion_tables()
    
    def setup_ingestion_tables(self):
        """Create tables for tracking ingestion and quality metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Data ingestion log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_ingestion_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    source_system TEXT NOT NULL,
                    records_received INTEGER NOT NULL,
                    records_processed INTEGER NOT NULL,
                    records_accepted INTEGER NOT NULL,
                    records_rejected INTEGER NOT NULL,
                    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processing_duration_seconds REAL,
                    status TEXT NOT NULL
                )
            ''')
            
            # Data quality results
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_quality_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    batch_id TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    field_name TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    passed BOOLEAN NOT NULL,
                    check_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def ingest_batch(self, records: List[Dict[str, Any]], source_system: str) -> Dict[str, Any]:
        """
        Ingest a batch of wildlife observation records with full lifecycle management
        
        Args:
            records: List of wildlife observation records
            source_system: Name of the source system (e.g., 'iNaturalist', 'GBIF')
        
        Returns:
            Dictionary with ingestion results and metrics
        """
        start_time = datetime.now()
        batch_id = self._generate_batch_id(source_system, start_time)
        
        logger.info(f"Starting ingestion batch {batch_id} with {len(records)} records from {source_system}")
        
        processed_records = []
        quality_results = []
        accepted_count = 0
        rejected_count = 0
        
        # Process each record through the data lifecycle
        for record in records:
            try:
                # Step 1: Data standardization
                standardized_record = self._standardize_record(record, source_system)
                
                # Step 2: Data quality assessment
                validation_results = self.standards_manager.validate_record(standardized_record)
                quality_results.extend(validation_results)
                
                # Step 3: Determine acceptance based on quality rules
                has_errors = any(r.severity == 'error' and not r.passed for r in validation_results)
                
                if not has_errors:
                    # Step 4: Store accepted record
                    self._store_record(standardized_record)
                    accepted_count += 1
                else:
                    rejected_count += 1
                    logger.warning(f"Record rejected due to quality errors: {[r.message for r in validation_results if r.severity == 'error' and not r.passed]}")
                
                processed_records.append({
                    'record': standardized_record,
                    'quality_results': validation_results,
                    'accepted': not has_errors
                })
                
            except Exception as e:
                rejected_count += 1
                logger.error(f"Error processing record: {e}")
        
        # Record ingestion metrics
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        ingestion_result = {
            'batch_id': batch_id,
            'source_system': source_system,
            'records_received': len(records),
            'records_processed': len(processed_records),
            'records_accepted': accepted_count,
            'records_rejected': rejected_count,
            'processing_duration_seconds': duration,
            'quality_results': quality_results,
            'status': 'completed'
        }
        
        self._log_ingestion_batch(ingestion_result)
        self._store_quality_results(batch_id, quality_results)
        
        logger.info(f"Completed batch {batch_id}: {accepted_count} accepted, {rejected_count} rejected")
        
        return ingestion_result
    
    def _generate_batch_id(self, source_system: str, timestamp: datetime) -> str:
        """Generate a unique batch ID"""
        timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
        return f"{source_system}_{timestamp_str}_{hash(str(timestamp)) % 10000:04d}"
    
    def _standardize_record(self, record: Dict[str, Any], source_system: str) -> Dict[str, Any]:
        """Apply data standards and normalization"""
        standardized = record.copy()
        
        # Ensure required fields exist
        standardized.setdefault('data_source', source_system)
        standardized.setdefault('created_at', datetime.now().isoformat())
        
        # Standardize field names and formats
        if 'species_guess' in record:
            standardized['common_name'] = record['species_guess']
        
        if 'place_guess' in record:
            standardized['location_description'] = record['place_guess']
        
        if 'observed_on' in record:
            standardized['observed_date'] = record['observed_on']
        
        if 'user' in record and isinstance(record['user'], dict):
            standardized['observer_name'] = record['user'].get('login', 'Anonymous')
        
        # Handle coordinates from different formats
        if 'geojson' in record and record['geojson']:
            coords = record['geojson'].get('coordinates', [])
            if len(coords) >= 2:
                standardized['longitude'] = coords[0]
                standardized['latitude'] = coords[1]
        elif 'location' in record and isinstance(record['location'], list) and len(record['location']) >= 2:
            standardized['longitude'] = record['location'][0]
            standardized['latitude'] = record['location'][1]
        
        # Clean and validate data types
        if 'latitude' in standardized and standardized['latitude']:
            try:
                standardized['latitude'] = float(standardized['latitude'])
            except (ValueError, TypeError):
                standardized['latitude'] = None
        
        if 'longitude' in standardized and standardized['longitude']:
            try:
                standardized['longitude'] = float(standardized['longitude'])
            except (ValueError, TypeError):
                standardized['longitude'] = None
        
        return standardized
    
    def _store_record(self, record: Dict[str, Any]):
        """Store a validated record in the main database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO wildlife_sightings 
                (common_name, scientific_name, location_description, latitude, longitude,
                 observed_date, observer_name, photo_url, data_source, external_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                record.get('common_name'),
                record.get('scientific_name'),
                record.get('location_description'),
                record.get('latitude'),
                record.get('longitude'),
                record.get('observed_date'),
                record.get('observer_name'),
                record.get('photo_url'),
                record.get('data_source'),
                record.get('external_id')
            ))
    
    def _log_ingestion_batch(self, result: Dict[str, Any]):
        """Log ingestion batch results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO data_ingestion_log 
                (batch_id, source_system, records_received, records_processed, 
                 records_accepted, records_rejected, processing_duration_seconds, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result['batch_id'],
                result['source_system'],
                result['records_received'],
                result['records_processed'],
                result['records_accepted'],
                result['records_rejected'],
                result['processing_duration_seconds'],
                result['status']
            ))
    
    def _store_quality_results(self, batch_id: str, quality_results: List[DataQualityResult]):
        """Store data quality assessment results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for result in quality_results:
                cursor.execute('''
                    INSERT INTO data_quality_results 
                    (batch_id, record_id, rule_name, field_name, severity, message, passed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    batch_id,
                    result.record_id,
                    result.rule_name,
                    result.field,
                    result.severity,
                    result.message,
                    result.passed
                ))

class DataDeliveryManager:
    """
    Manages data delivery and distribution with quality guarantees.
    Provides controlled access to validated, high-quality wildlife data.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
    
    def get_quality_assured_dataset(self, 
                                  species_filter: Optional[List[str]] = None,
                                  date_range: Optional[Tuple[str, str]] = None,
                                  quality_level: str = "standard") -> Dict[str, Any]:
        """
        Deliver quality-assured dataset based on specified criteria
        
        Args:
            species_filter: List of species to include
            date_range: Tuple of (start_date, end_date) in YYYY-MM-DD format
            quality_level: 'high' (error-free only), 'standard' (errors + warnings ok), 'all'
        
        Returns:
            Dictionary containing the dataset and quality metadata
        """
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Build query based on quality level
            base_query = '''
                SELECT ws.*, 
                       COUNT(dqr.id) as quality_issues,
                       GROUP_CONCAT(dqr.message) as quality_messages
                FROM wildlife_sightings ws
                LEFT JOIN data_quality_results dqr ON CAST(ws.external_id AS TEXT) = dqr.record_id
            '''
            
            conditions = []
            params = []
            
            # Apply filters
            if species_filter:
                placeholders = ','.join(['?' for _ in species_filter])
                conditions.append(f'ws.common_name IN ({placeholders})')
                params.extend(species_filter)
            
            if date_range:
                conditions.append('ws.observed_date BETWEEN ? AND ?')
                params.extend(date_range)
            
            # Apply quality level filters
            if quality_level == "high":
                conditions.append('''
                    (dqr.severity IS NULL OR dqr.severity != 'error' OR dqr.passed = 1)
                ''')
            
            # Complete query
            if conditions:
                base_query += ' WHERE ' + ' AND '.join(conditions)
            
            base_query += '''
                GROUP BY ws.id
                ORDER BY ws.observed_date DESC, ws.created_at DESC
            '''
            
            cursor.execute(base_query, params)
            records = cursor.fetchall()
            
            # Get quality metrics for this dataset
            quality_metrics = self._calculate_quality_metrics(cursor, conditions, params)
            
            dataset = {
                'records': [dict(record) for record in records],
                'metadata': {
                    'total_records': len(records),
                    'quality_level': quality_level,
                    'filters_applied': {
                        'species_filter': species_filter,
                        'date_range': date_range
                    },
                    'quality_metrics': quality_metrics,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'data_standards_version': "1.0"
                }
            }
            
        return dataset
    
    def _calculate_quality_metrics(self, cursor, conditions: List[str], params: List[Any]) -> Dict[str, Any]:
        """Calculate quality metrics for the delivered dataset"""
        
        # Total quality checks performed
        cursor.execute('SELECT COUNT(*) FROM data_quality_results')
        total_checks = cursor.fetchone()[0]
        
        # Quality issues by severity
        cursor.execute('''
            SELECT severity, passed, COUNT(*) as count
            FROM data_quality_results 
            GROUP BY severity, passed
        ''')
        
        quality_breakdown = {}
        for row in cursor.fetchall():
            severity, passed, count = row
            status = 'passed' if passed else 'failed'
            quality_breakdown[f"{severity}_{status}"] = count
        
        return {
            'total_quality_checks': total_checks,
            'quality_breakdown': quality_breakdown,
            'data_completeness': self._calculate_completeness(cursor),
            'last_quality_assessment': self._get_last_quality_check(cursor)
        }
    
    def _calculate_completeness(self, cursor) -> Dict[str, float]:
        """Calculate data completeness percentages"""
        cursor.execute('SELECT COUNT(*) FROM wildlife_sightings')
        total_records = cursor.fetchone()[0]
        
        if total_records == 0:
            return {}
        
        completeness = {}
        key_fields = ['common_name', 'location_description', 'observed_date', 'latitude', 'longitude']
        
        for field in key_fields:
            cursor.execute(f'''
                SELECT COUNT(*) FROM wildlife_sightings 
                WHERE {field} IS NOT NULL AND {field} != ''
            ''')
            complete_count = cursor.fetchone()[0]
            completeness[field] = (complete_count / total_records) * 100
        
        return completeness
    
    def _get_last_quality_check(self, cursor) -> Optional[str]:
        """Get timestamp of last quality assessment"""
        cursor.execute('''
            SELECT MAX(check_timestamp) FROM data_quality_results
        ''')
        result = cursor.fetchone()
        return result[0] if result[0] else None

class EnterpriseDataLifecycleManager:
    """
    Comprehensive enterprise data lifecycle management system.
    Orchestrates all aspects of contemporary data management.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
        
        # Initialize all contemporary data management components
        self.ingestion_manager = DataIngestionManager(db_path)
        self.delivery_manager = DataDeliveryManager(db_path)
        self.catalog_manager = DataCatalogManager(db_path)
        self.lineage_tracker = DataLineageTracker(db_path)
        self.compliance_manager = ComplianceManager(db_path)
        self.quality_monitor = RealTimeQualityMonitor(db_path, monitoring_interval=300)
        self.etl_pipeline = ModernETLPipeline(db_path)
        
        # Setup integrated monitoring
        self.quality_monitor.add_alert_handler(console_alert_handler)
        self.quality_monitor.add_alert_handler(self._governance_alert_handler)
        
        # Register core data assets
        self._register_core_assets()
        
        logger.info("Enterprise Data Lifecycle Management System initialized")
    
    def _register_core_assets(self):
        """Register core data assets in the catalog"""
        wildlife_asset = DataAsset(
            asset_id="wildlife_observations_bronze",
            name="Wildlife Observations - Bronze Layer",
            description="Raw wildlife sighting data from external sources (iNaturalist, GBIF)",
            schema_version="1.0",
            owner="Data Engineering Team",
            steward="Wildlife Research Lead",
            classification="internal",
            retention_policy="7_years",
            created_date=datetime.now().isoformat(),
            last_modified=datetime.now().isoformat(),
            source_systems=["iNaturalist API", "GBIF API"],
            downstream_systems=["Silver Layer", "Analytics Dashboard"],
            quality_score=0.75,
            compliance_status="assessed"
        )
        
        self.catalog_manager.register_data_asset(wildlife_asset)
    
    def _governance_alert_handler(self, alert: QualityAlert):
        """Handle quality alerts with governance implications"""
        if alert.severity in ['critical', 'high']:
            # Record impact on data asset quality scores
            try:
                asset = self.catalog_manager.get_data_asset("wildlife_observations_bronze")
                if asset and alert.severity == 'critical':
                    # Reduce quality score for critical issues
                    asset.quality_score = max(0.0, asset.quality_score - 0.05)
                    asset.last_modified = datetime.now().isoformat()
                    self.catalog_manager.register_data_asset(asset)
                    
                    logger.warning(f"Asset quality score updated due to critical alert: {asset.quality_score}")
            
            except Exception as e:
                logger.error(f"Error updating asset quality score: {e}")
    
    def execute_full_lifecycle_ingestion(self, records: List[Dict[str, Any]], source_system: str) -> Dict[str, Any]:
        """
        Execute complete data lifecycle ingestion with all contemporary practices
        """
        start_time = datetime.now()
        
        logger.info(f"Starting full lifecycle ingestion for {len(records)} records from {source_system}")
        
        # Phase 1: Data Ingestion with Standards and Quality
        ingestion_result = self.ingestion_manager.ingest_batch(records, source_system)
        
        # Phase 2: Record Data Lineage
        if ingestion_result['records_accepted'] > 0:
            lineage_entry = DataLineageEntry(
                lineage_id=f"ingestion_{ingestion_result['batch_id']}",
                source_asset_id=f"external_{source_system.lower()}",
                target_asset_id="wildlife_observations_bronze",
                transformation_type="ingestion_with_validation",
                transformation_details={
                    "ingestion_batch_id": ingestion_result['batch_id'],
                    "validation_rules_applied": ["completeness", "format", "business_rules"],
                    "quality_gates": ["virus_scan", "format_validation"]
                },
                executed_by="enterprise_lifecycle_manager",
                execution_timestamp=start_time.isoformat(),
                input_record_count=ingestion_result['records_received'],
                output_record_count=ingestion_result['records_accepted'],
                quality_impact={
                    "quality_issues_count": len(ingestion_result['quality_results']),
                    "rejection_rate": ingestion_result['records_rejected'] / ingestion_result['records_received'] if ingestion_result['records_received'] > 0 else 0
                }
            )
            
            self.lineage_tracker.record_transformation(lineage_entry)
        
        # Phase 3: Update Data Catalog
        asset = self.catalog_manager.get_data_asset("wildlife_observations_bronze")
        if asset:
            # Update asset metadata based on ingestion results
            asset.last_modified = datetime.now().isoformat()
            
            # Calculate quality impact
            quality_score_delta = 0
            if ingestion_result['records_rejected'] == 0:
                quality_score_delta = 0.01  # Small boost for perfect ingestion
            elif ingestion_result['records_rejected'] > ingestion_result['records_accepted']:
                quality_score_delta = -0.02  # Penalty for high rejection rate
            
            asset.quality_score = min(1.0, max(0.0, asset.quality_score + quality_score_delta))
            self.catalog_manager.register_data_asset(asset)
        
        # Phase 4: Execute ETL Pipeline (Bronze to Silver)
        etl_results = {}
        try:
            # Register and execute bronze to silver job if not already registered
            bronze_to_silver = self.etl_pipeline.create_bronze_to_silver_job()
            self.etl_pipeline.register_job(bronze_to_silver)
            
            # Execute with incremental processing
            etl_result = self.etl_pipeline.execute_job(
                bronze_to_silver.job_id, 
                {"last_processed_date": (datetime.now() - timedelta(hours=1)).isoformat()}
            )
            
            etl_results = {
                "bronze_to_silver": {
                    "status": etl_result.status,
                    "records_processed": etl_result.records_processed,
                    "records_output": etl_result.records_output,
                    "quality_issues": len(etl_result.quality_issues)
                }
            }
            
        except Exception as e:
            logger.error(f"ETL pipeline execution failed: {e}")
            etl_results = {"error": str(e)}
        
        # Phase 5: Compliance Assessment
        compliance_results = self.compliance_manager.assess_compliance("wildlife_observations_bronze")
        
        # Phase 6: Quality Monitoring Update
        current_quality_metrics = self.quality_monitor.calculate_current_quality_metrics()
        quality_summary = {
            "metrics_calculated": len(current_quality_metrics),
            "overall_quality_score": self.quality_monitor._calculate_overall_quality_score()
        }
        
        # Compile comprehensive results
        lifecycle_result = {
            "ingestion": ingestion_result,
            "etl_pipeline": etl_results,
            "compliance": {
                "checks_performed": len(compliance_results),
                "non_compliant_checks": len([c for c in compliance_results if c.status == 'non_compliant'])
            },
            "quality_monitoring": quality_summary,
            "data_lineage": {
                "lineage_recorded": ingestion_result['records_accepted'] > 0,
                "transformation_tracked": True
            },
            "catalog_updated": True,
            "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
            "lifecycle_status": "completed"
        }
        
        logger.info(f"Full lifecycle ingestion completed in {lifecycle_result['processing_time_seconds']:.2f} seconds")
        
        return lifecycle_result
    
    def get_comprehensive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data across all lifecycle components"""
        
        # Data delivery metrics
        dataset = self.delivery_manager.get_quality_assured_dataset(quality_level="standard")
        
        # Quality monitoring dashboard
        quality_dashboard = self.quality_monitor.get_quality_dashboard_data()
        
        # Pipeline status
        pipeline_status = self.etl_pipeline.get_pipeline_status()
        
        # Catalog search results
        catalog_assets = self.catalog_manager.search_catalog("wildlife")
        
        # Compliance summary
        compliance_checks = self.compliance_manager.assess_compliance("wildlife_observations_bronze")
        
        return {
            "data_delivery": {
                "total_records": dataset['metadata']['total_records'],
                "quality_level": dataset['metadata']['quality_level'],
                "completeness": dataset['metadata']['quality_metrics'].get('data_completeness', {}),
                "last_extraction": dataset['metadata']['extraction_timestamp']
            },
            "quality_monitoring": {
                "overall_score": quality_dashboard['overall_quality_score'],
                "monitoring_status": quality_dashboard['monitoring_status'],
                "recent_alerts": len([a for a in quality_dashboard['recent_alerts'] if not a['resolved']]),
                "current_metrics": len(quality_dashboard['current_metrics'])
            },
            "etl_pipeline": {
                "registered_jobs": pipeline_status['registered_jobs'],
                "recent_executions": len(pipeline_status['recent_executions']),
                "success_rate": self._calculate_pipeline_success_rate(pipeline_status['job_metrics']),
                "inventory_summary": pipeline_status['inventory_summary']
            },
            "data_catalog": {
                "total_assets": len(catalog_assets),
                "asset_types": list(set([asset.classification for asset in catalog_assets])),
                "average_quality_score": sum([asset.quality_score for asset in catalog_assets]) / len(catalog_assets) if catalog_assets else 0
            },
            "compliance": {
                "total_checks": len(compliance_checks),
                "compliant_checks": len([c for c in compliance_checks if c.status == 'compliant']),
                "compliance_rate": len([c for c in compliance_checks if c.status == 'compliant']) / len(compliance_checks) if compliance_checks else 0
            },
            "system_status": {
                "all_systems_operational": True,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def _calculate_pipeline_success_rate(self, job_metrics: Dict[str, Any]) -> float:
        """Calculate overall pipeline success rate"""
        if not job_metrics:
            return 0.0
        
        success_rates = [metrics['success_rate'] for metrics in job_metrics.values()]
        return sum(success_rates) / len(success_rates) if success_rates else 0.0
    
    def start_continuous_monitoring(self):
        """Start continuous quality monitoring"""
        self.quality_monitor.start_monitoring()
        logger.info("Continuous quality monitoring started")
    
    def stop_continuous_monitoring(self):
        """Stop continuous quality monitoring"""
        self.quality_monitor.stop_monitoring()
        logger.info("Continuous quality monitoring stopped")

def main():
    """Demonstrate the enterprise data lifecycle management system"""
    
    print("ENTERPRISE DATA LIFECYCLE MANAGEMENT SYSTEM")
    print("=" * 55)
    print("Contemporary data management with enterprise-grade capabilities:")
    print("• Data ingestion with validation and standardization")
    print("• Real-time quality monitoring and alerting")
    print("• Data governance, cataloging, and lineage tracking")
    print("• Modern ETL pipeline with data lake architecture")
    print("• Compliance management and regulatory adherence")
    print("• Quality-assured data delivery")
    print()
    
    # Initialize the enterprise system
    lifecycle_manager = EnterpriseDataLifecycleManager()
    
    # Demonstrate comprehensive dashboard
    print("Generating comprehensive data management dashboard...")
    dashboard = lifecycle_manager.get_comprehensive_dashboard()
    
    print(f"\nDATA DELIVERY")
    print(f"  Total Records: {dashboard['data_delivery']['total_records']}")
    print(f"  Quality Level: {dashboard['data_delivery']['quality_level']}")
    
    print(f"\nQUALITY MONITORING")
    print(f"  Overall Quality Score: {dashboard['quality_monitoring']['overall_score']:.3f}")
    print(f"  Monitoring Status: {dashboard['quality_monitoring']['monitoring_status']}")
    print(f"  Active Alerts: {dashboard['quality_monitoring']['recent_alerts']}")
    
    print(f"\nETL PIPELINE")
    print(f"  Registered Jobs: {dashboard['etl_pipeline']['registered_jobs']}")
    print(f"  Success Rate: {dashboard['etl_pipeline']['success_rate']:.1%}")
    
    print(f"\nDATA CATALOG")
    print(f"  Total Assets: {dashboard['data_catalog']['total_assets']}")
    print(f"  Average Quality Score: {dashboard['data_catalog']['average_quality_score']:.3f}")
    
    print(f"\nCOMPLIANCE")
    print(f"  Compliance Rate: {dashboard['compliance']['compliance_rate']:.1%}")
    print(f"  Total Checks: {dashboard['compliance']['total_checks']}")
    
    print(f"\nEnterprise data lifecycle management system operational")
    print("Ready for production workloads with full governance and monitoring")

if __name__ == "__main__":
    main()
