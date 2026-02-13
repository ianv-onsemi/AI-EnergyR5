#!/usr/bin/env python3
"""Test the new date range functions"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the functions we want to test
from web.ingestion_trigger import (
    get_last_timestamp_by_source,
    calculate_date_range,
    generate_timestamps_for_date_range
)

def test_calculate_date_range():
    """Test the calculate_date_range function"""
    print("=" * 60)
    print("Testing calculate_date_range function")
    print("=" * 60)
    
    # Test case 1: No last timestamp (None)
    start, end = calculate_date_range(None)
    print(f"\nTest 1 - No last timestamp:")
    print(f"  Start: {start}, End: {end}")
    print(f"  Expected: yesterday to today")
    
    # Test case 2: Last timestamp is yesterday
    yesterday = datetime.now() - timedelta(days=1)
    start, end = calculate_date_range(yesterday)
    print(f"\nTest 2 - Last timestamp is yesterday ({yesterday}):")
    print(f"  Start: {start}, End: {end}")
    print(f"  Expected: today to today")
    
    # Test case 3: Last timestamp is today (database up to date)
    today = datetime.now()
    start, end = calculate_date_range(today)
    print(f"\nTest 3 - Last timestamp is today ({today}):")
    print(f"  Start: {start}, End: {end}")
    print(f"  Expected: None, None (database up to date)")
    
    # Test case 4: Last timestamp is 3 days ago
    three_days_ago = datetime.now() - timedelta(days=3)
    start, end = calculate_date_range(three_days_ago)
    print(f"\nTest 4 - Last timestamp is 3 days ago ({three_days_ago}):")
    print(f"  Start: {start}, End: {end}")
    print(f"  Expected: 2 days ago to today")

def test_generate_timestamps():
    """Test the generate_timestamps_for_date_range function"""
    print("\n" + "=" * 60)
    print("Testing generate_timestamps_for_date_range function")
    print("=" * 60)
    
    today = datetime.now().date()
    
    # Test case 1: Single day (today)
    print(f"\nTest 1 - Single day ({today}):")
    timestamps = generate_timestamps_for_date_range(today, today, 10)
    print(f"  Generated {len(timestamps)} timestamps:")
    for i, ts in enumerate(timestamps):
        print(f"    {i+1}. {ts}")
    
    # Test case 2: 3-day range
    start_date = today - timedelta(days=2)
    print(f"\nTest 2 - 3-day range ({start_date} to {today}):")
    timestamps = generate_timestamps_for_date_range(start_date, today, 10)
    print(f"  Generated {len(timestamps)} timestamps:")
    for i, ts in enumerate(timestamps):
        print(f"    {i+1}. {ts}")

def test_database_queries():
    """Test database query functions"""
    print("\n" + "=" * 60)
    print("Testing database query functions")
    print("=" * 60)
    
    # Test getting latest timestamps
    print("\nFetching latest timestamps from database...")
    
    openweather_latest = get_last_timestamp_by_source('openweather')
    print(f"OpenWeather latest: {openweather_latest}")
    
    nasa_latest = get_last_timestamp_by_source('nasa_power')
    print(f"NASA POWER latest: {nasa_latest}")
    
    # Calculate date ranges
    if openweather_latest:
        ow_start, ow_end = calculate_date_range(openweather_latest)
        print(f"\nOpenWeather date range: {ow_start} to {ow_end}")
    
    if nasa_latest:
        nasa_start, nasa_end = calculate_date_range(nasa_latest)
        print(f"NASA POWER date range: {nasa_start} to {nasa_end}")

if __name__ == "__main__":
    print("Testing Date Range Functions")
    print("=" * 60)
    
    test_calculate_date_range()
    test_generate_timestamps()
    test_database_queries()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
