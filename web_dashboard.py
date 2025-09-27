#!/usr/bin/env python3
"""
Australian Wildlife Web Dashboard
================================
Creates an interactive web dashboard for visualizing wildlife data.
Uses Flask to serve a web page that you can view in your browser.
"""

from flask import Flask, render_template, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

def get_database_stats():
    """Get statistics from the wildlife database"""
    
    db_path = "aussie_wildlife.db"
    
    if not os.path.exists(db_path):
        return {
            'total_sightings': 0,
            'species_count': 0,
            'recent_sightings': [],
            'species_data': [],
            'location_data': []
        }
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        # Total sightings
        cursor.execute("SELECT COUNT(*) FROM wildlife_sightings")
        total_sightings = cursor.fetchone()[0]
        
        # Species count
        cursor.execute("SELECT COUNT(DISTINCT common_name) FROM wildlife_sightings WHERE common_name != 'Unknown species'")
        species_count = cursor.fetchone()[0]
        
        # Recent sightings
        cursor.execute("""
            SELECT common_name, location_description, observed_date, observer_name
            FROM wildlife_sightings 
            ORDER BY observed_date DESC, created_at DESC
            LIMIT 10
        """)
        recent_sightings = cursor.fetchall()
        
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

@app.route('/')
def dashboard():
    """Main dashboard page"""
    stats = get_database_stats()
    return render_template('dashboard.html', stats=stats)

@app.route('/api/data')
def api_data():
    """API endpoint for getting wildlife data as JSON"""
    stats = get_database_stats()
    return jsonify(stats)

@app.route('/api/species')
def api_species():
    """API endpoint for species data"""
    stats = get_database_stats()
    return jsonify({
        'labels': [species[0] for species in stats['species_data']],
        'data': [species[1] for species in stats['species_data']]
    })

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("Starting Australian Wildlife Dashboard...")
    print("Open your web browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='localhost', port=5000)
