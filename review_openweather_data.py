#!/usr/bin/env python3
"""
Script to review and display all OpenWeather data from the database.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'db'))

from db_connector import get_connection

def review_openweather_data():
    """Review and display all OpenWeather data from database"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Query all OpenWeather data (source != 'sim')
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed, source
                FROM sensor_data
                WHERE source != 'sim'
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()
        conn.close()

        print("=== OPENWEATHER DATA REVIEW ===")
        print(f"Total records found: {len(rows)}")
        print()

        if not rows:
            print("No OpenWeather data found in database.")
            return

        print("Data details:")
        print("-" * 100)
        print(f"{'Timestamp':<20} {'Temp(°C)':<10} {'Humidity(%)':<12} {'Irradiance(W/m²)':<18} {'Wind(m/s)':<10} {'Source':<10}")
        print("-" * 100)

        for row in rows:
            timestamp = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else 'N/A'
            temp = f"{row[1]:.2f}" if row[1] else 'N/A'
            humidity = f"{row[2]:.2f}" if row[2] else 'N/A'
            irradiance = f"{row[3]:.2f}" if row[3] else 'N/A'
            wind_speed = f"{row[4]:.2f}" if row[4] else 'N/A'
            source = row[5] if row[5] else 'N/A'

            print(f"{timestamp:<20} {temp:<10} {humidity:<12} {irradiance:<18} {wind_speed:<10} {source:<10}")

        print("-" * 100)

        # Summary statistics
        print("\n=== SUMMARY STATISTICS ===")
        temperatures = [row[1] for row in rows if row[1] is not None]
        humidities = [row[2] for row in rows if row[2] is not None]
        irradiances = [row[3] for row in rows if row[3] is not None]
        wind_speeds = [row[4] for row in rows if row[4] is not None]

        if temperatures:
            print(f"Temperature: Min={min(temperatures):.2f}°C, Max={max(temperatures):.2f}°C, Avg={sum(temperatures)/len(temperatures):.2f}°C")
        if humidities:
            print(f"Humidity: Min={min(humidities):.2f}%, Max={max(humidities):.2f}%, Avg={sum(humidities)/len(humidities):.2f}%")
        if irradiances:
            print(f"Irradiance: Min={min(irradiances):.2f} W/m², Max={max(irradiances):.2f} W/m², Avg={sum(irradiances)/len(irradiances):.2f} W/m²")
        if wind_speeds:
            print(f"Wind Speed: Min={min(wind_speeds):.2f} m/s, Max={max(wind_speeds):.2f} m/s, Avg={sum(wind_speeds)/len(wind_speeds):.2f} m/s")

    except Exception as e:
        print(f"Error reviewing OpenWeather data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    review_openweather_data()
