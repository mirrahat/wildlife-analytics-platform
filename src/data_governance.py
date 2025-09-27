#!/usr/bin/env python3
"""
Data Governance and Compliance Management
=========================================
Contemporary data governance for the Australian Biodiversity Platform.
Manages data lineage, cataloging, compliance, and governance policies.

This module implements enterprise-grade data governance practices including:
- Data cataloging and metadata management
- Data lineage tracking across transformations
- Compliance and audit trail management
- Data privacy and security controls
- Automated governance policy enforcement
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any, Tuple
import logging
import os
import uuid

logger = logging.getLogger(__name__)

@dataclass
class DataAsset:
    """Represents a data asset in the data catalog"""
    asset_id: str
    name: str
    description: str
    schema_version: str
    owner: str
    steward: str
    classification: str  # public, internal, confidential, restricted
    retention_policy: str
    created_date: str
    last_modified: str
    source_systems: List[str]
    downstream_systems: List[str]
    quality_score: float
    compliance_status: str

@dataclass
class DataLineageEntry:
    """Tracks data lineage and transformations"""
    lineage_id: str
    source_asset_id: str
    target_asset_id: str
    transformation_type: str
    transformation_details: Dict[str, Any]
    executed_by: str
    execution_timestamp: str
    input_record_count: int
    output_record_count: int
    quality_impact: Dict[str, Any]

@dataclass
class ComplianceCheck:
    """Represents a compliance validation check"""
    check_id: str
    regulation: str  # GDPR, Privacy Act, etc.
    requirement: str
    check_type: str
    status: str
    evidence: Dict[str, Any]
    last_assessed: str
    next_assessment_due: str

class DataCatalogManager:
    """
    Manages the enterprise data catalog with metadata and asset tracking.
    Provides comprehensive visibility into all data assets and their properties.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
        self.setup_catalog_tables()
    
    def setup_catalog_tables(self):
        """Initialize data catalog database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Data assets catalog
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_catalog (
                    asset_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    schema_version TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    steward TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    retention_policy TEXT NOT NULL,
                    created_date TIMESTAMP NOT NULL,
                    last_modified TIMESTAMP NOT NULL,
                    source_systems TEXT, -- JSON array
                    downstream_systems TEXT, -- JSON array
                    quality_score REAL DEFAULT 0.0,
                    compliance_status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Data lineage tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_lineage (
                    lineage_id TEXT PRIMARY KEY,
                    source_asset_id TEXT NOT NULL,
                    target_asset_id TEXT NOT NULL,
                    transformation_type TEXT NOT NULL,
                    transformation_details TEXT, -- JSON
                    executed_by TEXT NOT NULL,
                    execution_timestamp TIMESTAMP NOT NULL,
                    input_record_count INTEGER,
                    output_record_count INTEGER,
                    quality_impact TEXT, -- JSON
                    FOREIGN KEY (source_asset_id) REFERENCES data_catalog (asset_id),
                    FOREIGN KEY (target_asset_id) REFERENCES data_catalog (asset_id)
                )
            ''')
            
            # Compliance checks
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS compliance_checks (
                    check_id TEXT PRIMARY KEY,
                    asset_id TEXT NOT NULL,
                    regulation TEXT NOT NULL,
                    requirement TEXT NOT NULL,
                    check_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence TEXT, -- JSON
                    last_assessed TIMESTAMP NOT NULL,
                    next_assessment_due TIMESTAMP NOT NULL,
                    FOREIGN KEY (asset_id) REFERENCES data_catalog (asset_id)
                )
            ''')
            
            conn.commit()
    
    def register_data_asset(self, asset: DataAsset) -> bool:
        """Register a new data asset in the catalog"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO data_catalog
                    (asset_id, name, description, schema_version, owner, steward, 
                     classification, retention_policy, created_date, last_modified,
                     source_systems, downstream_systems, quality_score, compliance_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    asset.asset_id,
                    asset.name,
                    asset.description,
                    asset.schema_version,
                    asset.owner,
                    asset.steward,
                    asset.classification,
                    asset.retention_policy,
                    asset.created_date,
                    asset.last_modified,
                    json.dumps(asset.source_systems),
                    json.dumps(asset.downstream_systems),
                    asset.quality_score,
                    asset.compliance_status
                ))
                
                logger.info(f"Registered data asset: {asset.name} ({asset.asset_id})")
                return True
        
        except Exception as e:
            logger.error(f"Failed to register data asset {asset.asset_id}: {e}")
            return False
    
    def get_data_asset(self, asset_id: str) -> Optional[DataAsset]:
        """Retrieve a data asset from the catalog"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM data_catalog WHERE asset_id = ?', (asset_id,))
            row = cursor.fetchone()
            
            if row:
                return DataAsset(
                    asset_id=row['asset_id'],
                    name=row['name'],
                    description=row['description'],
                    schema_version=row['schema_version'],
                    owner=row['owner'],
                    steward=row['steward'],
                    classification=row['classification'],
                    retention_policy=row['retention_policy'],
                    created_date=row['created_date'],
                    last_modified=row['last_modified'],
                    source_systems=json.loads(row['source_systems']) if row['source_systems'] else [],
                    downstream_systems=json.loads(row['downstream_systems']) if row['downstream_systems'] else [],
                    quality_score=row['quality_score'],
                    compliance_status=row['compliance_status']
                )
        
        return None
    
    def search_catalog(self, query: str, classification_filter: Optional[str] = None) -> List[DataAsset]:
        """Search the data catalog by name or description"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            base_query = '''
                SELECT * FROM data_catalog 
                WHERE (name LIKE ? OR description LIKE ?)
            '''
            params = [f'%{query}%', f'%{query}%']
            
            if classification_filter:
                base_query += ' AND classification = ?'
                params.append(classification_filter)
            
            base_query += ' ORDER BY quality_score DESC, last_modified DESC'
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            assets = []
            for row in rows:
                assets.append(DataAsset(
                    asset_id=row['asset_id'],
                    name=row['name'],
                    description=row['description'],
                    schema_version=row['schema_version'],
                    owner=row['owner'],
                    steward=row['steward'],
                    classification=row['classification'],
                    retention_policy=row['retention_policy'],
                    created_date=row['created_date'],
                    last_modified=row['last_modified'],
                    source_systems=json.loads(row['source_systems']) if row['source_systems'] else [],
                    downstream_systems=json.loads(row['downstream_systems']) if row['downstream_systems'] else [],
                    quality_score=row['quality_score'],
                    compliance_status=row['compliance_status']
                ))
            
            return assets

class DataLineageTracker:
    """
    Tracks data lineage and transformation history across the platform.
    Provides complete visibility into data flow and transformation impact.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
    
    def record_transformation(self, lineage_entry: DataLineageEntry) -> bool:
        """Record a data transformation in the lineage tracker"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO data_lineage
                    (lineage_id, source_asset_id, target_asset_id, transformation_type,
                     transformation_details, executed_by, execution_timestamp,
                     input_record_count, output_record_count, quality_impact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lineage_entry.lineage_id,
                    lineage_entry.source_asset_id,
                    lineage_entry.target_asset_id,
                    lineage_entry.transformation_type,
                    json.dumps(lineage_entry.transformation_details),
                    lineage_entry.executed_by,
                    lineage_entry.execution_timestamp,
                    lineage_entry.input_record_count,
                    lineage_entry.output_record_count,
                    json.dumps(lineage_entry.quality_impact)
                ))
                
                logger.info(f"Recorded lineage: {lineage_entry.transformation_type} from {lineage_entry.source_asset_id}")
                return True
        
        except Exception as e:
            logger.error(f"Failed to record lineage {lineage_entry.lineage_id}: {e}")
            return False
    
    def get_upstream_lineage(self, asset_id: str, max_depth: int = 10) -> List[DataLineageEntry]:
        """Get upstream data lineage for an asset"""
        lineage = []
        current_assets = [asset_id]
        depth = 0
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            while current_assets and depth < max_depth:
                placeholders = ','.join(['?' for _ in current_assets])
                cursor.execute(f'''
                    SELECT * FROM data_lineage 
                    WHERE target_asset_id IN ({placeholders})
                    ORDER BY execution_timestamp DESC
                ''', current_assets)
                
                batch_lineage = []
                next_assets = set()
                
                for row in cursor.fetchall():
                    entry = DataLineageEntry(
                        lineage_id=row['lineage_id'],
                        source_asset_id=row['source_asset_id'],
                        target_asset_id=row['target_asset_id'],
                        transformation_type=row['transformation_type'],
                        transformation_details=json.loads(row['transformation_details']) if row['transformation_details'] else {},
                        executed_by=row['executed_by'],
                        execution_timestamp=row['execution_timestamp'],
                        input_record_count=row['input_record_count'],
                        output_record_count=row['output_record_count'],
                        quality_impact=json.loads(row['quality_impact']) if row['quality_impact'] else {}
                    )
                    
                    batch_lineage.append(entry)
                    next_assets.add(entry.source_asset_id)
                
                lineage.extend(batch_lineage)
                current_assets = list(next_assets)
                depth += 1
        
        return lineage
    
    def get_downstream_lineage(self, asset_id: str, max_depth: int = 10) -> List[DataLineageEntry]:
        """Get downstream data lineage for an asset"""
        lineage = []
        current_assets = [asset_id]
        depth = 0
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            while current_assets and depth < max_depth:
                placeholders = ','.join(['?' for _ in current_assets])
                cursor.execute(f'''
                    SELECT * FROM data_lineage 
                    WHERE source_asset_id IN ({placeholders})
                    ORDER BY execution_timestamp DESC
                ''', current_assets)
                
                batch_lineage = []
                next_assets = set()
                
                for row in cursor.fetchall():
                    entry = DataLineageEntry(
                        lineage_id=row['lineage_id'],
                        source_asset_id=row['source_asset_id'],
                        target_asset_id=row['target_asset_id'],
                        transformation_type=row['transformation_type'],
                        transformation_details=json.loads(row['transformation_details']) if row['transformation_details'] else {},
                        executed_by=row['executed_by'],
                        execution_timestamp=row['execution_timestamp'],
                        input_record_count=row['input_record_count'],
                        output_record_count=row['output_record_count'],
                        quality_impact=json.loads(row['quality_impact']) if row['quality_impact'] else {}
                    )
                    
                    batch_lineage.append(entry)
                    next_assets.add(entry.target_asset_id)
                
                lineage.extend(batch_lineage)
                current_assets = list(next_assets)
                depth += 1
        
        return lineage

class ComplianceManager:
    """
    Manages compliance and regulatory requirements for data governance.
    Ensures adherence to privacy laws and data protection regulations.
    """
    
    def __init__(self, db_path: str = "aussie_wildlife.db"):
        self.db_path = db_path
        self.setup_compliance_framework()
    
    def setup_compliance_framework(self):
        """Initialize compliance framework with Australian regulations"""
        self.regulations = {
            'Privacy Act 1988': {
                'requirements': [
                    'Personal information collection notice',
                    'Consent for sensitive information',
                    'Data minimization principle',
                    'Purpose limitation',
                    'Data quality assurance',
                    'Security safeguards',
                    'Access and correction rights'
                ]
            },
            'Biosecurity Act 2015': {
                'requirements': [
                    'Accurate species identification',
                    'Location data validation',
                    'Quarantine sensitive data handling'
                ]
            },
            'EPBC Act': {
                'requirements': [
                    'Threatened species data protection',
                    'Critical habitat location security',
                    'Indigenous cultural site respect'
                ]
            }
        }
    
    def assess_compliance(self, asset_id: str) -> List[ComplianceCheck]:
        """Perform compliance assessment for a data asset"""
        checks = []
        
        # Get asset details
        catalog_manager = DataCatalogManager(self.db_path)
        asset = catalog_manager.get_data_asset(asset_id)
        
        if not asset:
            return checks
        
        # Assess each regulation
        for regulation, details in self.regulations.items():
            for requirement in details['requirements']:
                check = self._perform_compliance_check(asset, regulation, requirement)
                if check:
                    checks.append(check)
        
        # Store compliance results
        self._store_compliance_checks(checks)
        
        return checks
    
    def _perform_compliance_check(self, asset: DataAsset, regulation: str, requirement: str) -> Optional[ComplianceCheck]:
        """Perform a specific compliance check"""
        check_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        # Privacy Act checks
        if regulation == 'Privacy Act 1988':
            if 'personal information' in requirement.lower():
                # Check if asset contains personal data
                has_personal_data = self._check_personal_data_presence(asset.asset_id)
                status = 'compliant' if not has_personal_data else 'needs_review'
                evidence = {'personal_data_detected': has_personal_data}
            
            elif 'data quality' in requirement.lower():
                # Check data quality scores
                status = 'compliant' if asset.quality_score >= 0.8 else 'non_compliant'
                evidence = {'quality_score': asset.quality_score, 'threshold': 0.8}
            
            elif 'security' in requirement.lower():
                # Check security classification
                status = 'compliant' if asset.classification in ['internal', 'confidential'] else 'needs_review'
                evidence = {'classification': asset.classification}
            
            else:
                status = 'not_assessed'
                evidence = {}
        
        # Biosecurity Act checks
        elif regulation == 'Biosecurity Act 2015':
            if 'species identification' in requirement.lower():
                accuracy = self._check_species_identification_accuracy(asset.asset_id)
                status = 'compliant' if accuracy >= 0.9 else 'non_compliant'
                evidence = {'identification_accuracy': accuracy}
            
            else:
                status = 'not_assessed'
                evidence = {}
        
        # EPBC Act checks
        elif regulation == 'EPBC Act':
            if 'threatened species' in requirement.lower():
                has_threatened_data = self._check_threatened_species_data(asset.asset_id)
                status = 'compliant' if not has_threatened_data or asset.classification == 'confidential' else 'non_compliant'
                evidence = {'threatened_species_data': has_threatened_data, 'protection_level': asset.classification}
            
            else:
                status = 'not_assessed'
                evidence = {}
        
        else:
            status = 'not_assessed'
            evidence = {}
        
        return ComplianceCheck(
            check_id=check_id,
            regulation=regulation,
            requirement=requirement,
            check_type='automated',
            status=status,
            evidence=evidence,
            last_assessed=current_time,
            next_assessment_due=(datetime.now() + timedelta(days=90)).isoformat()
        )
    
    def _check_personal_data_presence(self, asset_id: str) -> bool:
        """Check if asset contains personal data"""
        # For wildlife data, observer names could be considered personal data
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM wildlife_sightings 
                WHERE observer_name IS NOT NULL AND observer_name != 'Anonymous'
            ''')
            count = cursor.fetchone()[0]
            return count > 0
    
    def _check_species_identification_accuracy(self, asset_id: str) -> float:
        """Estimate species identification accuracy based on data quality"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT AVG(CASE 
                    WHEN scientific_name IS NOT NULL THEN 1.0
                    WHEN common_name LIKE '%unknown%' OR common_name LIKE '%unidentified%' THEN 0.3
                    ELSE 0.8
                END) as accuracy
                FROM wildlife_sightings
            ''')
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0
    
    def _check_threatened_species_data(self, asset_id: str) -> bool:
        """Check if asset contains threatened species data"""
        # List of some known threatened Australian species
        threatened_species = ['koala', 'bilby', 'numbat', 'quoll', 'bandicoot']
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for species in threatened_species:
                cursor.execute('''
                    SELECT COUNT(*) FROM wildlife_sightings 
                    WHERE LOWER(common_name) LIKE ?
                ''', (f'%{species}%',))
                
                if cursor.fetchone()[0] > 0:
                    return True
            
            return False
    
    def _store_compliance_checks(self, checks: List[ComplianceCheck]):
        """Store compliance check results"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for check in checks:
                cursor.execute('''
                    INSERT OR REPLACE INTO compliance_checks
                    (check_id, asset_id, regulation, requirement, check_type, 
                     status, evidence, last_assessed, next_assessment_due)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    check.check_id,
                    'wildlife_observations',  # Default asset for now
                    check.regulation,
                    check.requirement,
                    check.check_type,
                    check.status,
                    json.dumps(check.evidence),
                    check.last_assessed,
                    check.next_assessment_due
                ))

def main():
    """Demonstrate the data governance system"""
    print("DATA GOVERNANCE AND COMPLIANCE SYSTEM")
    print("=" * 45)
    
    # Initialize governance components
    catalog_manager = DataCatalogManager()
    lineage_tracker = DataLineageTracker()
    compliance_manager = ComplianceManager()
    
    # Register a sample data asset
    wildlife_asset = DataAsset(
        asset_id="wildlife_observations_v1",
        name="Australian Wildlife Observations",
        description="Curated wildlife sighting data from multiple Australian sources",
        schema_version="1.0",
        owner="Data Science Team",
        steward="Wildlife Research Lead",
        classification="internal",
        retention_policy="7_years",
        created_date=datetime.now().isoformat(),
        last_modified=datetime.now().isoformat(),
        source_systems=["iNaturalist", "GBIF"],
        downstream_systems=["Analytics Dashboard", "Research Reports"],
        quality_score=0.85,
        compliance_status="assessed"
    )
    
    # Register the asset
    success = catalog_manager.register_data_asset(wildlife_asset)
    print(f"Data asset registration: {'Success' if success else 'Failed'}")
    
    # Perform compliance assessment
    print("\nPerforming compliance assessment...")
    compliance_checks = compliance_manager.assess_compliance(wildlife_asset.asset_id)
    
    print(f"Completed {len(compliance_checks)} compliance checks:")
    for check in compliance_checks[:5]:  # Show first 5 checks
        print(f"  • {check.regulation}: {check.requirement} - {check.status}")
    
    print(f"\nData governance framework established with {len(compliance_checks)} compliance controls")

if __name__ == "__main__":
    main()
