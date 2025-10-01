import sqlite3

conn = sqlite3.connect('data/aussie_wildlife.db')

print("Bronze layer columns:")
bronze_cols = conn.execute("PRAGMA table_info(wildlife_bronze)").fetchall()
for col in bronze_cols:
    print(f"  {col[1]} ({col[2]})")

print("\nGold layer columns:")
gold_cols = conn.execute("PRAGMA table_info(wildlife_gold)").fetchall()
for col in gold_cols:
    print(f"  {col[1]} ({col[2]})")

conn.close()