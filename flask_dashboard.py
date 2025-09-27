#!/usr/bin/env python3
"""
Australian Wildlife Data Flask Dashboard
=======================================
Modern Flask web interface for exploring wildlife observation data and ETL pipeline results.

Features:
- Real-time data visualization with Plotly
- ETL pipeline monitoring and execution
- Interactive species exploration
- Data quality dashboard
- Multi-source analytics
- Australian biodiversity insights
- REST API endpoints

Run with: python flask_dashboard.py
Access at: http://localhost:5000
"""

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, flash
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.utils
import json
from datetime import datetime, timedelta
import os
import sys
import subprocess
import threading
import time
from werkzeug.serving import make_server
import logging

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'australian_wildlife_biodiversity_2025'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WildlifeDashboard:
    def __init__(self, db_path="data/aussie_wildlife.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            return None
        return sqlite3.connect(self.db_path)
    
    def load_etl_layers_summary(self):
        """Load ETL layers summary"""
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
            
            cursor.execute("SELECT AVG(quality_score) FROM wildlife_silver")
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
                'avg_quality': avg_quality,
                'total_jobs': job_stats[0],
                'successful_jobs': job_stats[1]
            }
        except Exception as e:
            logger.error(f"Error loading ETL summary: {e}")
            if conn:
                conn.close()
            return {}
    
    def load_etl_job_history(self):
        """Load ETL job execution history"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT job_name, status, 
                       records_extracted, records_transformed, records_loaded,
                       datetime(start_time) as start_time,
                       datetime(end_time) as end_time,
                       ROUND((julianday(end_time) - julianday(start_time)) * 86400, 2) as duration_seconds,
                       quality_issues
                FROM etl_job_executions
                ORDER BY start_time DESC
                LIMIT 20
            """, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error loading ETL history: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()
    
    def load_silver_layer_data(self):
        """Load cleaned data from silver layer"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT common_name, scientific_name, location_description,
                       latitude, longitude, observed_date, observer_name,
                       quality_score, data_source
                FROM wildlife_silver
                WHERE common_name IS NOT NULL
                ORDER BY processed_at DESC
            """, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error loading silver layer data: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()
    
    def load_multisource_data(self):
        """Load multi-source data"""
        conn = self.get_connection()
        if conn is None:
            return pd.DataFrame()
        
        try:
            df = pd.read_sql_query("""
                SELECT * FROM wildlife_multisource 
                ORDER BY collected_at DESC
                LIMIT 1000
            """, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"Error loading multi-source data: {e}")
            if conn:
                conn.close()
            return pd.DataFrame()

# Initialize dashboard
dashboard = WildlifeDashboard()

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Load ETL summary
        etl_summary = dashboard.load_etl_layers_summary()
        
        # Load silver layer data for additional stats
        silver_data = dashboard.load_silver_layer_data()
        
        # Create stats object that matches template expectations
        stats = {
            'total_sightings': etl_summary.get('silver_count', 0),
            'species_count': len(silver_data['common_name'].dropna().unique()) if not silver_data.empty else 0,
            'bronze_count': etl_summary.get('bronze_count', 0),
            'silver_count': etl_summary.get('silver_count', 0),
            'gold_count': etl_summary.get('gold_count', 0),
            'avg_quality': etl_summary.get('avg_quality', 0),
            'total_jobs': etl_summary.get('total_jobs', 0),
            'successful_jobs': etl_summary.get('successful_jobs', 0),
            'location_data': []  # Will be populated by the chart data endpoint
        }
        
        # Calculate success rate
        if stats['total_jobs'] > 0:
            stats['success_rate'] = (stats['successful_jobs'] / stats['total_jobs']) * 100
        else:
            stats['success_rate'] = 0
        
        return render_template('dashboard.html', 
                             stats=stats,
                             etl_summary=etl_summary, 
                             page_title="Australian Wildlife Analytics")
    
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Provide empty stats if there's an error
        empty_stats = {
            'total_sightings': 0,
            'species_count': 0,
            'bronze_count': 0,
            'silver_count': 0,
            'gold_count': 0,
            'avg_quality': 0,
            'total_jobs': 0,
            'successful_jobs': 0,
            'success_rate': 0,
            'location_data': []
        }
        return render_template('dashboard.html', 
                             stats=empty_stats,
                             etl_summary={}, 
                             page_title="Australian Wildlife Analytics")

@app.route('/etl-monitoring')
def etl_monitoring():
    """ETL monitoring page"""
    etl_history = dashboard.load_etl_job_history()
    return render_template('etl_monitoring.html', 
                         etl_history=etl_history.to_dict('records') if not etl_history.empty else [],
                         page_title="ETL Monitoring")

