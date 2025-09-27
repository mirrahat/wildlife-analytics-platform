#!/usr/bin/env python3
"""
Unified Australian Wildlife Analytics Dashboard
=============================================
Comprehensive Flask web application combining:
- ETL Pipeline Monitoring
- Data Quality Dashboard  
- Species Explorer
- Real-time Analytics

Single URL for all data engineering needs.
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import subprocess
import sys

app = Flask(__name__)

class UnifiedWildlifeDashboard:
    """Unified dashboard combining all ETL and analytics features"""
    
    def __init__(self, db_path="data/aussie_wildlife.db"):
        self.db_path = db_path
    
    def get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            return None
        return sqlite3.connect(self.db_path)
    
    def get_etl_summary(self):
        """Get ETL layers summary"""
        conn = self.get_connection()
        if conn is None:
            return {}
        
        try:
            cursor = conn.cursor()
            
            # Bronze layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_bronze")
            bronze_count = cursor.fetchone()[0]
            
            # Silver layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_silver")
            silver_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT AVG(quality_score) FROM wildlife_silver WHERE quality_score IS NOT NULL")
            avg_quality = cursor.fetchone()[0] or 0
            
            # Gold layer
            cursor.execute("SELECT COUNT(*) FROM wildlife_gold")
            gold_count = cursor.fetchone()[0]
            
            # ETL jobs
            cursor.execute("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'success' THEN 1 END) as successful
                FROM etl_job_executions
            """)
            job_stats = cursor.fetchone()
            
            conn.close()
            
            return {
                'bronze_count': bronze_count,
                'silver_count': silver_count,
                'gold_count': gold_count,
                'avg_quality': round(avg_quality, 3) if avg_quality else 0,
                'total_jobs': job_stats[0],
                'successful_jobs': job_stats[1],
                'success_rate': round((job_stats[1] / job_stats[0]) * 100, 1) if job_stats[0] > 0 else 0
            }
        except Exception as e:
            print(f"Error loading ETL summary: {e}")
            return {}
    
    def get_etl_job_history(self, limit=20):
        """Get ETL job execution history"""
        conn = self.get_connection()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT job_name, status, 
                       records_extracted, records_transformed, records_loaded,
                       datetime(start_time) as start_time,
                       ROUND((julianday(end_time) - julianday(start_time)) * 86400, 2) as duration_seconds,
                       quality_issues
                FROM etl_job_executions
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            
            jobs = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'job_name': job[0],
                    'status': job[1],
                    'records_extracted': job[2] or 0,
                    'records_transformed': job[3] or 0,
                    'records_loaded': job[4] or 0,
                    'start_time': job[5],
                    'duration_seconds': job[6] or 0,
                    'quality_issues': json.loads(job[7]) if job[7] else []
                }
                for job in jobs
            ]
        except Exception as e:
            print(f"Error loading ETL history: {e}")
            return []
    
    def get_species_data(self):
        """Get species observation data"""
        conn = self.get_connection()
        if conn is None:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT common_name, COUNT(*) as count,
                       AVG(quality_score) as avg_quality,
                       COUNT(DISTINCT location_description) as location_count
                FROM wildlife_silver 
                WHERE common_name IS NOT NULL
                GROUP BY common_name
                ORDER BY count DESC
                LIMIT 20
            """)
            
            species = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'name': species_data[0],
                    'observations': species_data[1],
                    'avg_quality': round(species_data[2], 3) if species_data[2] else 0,
                    'locations': species_data[3]
                }
                for species_data in species
            ]
        except Exception as e:
            print(f"Error loading species data: {e}")
            return []

dashboard = UnifiedWildlifeDashboard()

def get_database_stats():
    """Get basic database statistics for compatibility"""
    try:
        etl_summary = dashboard.get_etl_summary()
        species_data = dashboard.get_species_data()
        
        return {
            'total_observations': etl_summary.get('silver_count', 0),
            'species_count': len(species_data),
            'recent_sightings': [],
            'species_data': species_data[:10],
            'location_data': [],
            'etl_summary': etl_summary
        }
    except Exception as e:
        print(f"Error in get_database_stats: {e}")
        return {
            'total_observations': 0,
            'species_count': 0,
            'recent_sightings': [],
            'species_data': [],
            'location_data': [],
            'etl_summary': {}
        }
        
        # Species data for charts
        cursor.execute("""
            SELECT common_name, COUNT(*) as count
            FROM wildlife_sightings 
            WHERE common_name != 'Unknown species'
            GROUP BY common_name
            ORDER BY count DESC
            LIMIT 10
        """)
        species_data = cursor.fetchall()
        
        # Location data
        cursor.execute("""
            SELECT location_description, COUNT(*) as count
            FROM wildlife_sightings 
            WHERE location_description != 'Unknown location'
            GROUP BY location_description
            ORDER BY count DESC
            LIMIT 10
        """)
        location_data = cursor.fetchall()
        
        return {
            'total_sightings': total_sightings,
            'species_count': species_count,
            'recent_sightings': recent_sightings,
            'species_data': species_data,
            'location_data': location_data
        }

# Routes
@app.route('/')
def index():
    """Main unified dashboard page"""
    stats = get_database_stats()
    etl_jobs = dashboard.get_etl_job_history(10)
    return render_template('unified_dashboard.html', stats=stats, etl_jobs=etl_jobs)

@app.route('/etl-monitoring')
def etl_monitoring():
    """ETL Pipeline Monitoring Page"""
    etl_summary = dashboard.get_etl_summary()
    etl_jobs = dashboard.get_etl_job_history(20)
    return render_template('etl_monitoring.html', etl_summary=etl_summary, etl_jobs=etl_jobs)

@app.route('/data-quality')
def data_quality():
    """Data Quality Dashboard"""
    stats = get_database_stats()
    return render_template('data_quality.html', stats=stats)

@app.route('/species-explorer')
def species_explorer():
    """Species Explorer Interface"""
    species_data = dashboard.get_species_data()
    return render_template('species_explorer.html', species=species_data)

@app.route('/run-etl', methods=['POST'])
def run_etl():
    """Execute ETL pipeline"""
    try:
        result = subprocess.run(
            [sys.executable, 'scripts/enhanced_etl_demo.py'], 
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        return jsonify({
            'success': result.returncode == 0,
            'output': result.stdout if result.returncode == 0 else result.stderr,
            'message': 'ETL pipeline completed successfully!' if result.returncode == 0 else 'ETL pipeline failed!'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'output': str(e),
            'message': 'Error executing ETL pipeline'
        })

# API Endpoints
@app.route('/api/stats')
def api_stats():
    """API endpoint for getting database statistics"""
    return jsonify(get_database_stats())

@app.route('/api/etl-summary')
def api_etl_summary():
    """API endpoint for ETL summary"""
    return jsonify(dashboard.get_etl_summary())

@app.route('/api/etl-jobs')
def api_etl_jobs():
    """API endpoint for ETL job history"""
    return jsonify(dashboard.get_etl_job_history())

@app.route('/api/species')
def api_species():
    """API endpoint for species data"""
    return jsonify(dashboard.get_species_data())

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("🦘 Starting Unified Australian Wildlife Analytics Dashboard...")
    print("📊 Comprehensive ETL & Analytics Interface")
    print("🔗 Dashboard available at: http://localhost:5000")
    print("🌐 Features:")
    print("   • ETL Pipeline Monitoring")
    print("   • Data Quality Dashboard")  
    print("   • Species Explorer")
    print("   • Real-time Analytics")
    print("   • Unified Interface")
    print()
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='localhost', port=5000)
