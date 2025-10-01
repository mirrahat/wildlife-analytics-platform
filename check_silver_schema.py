import sqlite3

def check_silver_schema():
    """Check schema of silver_wildlife_data table"""
    conn = sqlite3.connect('aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Check silver_wildlife_data schema
    cursor.execute('PRAGMA table_info(silver_wildlife_data)')
    columns = cursor.fetchall()
    print('Silver wildlife data columns:')
    for col in columns:
        print(f'  {col[1]} ({col[2]})')
    
    # Check if there's actually data from multiple sources
    cursor.execute('SELECT DISTINCT data_source, COUNT(*) FROM silver_wildlife_data GROUP BY data_source')
    sources = cursor.fetchall()
    print('\nSilver data sources:')
    for source, count in sources:
        print(f'  {source}: {count} records')
    
    # Check wildlife_sightings for comparison
    cursor.execute('SELECT DISTINCT data_source, COUNT(*) FROM wildlife_sightings GROUP BY data_source')
    main_sources = cursor.fetchall()
    print('\nMain wildlife_sightings data sources:')
    for source, count in main_sources:
        print(f'  {source}: {count} records')
    
    conn.close()

if __name__ == "__main__":
    check_silver_schema()