@app.route('/data-quality')
def data_quality():
    """Data quality dashboard"""
    silver_data = dashboard.load_silver_layer_data()
    return render_template('data_quality.html', 
                         silver_data=silver_data.to_dict('records') if not silver_data.empty else [],
                         page_title="Data Quality")

@app.route('/species-explorer')
def species_explorer():
    """Species exploration interface"""
    silver_data = dashboard.load_silver_layer_data()
    species_list = []
    if not silver_data.empty:
        species_list = sorted(silver_data['common_name'].dropna().unique())
    
    return render_template('species_explorer.html', 
                         species_list=species_list,
                         page_title="Species Explorer")

@app.route('/multi-source-analytics')
def multi_source_analytics():
    """Multi-source analytics page"""
    multisource_data = dashboard.load_multisource_data()
    return render_template('multi_source_analytics.html', 
                         has_data=not multisource_data.empty,
                         page_title="Multi-Source Analytics")

# API Routes
@app.route('/api/etl-summary')
def api_etl_summary():
    """API endpoint for ETL summary"""
    return jsonify(dashboard.load_etl_layers_summary())

@app.route('/api/species-map')
def api_species_map():
    """API endpoint for species distribution map"""
    silver_data = dashboard.load_silver_layer_data()
    
    if silver_data.empty or 'latitude' not in silver_data.columns:
        return jsonify({'error': 'No location data available'})
    
    # Filter for valid coordinates
    map_data = silver_data.dropna(subset=['latitude', 'longitude'])
    
    if map_data.empty:
        return jsonify({'error': 'No coordinate data available'})
    
    fig = px.scatter_map(
        map_data,
        lat="latitude",
        lon="longitude",
        hover_name="common_name",
        hover_data={"location_description": True, "observed_date": True, "quality_score": ":.3f"},
        color="common_name",
        zoom=4,
        height=500,
        title="Wildlife Observations Across Australia"
    )
    
    fig.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    
    return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))

@app.route('/api/species-observations')
def api_species_observations():
    """API endpoint for species observations chart"""
    silver_data = dashboard.load_silver_layer_data()
    
    if silver_data.empty:
        return jsonify({'error': 'No species data available'})
    
    species_counts = silver_data['common_name'].value_counts().head(10)
    
    fig = px.bar(
        x=species_counts.values,
        y=species_counts.index,
        orientation='h',
        title="Top 10 Most Observed Species",
        labels={'x': 'Observations', 'y': 'Species'}
    )
    
    fig.update_layout(height=500)
    
    return jsonify(json.loads(plotly.utils.PlotlyJSONEncoder().encode(fig)))

@app.route('/api/etl-performance')
def api_etl_performance():
    """API endpoint for ETL performance charts"""
    etl_history = dashboard.load_etl_job_history()
    
    if etl_history.empty:
        return jsonify({'error': 'No ETL history available'})
    
    # Success rate pie chart
    success_counts = etl_history['status'].value_counts()
    
    pie_fig = px.pie(
        values=success_counts.values,
        names=success_counts.index,
        title="ETL Job Status Distribution",
        color_discrete_map={'success': '#28a745', 'failed': '#dc3545'}
    )
    
    # Duration trend
    etl_history['start_time'] = pd.to_datetime(etl_history['start_time'])
    
    line_fig = px.line(
        etl_history,
        x='start_time',
        y='duration_seconds',
        color='job_name',
        title="ETL Job Duration Over Time",
        labels={'start_time': 'Execution Time', 'duration_seconds': 'Duration (seconds)'}
    )
    
    return jsonify({
        'pie_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(pie_fig)),
        'line_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(line_fig))
    })

@app.route('/api/data-quality-charts')
def api_data_quality_charts():
    """API endpoint for data quality charts"""
    silver_data = dashboard.load_silver_layer_data()
    
    if silver_data.empty:
        return jsonify({'error': 'No quality data available'})
    
    # Data completeness
    completeness_data = []
    for column in ['common_name', 'scientific_name', 'location_description', 
                  'latitude', 'longitude', 'observed_date', 'observer_name']:
        if column in silver_data.columns:
            completeness = (silver_data[column].notna().sum() / len(silver_data)) * 100
            completeness_data.append({'Field': column, 'Completeness (%)': completeness})
    
    completeness_df = pd.DataFrame(completeness_data)
    
    completeness_fig = px.bar(
        completeness_df,
        x='Field',
        y='Completeness (%)',
        title="Data Field Completeness",
        color='Completeness (%)',
        color_continuous_scale='RdYlGn'
    )
    completeness_fig.update_layout(xaxis_tickangle=45)
    
    # Quality score distribution
    quality_fig = None
    if 'quality_score' in silver_data.columns:
        quality_fig = px.histogram(
            silver_data,
            x='quality_score',
            nbins=20,
            title="Quality Score Distribution",
            labels={'quality_score': 'Quality Score', 'count': 'Number of Records'}
        )
    
    # Data source breakdown
    source_fig = None
    if 'data_source' in silver_data.columns:
        source_counts = silver_data['data_source'].value_counts()
        source_fig = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            title="Data Sources Distribution"
        )
    
    return jsonify({
        'completeness_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(completeness_fig)),
        'quality_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(quality_fig)) if quality_fig else None,
        'source_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(source_fig)) if source_fig else None
    })

