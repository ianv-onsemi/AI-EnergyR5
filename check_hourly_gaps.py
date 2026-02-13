#!/usr/bin/env python3
"""Check database for hourly data gaps from Jan 1, 2026 to today"""

import sys
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def check_hourly_coverage(start_date, end_date):
    """Check hourly data coverage for each source"""
    try:
        conn = get_connection()
        
        # Get all data from Jan 1, 2026 to today for each source
        sources = ['openweather', 'nasa_power']
        coverage = {}
        
        for source in sources:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT timestamp, temperature, humidity, irradiance, wind_speed
                    FROM sensor_data
                    WHERE source = %s
                    AND timestamp >= %s
                    AND timestamp <= %s
                    ORDER BY timestamp ASC
                """, (source, start_date, end_date))
                rows = cur.fetchall()
            
            # Organize by date and hour
            hourly_data = defaultdict(lambda: defaultdict(bool))
            for row in rows:
                ts = row[0]
                date_key = ts.strftime('%Y-%m-%d')
                hour_key = ts.hour
                hourly_data[date_key][hour_key] = True
            
            # Calculate coverage
            total_days = (end_date - start_date).days + 1
            expected_hours = total_days * 24
            actual_hours = sum(len(hours) for hours in hourly_data.values())
            missing_hours = expected_hours - actual_hours
            
            coverage[source] = {
                'total_rows': len(rows),
                'date_range': f"{start_date.date()} to {end_date.date()}",
                'total_days': total_days,
                'expected_hours': expected_hours,
                'actual_hours': actual_hours,
                'missing_hours': missing_hours,
                'coverage_percent': (actual_hours / expected_hours * 100) if expected_hours > 0 else 0,
                'hourly_data': hourly_data,
                'earliest': rows[0][0] if rows else None,
                'latest': rows[-1][0] if rows else None
            }
        
        conn.close()
        return coverage
        
    except Exception as e:
        print(f"Error checking hourly coverage: {e}")
        return None

def print_coverage_report(coverage):
    """Print detailed coverage report"""
    print("=" * 80)
    print("HOURLY DATA COVERAGE REPORT")
    print("=" * 80)
    
    for source, data in coverage.items():
        print(f"\n{'='*80}")
        print(f"Source: {source.upper()}")
        print(f"{'='*80}")
        print(f"Date Range: {data['date_range']}")
        print(f"Total Days: {data['total_days']}")
        print(f"Expected Hours: {data['expected_hours']}")
        print(f"Actual Hours: {data['actual_hours']}")
        print(f"Missing Hours: {data['missing_hours']}")
        print(f"Coverage: {data['coverage_percent']:.2f}%")
        print(f"Earliest Record: {data['earliest']}")
        print(f"Latest Record: {data['latest']}")
        print(f"Total Rows: {data['total_rows']}")
        
        # Show daily breakdown
        print(f"\nDaily Breakdown:")
        print("-" * 40)
        for date in sorted(data['hourly_data'].keys()):
            hours_count = len(data['hourly_data'][date])
            missing = 24 - hours_count
            status = "✅ Complete" if hours_count == 24 else f"⚠️  Missing {missing} hours"
            print(f"  {date}: {hours_count}/24 hours {status}")

def identify_gaps(coverage):
    """Identify specific gaps in hourly data"""
    print(f"\n{'='*80}")
    print("HOURLY GAPS IDENTIFICATION")
    print(f"{'='*80}")
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    for source, data in coverage.items():
        print(f"\n{source.upper()} Gaps:")
        print("-" * 40)
        
        current = start_date
        gaps_found = []
        
        while current <= end_date:
            date_key = current.strftime('%Y-%m-%d')
            hour_key = current.hour
            
            # Check if this hour exists
            if date_key in data['hourly_data']:
                if hour_key not in data['hourly_data'][date_key]:
                    gaps_found.append(current)
            else:
                # Whole day is missing
                gaps_found.append(current)
            
            current += timedelta(hours=1)
        
        # Print gaps summary
        if gaps_found:
            print(f"  Total gaps found: {len(gaps_found)} hours")
            
            # Group consecutive gaps
            if gaps_found:
                gap_groups = []
                current_group = [gaps_found[0]]
                
                for i in range(1, len(gaps_found)):
                    if (gaps_found[i] - gaps_found[i-1]) == timedelta(hours=1):
                        current_group.append(gaps_found[i])
                    else:
                        gap_groups.append(current_group)
                        current_group = [gaps_found[i]]
                gap_groups.append(current_group)
                
                print(f"  Gap groups: {len(gap_groups)}")
                for i, group in enumerate(gap_groups[:10]):  # Show first 10 groups
                    start = group[0]
                    end = group[-1]
                    if len(group) == 1:
                        print(f"    {i+1}. Single hour: {start}")
                    else:
                        print(f"    {i+1}. {start} to {end} ({len(group)} hours)")
                
                if len(gap_groups) > 10:
                    print(f"    ... and {len(gap_groups) - 10} more groups")
        else:
            print("  ✅ No gaps found - hourly coverage is complete!")

if __name__ == "__main__":
    # Define date range: Jan 1, 2026 to today
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    print(f"Checking hourly data coverage from {start_date.date()} to {end_date.date()}")
    print(f"Expected: 24 data points per day for each source")
    
    coverage = check_hourly_coverage(start_date, end_date)
    
    if coverage:
        print_coverage_report(coverage)
        identify_gaps(coverage)
    else:
        print("Failed to retrieve coverage data")
