import sqlite3

def check_all_tables():
    """Check all tables for multi-source data"""
    conn = sqlite3.connect('aussie_wildlife.db')
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = [t[0] for t in cursor.fetchall()]
    
    print('Checking all tables for data sources...')
    
    for table in tables:
        try:
            cursor.execute(f'SELECT DISTINCT data_source, COUNT(*) FROM {table} GROUP BY data_source')
            sources = cursor.fetchall()
            if sources:
                print(f'\n{table}:')
                for source, count in sources:
                    print(f'  {source}: {count} records')
        except Exception as e:
            # Skip tables without data_source column
            pass
    
    conn.close()

if __name__ == "__main__":
    check_all_tables()