@app.route('/api/species/<species_name>')
def api_species_detail(species_name):
    """API endpoint for species detail"""
    silver_data = dashboard.load_silver_layer_data()
    
    if silver_data.empty:
        return jsonify({'error': 'No species data available'})
    
    species_data = silver_data[silver_data['common_name'] == species_name]
    
    if species_data.empty:
        return jsonify({'error': 'Species not found'})
    
    # Species metrics
    metrics = {
        'total_observations': len(species_data),
        'unique_locations': species_data['location_description'].nunique(),
        'avg_quality': species_data['quality_score'].mean(),
        'observation_days': species_data['observed_date'].nunique()
    }
    
    # Location chart
    location_counts = species_data['location_description'].value_counts().head(10)
    location_fig = px.bar(
        x=location_counts.values,
        y=location_counts.index,
        orientation='h',
        title=f"Top Locations for {species_name}",
        labels={'x': 'Observations', 'y': 'Location'}
    )
    
    # Timeline chart
    timeline_fig = None
    if 'observed_date' in species_data.columns:
        species_data['observed_date'] = pd.to_datetime(species_data['observed_date'])
        daily_counts = species_data.groupby(species_data['observed_date'].dt.date).size()
        
        timeline_fig = px.line(
            x=daily_counts.index,
            y=daily_counts.values,
            title=f"{species_name} Observations Over Time",
            labels={'x': 'Date', 'y': 'Observations'}
        )
    
    # Recent observations
    recent_observations = species_data.head(10)[
        ['location_description', 'observed_date', 'observer_name', 'quality_score']
    ].to_dict('records')
    
    return jsonify({
        'metrics': metrics,
        'location_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(location_fig)),
        'timeline_chart': json.loads(plotly.utils.PlotlyJSONEncoder().encode(timeline_fig)) if timeline_fig else None,
        'recent_observations': recent_observations
    })

