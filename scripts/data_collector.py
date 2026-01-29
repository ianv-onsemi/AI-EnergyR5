import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_connector import get_connection

collection_file = 'data/collect1.txt'

def collect_data():
    # Get existing timestamps to avoid duplicates
    existing_sim = set()
    existing_api = set()
    existing_api_sources = set()
    file_exists = os.path.exists(collection_file)
    if file_exists:
        with open(collection_file, 'r') as f:
            current_group = None
            for line in f:
                line = line.strip()
                if line == '[sim]':
                    current_group = 'sim'
                elif line.startswith('[') and line.endswith(']') and line != '[sim]':
                    current_group = line[1:-1]
                    existing_api_sources.add(current_group)
                elif line and not line.startswith('timestamp') and current_group and ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 1:
                        timestamp = parts[0]
                        if current_group == 'sim':
                            existing_sim.add(timestamp)
                        else:
                            existing_api.add(timestamp)

    # Fetch sim data from sensor_logs.txt
    sim_data = []
    sensor_logs_path = 'data/sensor_logs.txt'
    if os.path.exists(sensor_logs_path):
        with open(sensor_logs_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.lower().startswith('timestamp'):
                    parts = line.split(',')
                    if len(parts) == 5:
                        timestamp = parts[0]
                        if timestamp not in existing_sim:
                            sim_data.append(tuple(parts))
                            existing_sim.add(timestamp)

    # Fetch api data from database and group by inferred source
    api_data_by_source = {}
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed FROM sensor_data ORDER BY timestamp")
            rows = cur.fetchall()
        conn.close()
        for row in rows:
            timestamp = str(row[0])
            if timestamp not in existing_api:
                data_tuple = (timestamp, str(row[1]), str(row[2]), str(row[3]), str(row[4]))
                # Infer source based on data patterns
                temperature = float(row[1])
                irradiance = float(row[3])
                wind_speed = float(row[4])

                # OpenWeather: typically has temperature around 20-35°C, irradiance=0, wind_speed varies
                if irradiance == 0.0 and 15 <= temperature <= 40:
                    source = "group openweather"
                # NASA Power: typically has high irradiance values, temperature might be missing or different
                elif irradiance > 100:
                    source = "nasa_power"
                else:
                    source = "unknown"

                if source not in api_data_by_source:
                    api_data_by_source[source] = []
                api_data_by_source[source].append(data_tuple)
                existing_api.add(timestamp)
    except Exception as e:
        print(f"Error fetching from database: {e}")

    # Append new data to collection file
    with open(collection_file, 'w') as f:  # Use 'w' to overwrite with fresh data
        from datetime import datetime
        f.write(f'# Data collection last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
        f.write('[sim]\n')
        f.write('timestamp,temperature,humidity,irradiance,wind_speed\n')
        for data in sorted(sim_data, key=lambda x: x[0]):
            f.write(','.join(data) + '\n')
        for source, data_list in api_data_by_source.items():
            f.write(f'\n[{source}]\n')
            f.write('timestamp,temperature,humidity,irradiance,wind_speed\n')
            for data in sorted(data_list, key=lambda x: x[0]):
                f.write(','.join(data) + '\n')

if __name__ == '__main__':
    collect_data()
    print("Data collection completed.")
