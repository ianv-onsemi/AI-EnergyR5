import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_connector import get_connection

def count_data_sources():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed FROM sensor_data ORDER BY timestamp")
            rows = cur.fetchall()
        conn.close()

        sim_count = 0
        openweather_count = 0
        nasa_power_count = 0
        unknown_count = 0

        for row in rows:
            temperature = float(row[1])
            irradiance = float(row[3])
            wind_speed = float(row[4])

            # Infer source based on data patterns
            if irradiance == 0.0 and 15 <= temperature <= 40:
                openweather_count += 1
            elif irradiance > 100:
                nasa_power_count += 1
            else:
                unknown_count += 1

        # Count sim data from sensor_logs.txt
        sensor_logs_path = 'data/sensor_logs.txt'
        if os.path.exists(sensor_logs_path):
            with open(sensor_logs_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.lower().startswith('timestamp'):
                        parts = line.split(',')
                        if len(parts) == 5:
                            sim_count += 1

        print(f"Sim data: {sim_count}")
        print(f"OpenWeather data: {openweather_count}")
        print(f"NASA Power data: {nasa_power_count}")
        print(f"Unknown/other data: {unknown_count}")
        print(f"Total database rows: {len(rows)}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    count_data_sources()
