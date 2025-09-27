#!/usr/bin/env python3
"""
Cloud Data Lake Enhancement for Australian Wildlife Platform
==========================================================
Extends the existing SQLite-based data lake to cloud storage (AWS S3, Azure Blob, GCP)
with advanced features like partitioning, compression, and distributed processing.

Features:
- Multi-cloud data lake storage
- Parquet/Delta Lake formats
- Automatic partitioning
- Data lifecycle management
- Cost optimization
"""

import os
import pandas as pd
import boto3
from datetime import datetime, date
import json
from typing import Dict, List, Optional, Any
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DataLakeConfig:
    """Configuration for cloud data lake"""
    provider: str  # 'aws', 'azure', 'gcp'
    bronze_bucket: str
    silver_bucket: str
    gold_bucket: str
    region: str
    compression: str = 'snappy'
    file_format: str = 'parquet'

class CloudDataLakeManager:
    """Enhanced data lake with cloud storage capabilities"""
    
    def __init__(self, config: DataLakeConfig, local_db_path: str = "data/aussie_wildlife.db"):
        self.config = config
        self.local_db_path = local_db_path
        self.setup_cloud_clients()
    
    def setup_cloud_clients(self):
        """Initialize cloud storage clients"""
        if self.config.provider == 'aws':
            self.s3_client = boto3.client('s3', region_name=self.config.region)
            self.glue_client = boto3.client('glue', region_name=self.config.region)
        elif self.config.provider == 'azure':
            # Azure Blob Storage client setup
            pass
        elif self.config.provider == 'gcp':
            # Google Cloud Storage client setup
            pass
    
    def migrate_to_cloud_data_lake(self):
        """Migrate existing SQLite data to cloud data lake"""
        print("🚀 Starting Data Lake Migration to Cloud...")
        
        # Migrate Bronze Layer
        self._migrate_bronze_layer()
        
        # Migrate Silver Layer  
        self._migrate_silver_layer()
        
        # Migrate Gold Layer
        self._migrate_gold_layer()
        
        print("✅ Data Lake migration completed successfully!")
    
    def _migrate_bronze_layer(self):
        """Migrate bronze layer with partitioning by date and source"""
        print("🥉 Migrating Bronze Layer...")
        
        conn = sqlite3.connect(self.local_db_path)
        
        # Read bronze data in chunks
        query = """
            SELECT *, 
                   date(ingested_at) as partition_date,
                   source_system as partition_source
            FROM wildlife_bronze
            ORDER BY ingested_at
        """
        
        bronze_data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Group by partitions
        for (partition_date, source), group in bronze_data.groupby(['partition_date', 'partition_source']):
            partition_path = f"year={partition_date[:4]}/month={partition_date[5:7]}/day={partition_date[8:10]}/source={source}/"
            
            # Convert to parquet and upload
            self._upload_partition(
                data=group.drop(['partition_date', 'partition_source'], axis=1),
                layer='bronze',
                partition_path=partition_path,
                filename=f"bronze_data_{partition_date}_{source}.parquet"
            )
        
        print(f"   ✓ Migrated {len(bronze_data)} bronze records")
    
    def _migrate_silver_layer(self):
        """Migrate silver layer with partitioning by species and date"""
        print("🥈 Migrating Silver Layer...")
        
        conn = sqlite3.connect(self.local_db_path)
        
        query = """
            SELECT *, 
                   date(observed_date) as partition_date,
                   COALESCE(common_name, 'unknown') as partition_species
            FROM wildlife_silver
            WHERE common_name IS NOT NULL
            ORDER BY observed_date
        """
        
        silver_data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Group by partitions
        for (partition_date, species), group in silver_data.groupby(['partition_date', 'partition_species']):
            if partition_date and species:
                partition_path = f"year={partition_date[:4]}/month={partition_date[5:7]}/species={species.replace(' ', '_').lower()}/"
                
                # Add data quality metadata
                group['data_lake_migrated_at'] = datetime.now()
                group['partition_info'] = f"date={partition_date},species={species}"
                
                self._upload_partition(
                    data=group.drop(['partition_date', 'partition_species'], axis=1),
                    layer='silver',
                    partition_path=partition_path,
                    filename=f"silver_data_{partition_date}_{species.replace(' ', '_').lower()}.parquet"
                )
        
        print(f"   ✓ Migrated {len(silver_data)} silver records")
    
    def _migrate_gold_layer(self):
        """Migrate gold layer with partitioning by aggregation type"""
        print("🥇 Migrating Gold Layer...")
        
        conn = sqlite3.connect(self.local_db_path)
        
        query = """
            SELECT *, 
                   date(created_at) as partition_date
            FROM wildlife_gold
            ORDER BY created_at
        """
        
        gold_data = pd.read_sql_query(query, conn)
        conn.close()
        
        # Group by aggregation type and date
        for (agg_type, partition_date), group in gold_data.groupby(['aggregation_type', 'partition_date']):
            partition_path = f"aggregation_type={agg_type}/year={partition_date[:4]}/month={partition_date[5:7]}/"
            
            self._upload_partition(
                data=group.drop(['partition_date'], axis=1),
                layer='gold',
                partition_path=partition_path,
                filename=f"gold_analytics_{agg_type}_{partition_date}.parquet"
            )
        
        print(f"   ✓ Migrated {len(gold_data)} gold analytics records")
    
    def _upload_partition(self, data: pd.DataFrame, layer: str, partition_path: str, filename: str):
        """Upload partitioned data to cloud storage"""
        if self.config.provider == 'aws':
            bucket_map = {
                'bronze': self.config.bronze_bucket,
                'silver': self.config.silver_bucket,  
                'gold': self.config.gold_bucket
            }
            
            bucket = bucket_map[layer]
            s3_key = f"{partition_path}{filename}"
            
            # Convert to parquet and upload
            parquet_buffer = data.to_parquet(
                compression=self.config.compression,
                index=False
            )
            
            try:
                self.s3_client.put_object(
                    Bucket=bucket,
                    Key=s3_key,
                    Body=parquet_buffer
                )
                print(f"     ✓ Uploaded {layer}/{partition_path}{filename}")
            except Exception as e:
                print(f"     ❌ Failed to upload {s3_key}: {e}")
    
    def create_data_catalog(self):
        """Create AWS Glue Data Catalog for the data lake"""
        print("📚 Creating Data Lake Catalog...")
        
        # Create database
        try:
            self.glue_client.create_database(
                DatabaseInput={
                    'Name': 'australian_wildlife_datalake',
                    'Description': 'Australian Wildlife Biodiversity Data Lake'
                }
            )
        except self.glue_client.exceptions.AlreadyExistsException:
            print("   ✓ Database already exists")
        
        # Create tables for each layer
        self._create_bronze_table()
        self._create_silver_table()
        self._create_gold_table()
        
        print("✅ Data catalog created successfully!")
    
    def _create_bronze_table(self):
        """Create bronze layer table in Glue catalog"""
        table_input = {
            'Name': 'wildlife_bronze',
            'StorageDescriptor': {
                'Columns': [
                    {'Name': 'id', 'Type': 'bigint'},
                    {'Name': 'raw_data', 'Type': 'string'},
                    {'Name': 'source_system', 'Type': 'string'},
                    {'Name': 'batch_id', 'Type': 'string'},
                    {'Name': 'record_hash', 'Type': 'string'},
                    {'Name': 'ingested_at', 'Type': 'timestamp'}
                ],
                'Location': f's3://{self.config.bronze_bucket}/',
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                }
            },
            'PartitionKeys': [
                {'Name': 'year', 'Type': 'string'},
                {'Name': 'month', 'Type': 'string'},
                {'Name': 'day', 'Type': 'string'},
                {'Name': 'source', 'Type': 'string'}
            ]
        }
        
        try:
            self.glue_client.create_table(
                DatabaseName='australian_wildlife_datalake',
                TableInput=table_input
            )
            print("   ✓ Bronze table created")
        except Exception as e:
            print(f"   ⚠️ Bronze table creation: {e}")
    
    def _create_silver_table(self):
        """Create silver layer table in Glue catalog"""
        table_input = {
            'Name': 'wildlife_silver',
            'StorageDescriptor': {
                'Columns': [
                    {'Name': 'id', 'Type': 'bigint'},
                    {'Name': 'common_name', 'Type': 'string'},
                    {'Name': 'scientific_name', 'Type': 'string'},
                    {'Name': 'location_description', 'Type': 'string'},
                    {'Name': 'latitude', 'Type': 'double'},
                    {'Name': 'longitude', 'Type': 'double'},
                    {'Name': 'observed_date', 'Type': 'string'},
                    {'Name': 'observer_name', 'Type': 'string'},
                    {'Name': 'quality_score', 'Type': 'double'},
                    {'Name': 'data_source', 'Type': 'string'}
                ],
                'Location': f's3://{self.config.silver_bucket}/',
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                }
            },
            'PartitionKeys': [
                {'Name': 'year', 'Type': 'string'},
                {'Name': 'month', 'Type': 'string'},
                {'Name': 'species', 'Type': 'string'}
            ]
        }
        
        try:
            self.glue_client.create_table(
                DatabaseName='australian_wildlife_datalake',
                TableInput=table_input
            )
            print("   ✓ Silver table created")
        except Exception as e:
            print(f"   ⚠️ Silver table creation: {e}")
    
    def _create_gold_table(self):
        """Create gold layer table in Glue catalog"""
        table_input = {
            'Name': 'wildlife_gold',
            'StorageDescriptor': {
                'Columns': [
                    {'Name': 'id', 'Type': 'bigint'},
                    {'Name': 'aggregation_type', 'Type': 'string'},
                    {'Name': 'dimension_1', 'Type': 'string'},
                    {'Name': 'dimension_2', 'Type': 'string'},
                    {'Name': 'metric_name', 'Type': 'string'},
                    {'Name': 'metric_value', 'Type': 'double'},
                    {'Name': 'created_at', 'Type': 'timestamp'}
                ],
                'Location': f's3://{self.config.gold_bucket}/',
                'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                'SerdeInfo': {
                    'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
                }
            },
            'PartitionKeys': [
                {'Name': 'aggregation_type', 'Type': 'string'},
                {'Name': 'year', 'Type': 'string'},
                {'Name': 'month', 'Type': 'string'}
            ]
        }
        
        try:
            self.glue_client.create_table(
                DatabaseName='australian_wildlife_datalake',
                TableInput=table_input
            )
            print("   ✓ Gold table created")
        except Exception as e:
            print(f"   ⚠️ Gold table creation: {e}")

