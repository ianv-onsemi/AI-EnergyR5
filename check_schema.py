import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db.db_connector import get_connection

conn = get_connection()
if conn:
    cur = conn.cursor()
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'sensor_data' 
        ORDER BY ordinal_position;
    """)
    cols = cur.fetchall()
    print("Current sensor_data table columns:")
    for col in cols:
        print(f"  - {col[0]}: {col[1]}")
    conn.close()
else:
    print("Failed to connect to database")
