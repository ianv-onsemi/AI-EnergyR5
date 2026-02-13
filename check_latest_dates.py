#!/usr/bin/env python3
"""Check the latest dates for OpenWeather and NASA POWER data in the database"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def get_latest_dates():
    """Get the latest timestamps from the database for each source"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get latest OpenWeather date
            cur.execute("""
                SELECT MAX(timestamp) 
                FROM sensor_data 
                WHERE source = 'openweather'
            """)
            openweather_latest = cur.fetchone()[0]
            
            # Get latest NASA POWER date
            cur.execute("""
                SELECT MAX(timestamp) 
                FROM sensor_data 
                WHERE source = 'nasa_power'
            """)
            nasa_latest = cur.fetchone()[0]
            
            # Get overall latest date
            cur.execute("""
                SELECT MAX(timestamp) 
                FROM sensor_data
            """)
            overall_latest = cur.fetchone()[0]
            
            # Get date range for each source
            cur.execute("""
                SELECT 
                    source,
                    MIN(timestamp) as earliest,
                    MAX(timestamp) as latest,
                    COUNT(*) as total_rows
                FROM sensor_data
                WHERE source IN ('openweather', 'nasa_power')
                GROUP BY source
            """)
            source_ranges = cur.fetchall()
            
        conn.close()
        
        print("=" * 60)
        print("LATEST DATES IN DATABASE")
        print("=" * 60)
        print(f"\nOpenWeather latest date: {openweather_latest}")
        print(f"NASA POWER latest date: {nasa_latest}")
        print(f"Overall latest date: {overall_latest}")
        
        print("\n" + "-" * 60)
        print("DATE RANGES BY SOURCE")
        print("-" * 60)
        for row in source_ranges:
            source, earliest, latest, count = row
            print(f"\nSource: {source}")
            print(f"  Earliest: {earliest}")
            print(f"  Latest:   {latest}")
            print(f"  Total rows: {count}")
        
        print("\n" + "=" * 60)
        
        return {
            'openweather_latest': openweather_latest,
            'nasa_latest': nasa_latest,
            'overall_latest': overall_latest,
            'source_ranges': source_ranges
        }
        
    except Exception as e:
        print(f"Error checking latest dates: {e}")
        return None

if __name__ == "__main__":
    get_latest_dates()
