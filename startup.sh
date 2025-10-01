# Azure App Service startup script for Australian Wildlife Analytics Platform

# Create necessary directories
mkdir -p data
mkdir -p logs

# Set environment variables for production
export STREAMLIT_SERVER_PORT=${PORT:-8000}
export STREAMLIT_SERVER_ADDRESS="0.0.0.0"
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Initialize database if it doesn't exist
if [ ! -f "data/aussie_wildlife.db" ]; then
    echo "Initializing database..."
    python -c "
import sqlite3
import os

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Create database
conn = sqlite3.connect('data/aussie_wildlife.db')
cursor = conn.cursor()

# Create basic tables
cursor.execute('''
    CREATE TABLE IF NOT EXISTS wildlife_multisource (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        common_name TEXT,
        scientific_name TEXT,
        location_description TEXT,
        latitude REAL,
        longitude REAL,
        observed_date TEXT,
        observer_name TEXT,
        data_source TEXT,
        collected_at TEXT
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS wildlife_silver (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        common_name TEXT,
        scientific_name TEXT,
        location_description TEXT,
        latitude REAL,
        longitude REAL,
        observed_date TEXT,
        observer_name TEXT,
        data_source TEXT,
        processed_at TEXT,
        quality_score REAL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS etl_execution_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_time TEXT,
        status TEXT,
        records_processed INTEGER,
        execution_duration REAL
    )
''')

conn.commit()
conn.close()
print('Database initialized successfully')
"
fi

# Start the Streamlit application
streamlit run streamlit_dashboard.py --server.port=$STREAMLIT_SERVER_PORT --server.address=$STREAMLIT_SERVER_ADDRESS --server.headless=true