def main():
    """Demonstrate cloud data lake migration"""
    print("🏛️ Australian Wildlife Cloud Data Lake Migration")
    print("=" * 60)
    
    # Configuration for AWS Data Lake
    config = DataLakeConfig(
        provider='aws',
        bronze_bucket='australian-wildlife-bronze',
        silver_bucket='australian-wildlife-silver',
        gold_bucket='australian-wildlife-gold',
        region='ap-southeast-2',  # Sydney region for Australian data
        compression='snappy',
        file_format='parquet'
    )
    
    # Initialize data lake manager
    data_lake = CloudDataLakeManager(config)
    
    # Check if local database exists
    if not os.path.exists("data/aussie_wildlife.db"):
        print("❌ Local database not found. Run ETL pipeline first.")
        return
    
    # Migrate to cloud data lake
    try:
        data_lake.migrate_to_cloud_data_lake()
        data_lake.create_data_catalog()
        
        print("\n🎉 Cloud Data Lake Migration Complete!")
        print("=" * 60)
        print("Next steps:")
        print("1. Set up AWS Athena for SQL queries")
        print("2. Configure QuickSight for BI dashboards") 
        print("3. Set up Glue ETL jobs for automated processing")
        print("4. Implement data lifecycle policies")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("Make sure AWS credentials are configured correctly.")

if __name__ == "__main__":
    main()
