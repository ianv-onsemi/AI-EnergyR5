#!/usr/bin/env python3
"""Verify hourly coverage for both OpenWeather and NASA POWER"""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def check_hourly_coverage():
    conn = get_connection()
    cur = conn.cursor()
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    print(f"Checking hourly coverage from {start_date} to {end_date}")
    print(f"Expected hours: {(end_date - start_date).days * 24 + (end_date - start_date).seconds // 3600}")
    print("=" * 70)
    
    for source in ['openweather', 'nasa_power']:
        print(f"\n{source.upper()} Coverage:")
        print("-" * 70)
        
        # Get all timestamps for this source
        cur.execute("""
            SELECT timestamp 
            FROM sensor_data 
            WHERE source = %s
            AND timestamp >= %s AND timestamp <= %s
            ORDER BY timestamp
        """, (source, start_date, end_date))
        
        timestamps = [row[0] for row in cur.fetchall()]
        actual_count = len(timestamps)
        
        # Calculate expected hours
        expected_hours = int((end_date - start_date).total_seconds() / 3600) + 1
        
        print(f"  Total records: {actual_count}")
        print(f"  Expected hours: {expected_hours}")
        print(f"  Coverage: {actual_count / expected_hours * 100:.2f}%")
        
        # Check for gaps
        if timestamps:
            # Create a set of all expected hours
            expected_set = set()
            current = start_date.replace(minute=0, second=0, microsecond=0)
            while current <= end_date:
                expected_set.add(current)
                current += timedelta(hours=1)
            
            # Create set of actual timestamps
            actual_set = set(ts.replace(minute=0, second=0, microsecond=0) for ts in timestamps)
            
            # Find gaps
            gaps = sorted(expected_set - actual_set)
            
            if gaps:
                print(f"\n  ⚠️  Gaps found: {len(gaps)} missing hours")
                print(f"  First 10 gaps:")
                for gap in gaps[:10]:
                    print(f"    - {gap}")
            else:
                print(f"\n  ✅ Complete coverage - no gaps!")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("Both sources should have hourly data from Jan 1, 2026 to present.")
    print("Target: 24 data points per day for each source")

if __name__ == "__main__":
    check_hourly_coverage()