@app.route('/api/multisource-analytics')
def api_multisource_analytics():
    """API endpoint for multi-source analytics"""
    multisource_data = dashboard.load_multisource_data()
    
    if multisource_data.empty:
        return jsonify({'error': 'No multi-source data available'})
    
    # Source metrics
    metrics = {
        'total_records': len(multisource_data),
        'unique_sources': multisource_data['source'].nunique(),
        'unique_species': multisource_data['scientific_name'].nunique(),
        'date_range': multisource_data['observed_date'].nunique()
    }
    
    # Source distribution
    source_counts = multisource_data['source'].value_counts()
    source_pie = px.pie(
        values=source_counts.values,
        names=source_counts.index,
        title="Distribution of Records Across Sources",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    source_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    # Quality by source
    quality_by_source = []
    for source in multisource_data['source'].unique():
        source_data = multisource_data[multisource_data['source'] == source]
        
        completeness = {
            'coordinates': (source_data[['latitude', 'longitude']].notna().all(axis=1)).mean(),
            'species_info': source_data['scientific_name'].notna().mean(),
            'date_info': source_data['observed_date'].notna().mean(),
            'location_info': source_data['location_description'].notna().mean()
        }
        
        overall_quality = sum(completeness.values()) / len(completeness)
        
        quality_by_source.append({
            'Source': source,
            'Quality Score': overall_quality,
            'Records': len(source_data)
        })
    
    quality_df = pd.DataFrame(quality_by_source)
    quality_scatter = px.scatter(
        quality_df,
        x='Records',
        y='Quality Score',
        size='Records',
        color='Source',
        title="Data Quality vs Volume by Source",
        hover_data=['Source', 'Records', 'Quality Score']
    )
    quality_scatter.update_layout(yaxis_range=[0, 1])
    
    # Geographic map
    geo_data = multisource_data.dropna(subset=['latitude', 'longitude'])
    geo_map = None
    if not geo_data.empty:
        geo_map = px.scatter_map(
            geo_data,
            lat="latitude",
            lon="longitude",
            color="source",
            hover_name="common_name",
            hover_data={"scientific_name": True, "observed_date": True, "source": True},
            title="Wildlife Observations by Data Source",
            zoom=4,
            height=600
        )
        geo_map.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    
    return jsonify({
        'metrics': metrics,
        'source_distribution': json.loads(plotly.utils.PlotlyJSONEncoder().encode(source_pie)),
        'quality_analysis': json.loads(plotly.utils.PlotlyJSONEncoder().encode(quality_scatter)),
        'geographic_map': json.loads(plotly.utils.PlotlyJSONEncoder().encode(geo_map)) if geo_map else None
    })

@app.route('/api/run-etl', methods=['POST'])
def api_run_etl():
    """API endpoint to run ETL pipeline"""
    try:
        current_dir = os.getcwd()
        script_path = os.path.join(current_dir, "scripts", "enhanced_etl_demo.py")
        
        if not os.path.exists(script_path):
            return jsonify({'success': False, 'error': f'ETL script not found at: {script_path}'})
        
        # Run ETL pipeline
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True,
            cwd=current_dir,
            timeout=180,
            encoding='utf-8',
            errors='replace',
            env=dict(os.environ, PYTHONIOENCODING='utf-8')
        )
        
        if result.returncode == 0:
            # Extract success messages
            output_lines = result.stdout.split('\n')
            success_lines = [line for line in output_lines if '✓' in line or 'SUCCESS' in line.upper()]
            
            return jsonify({
                'success': True,
                'message': 'ETL pipeline completed successfully',
                'results': success_lines[-10:] if success_lines else [],
                'full_output': result.stdout[-2000:]
            })
        else:
            return jsonify({
                'success': False,
                'error': 'ETL pipeline failed',
                'details': result.stderr,
                'output': result.stdout[-1500:] if result.stdout else ''
            })
    
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'ETL pipeline timed out after 3 minutes'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error running ETL pipeline: {str(e)}'
        })

@app.route('/api/run-multisource', methods=['POST'])
def api_run_multisource():
    """API endpoint to run multi-source collection"""
    try:
        script_path = os.path.join(os.getcwd(), "src", "multi_source_collector.py")
        
        result = subprocess.run(
            [sys.executable, script_path], 
            capture_output=True, 
            text=True,
            timeout=300,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Multi-source collection completed successfully',
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Multi-source collection failed',
                'details': result.stderr
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error running multi-source collection: {str(e)}'
        })

@app.route('/api/export/<data_type>')
def api_export(data_type):
    """API endpoint for data export"""
    try:
        if data_type == 'multisource_summary':
            multisource_data = dashboard.load_multisource_data()
            if multisource_data.empty:
                return jsonify({'error': 'No data available'})
            
            summary_data = multisource_data.groupby('source').agg({
                'scientific_name': 'nunique',
                'latitude': 'count',
                'observed_date': ['min', 'max']
            }).round(3)
            
            filename = f"multisource_summary_{datetime.now().strftime('%Y%m%d')}.csv"
            summary_data.to_csv(filename)
            
            return send_file(filename, as_attachment=True, download_name=filename)
        
        elif data_type == 'coordinates':
            multisource_data = dashboard.load_multisource_data()
            if multisource_data.empty:
                return jsonify({'error': 'No data available'})
            
            geo_data = multisource_data.dropna(subset=['latitude', 'longitude'])
            geo_export = geo_data[['source', 'scientific_name', 'common_name', 'latitude', 'longitude', 'location_description']].copy()
            
            filename = f"multisource_coordinates_{datetime.now().strftime('%Y%m%d')}.csv"
            geo_export.to_csv(filename, index=False)
            
            return send_file(filename, as_attachment=True, download_name=filename)
        
        elif data_type == 'full_dataset':
            multisource_data = dashboard.load_multisource_data()
            if multisource_data.empty:
                return jsonify({'error': 'No data available'})
            
            filename = f"multisource_full_{datetime.now().strftime('%Y%m%d')}.csv"
            multisource_data.to_csv(filename, index=False)
            
            return send_file(filename, as_attachment=True, download_name=filename)
        
        else:
            return jsonify({'error': 'Invalid export type'})
    
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'})

if __name__ == '__main__':
    print("🦘 Starting Australian Wildlife Analytics Flask Dashboard...")
    print("🌐 Dashboard will be available at: http://localhost:5000")
    print("📊 Features: ETL Monitoring, Species Explorer, Multi-Source Analytics")
    print("🚀 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
