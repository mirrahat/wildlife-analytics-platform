import sqlite3
import pandas as pd

def check_data_sources():
    """Check data sources in all tables"""
    conn = sqlite3.connect('aussie_wildlife.db')
    
    print("=== Data Sources Analysis ===")
    
    # Check multi-source table
    try:
        query = "SELECT DISTINCT data_source, COUNT(*) as count FROM wildlife_multisource GROUP BY data_source"
        multisource_df = pd.read_sql_query(query, conn)
        print("\n🌐 Multi-source table sources:")
        print(multisource_df)
    except Exception as e:
        print(f"Multi-source table error: {e}")
    
    # Check silver layer table
    try:
        query = "SELECT DISTINCT data_source, COUNT(*) as count FROM wildlife_silver GROUP BY data_source"
        silver_df = pd.read_sql_query(query, conn)
        print("\n🥈 Silver layer table sources:")
        print(silver_df)
    except Exception as e:
        print(f"Silver layer table error: {e}")
    
    # Check bronze layer table
    try:
        query = "SELECT DISTINCT data_source, COUNT(*) as count FROM wildlife_bronze GROUP BY data_source"
        bronze_df = pd.read_sql_query(query, conn)
        print("\n🥉 Bronze layer table sources:")
        print(bronze_df)
    except Exception as e:
        print(f"Bronze layer table error: {e}")
    
    # Check if silver layer has multi-source data
    try:
        query = "SELECT COUNT(*) as total_silver FROM wildlife_silver"
        total_silver = pd.read_sql_query(query, conn)
        print(f"\n📊 Total Silver layer records: {total_silver['total_silver'].iloc[0]}")
        
        query = "SELECT COUNT(*) as total_multi FROM wildlife_multisource"
        total_multi = pd.read_sql_query(query, conn)
        print(f"📊 Total Multi-source records: {total_multi['total_multi'].iloc[0]}")
    except Exception as e:
        print(f"Count error: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_data_sources()