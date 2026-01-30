#!/usr/bin/env python3
"""
Script to retrieve all data from database (all sources) and update collectAll.txt
"""

import sys
import os
from datetime import datetime
from collections import defaultdict

# Add db directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'db'))

from db_connector import get_connection

def update_collectAll():
    """Retrieve all data from database and update collectAll.txt"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Query all data from sensor_data table
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed, source
                FROM sensor_data
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()
        conn.close()

        if not rows:
            print("No data found in database.")
            return

        # Calculate statistics
        total_rows = len(rows)
        source_counts = defaultdict(int)
        for row in rows:
            source = row[5] if row[5] else 'unknown'
            source_counts[source] += 1

        # Prepare header
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        source_summary = ' | '.join([f"{source}: {count}" for source, count in sorted(source_counts.items())])
        header = f"Data retrieved at: {current_timestamp} | Total rows: {total_rows} | {source_summary}"

        # Group data by source
        data_by_source = defaultdict(list)
        for row in rows:
            source = row[5] if row[5] else 'unknown'
            data_by_source[source].append(row)

        # Write to collectAll.txt
        file_path = os.path.join('data', 'collectAll.txt')

        with open(file_path, 'w') as f:
            f.write(header + '\n\n')

            # Write data for each source
            for source in sorted(data_by_source.keys()):
                source_upper = source.upper()
                f.write(f"--- {source_upper} DATA ---\n")
                f.write("id,timestamp,temperature,humidity,irradiance,wind_speed,source\n")

                # Sort by timestamp DESC for each source
                sorted_data = sorted(data_by_source[source], key=lambda x: x[0] or datetime.min, reverse=True)

                for idx, row in enumerate(sorted_data, 1):
                    timestamp_str = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else ''
                    temp = f"{row[1]:.2f}" if row[1] is not None else ''
                    humidity = f"{row[2]:.2f}" if row[2] is not None else ''
                    irradiance = f"{row[3]:.2f}" if row[3] is not None else ''
                    wind_speed = f"{row[4]:.2f}" if row[4] is not None else ''
                    source_val = row[5] if row[5] else ''

                    f.write(f"{idx},{timestamp_str},{temp},{humidity},{irradiance},{wind_speed},{source_val}\n")

                f.write('\n')

        print(f"Successfully updated collectAll.txt with {total_rows} rows from database")
        print(f"Data sources: {source_summary}")

    except Exception as e:
        print(f"Error updating collectAll.txt: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_collectAll()
