#!/usr/bin/env python3
"""Check database status"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def check_status():
    conn = get_connection()
    cur = conn.cursor()
    
    # Check all sources
    cur.execute('SELECT source, COUNT(*) FROM sensor_data GROUP BY source ORDER BY source')
    sources = cur.fetchall()
    print('All sources:')
    for source, count in sources:
        print(f'  {source}: {count}')
    
    # Check recent NASA_POWER records
    cur.execute("""SELECT timestamp, source FROM sensor_data 
    WHERE source = 'nasa_power' 
    ORDER BY timestamp DESC 
    LIMIT 5""")
    recent = cur.fetchall()
    print('\nRecent NASA_POWER records:')
    for row in recent:
        print(f'  {row[0]} - {row[1]}')
    
    # Check date range for NASA_POWER
    cur.execute("""SELECT MIN(timestamp), MAX(timestamp), COUNT(*) 
    FROM sensor_data WHERE source = 'nasa_power'""")
    nasa_range = cur.fetchone()
    print(f'\nNASA POWER range: {nasa_range[0]} to {nasa_range[1]} ({nasa_range[2]} rows)')
    
    conn.close()

if __name__ == "__main__":
    check_status()
