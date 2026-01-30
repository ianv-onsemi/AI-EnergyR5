#!/usr/bin/env python3
"""
Script to collect OpenWeather data for Jan 25-30, 2026 and save first 50 rows to database
"""

import sys
import time
from datetime import datetime, timedelta
from api_wrappers.openweather import get_weather_data
from db.db_connector import get_connection

def collect_openweather_data():
    """Collect OpenWeather data and save to database with Jan 25-30 timestamps"""

    print("Starting OpenWeather data collection for Jan 25-30, 2026...")

    # Connect to database
    conn = get_connection()

    # Start date: January 25, 2026
    start_date = datetime(2026, 1, 25, 0, 0, 0)
    current_timestamp = start_date

    collected_count = 0
    max_rows = 50

    try:
        while collected_count < max_rows:
            # Fetch current weather data
            try:
                weather_data = get_weather_data()
                if weather_data:
                    # Use the fetched timestamp but adjust to our date range
                    adjusted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

                    # Extract data from OpenWeather response
                    # weather_data format: (timestamp, wind_speed, wind_dir, solar_irradiance)
                    _, wind_speed, wind_dir, solar_irradiance = weather_data

                    # Create database entry with OpenWeather data
                    # We need to map this to our sensor_data schema: timestamp, temperature, humidity, irradiance, wind_speed, source
                    # Since OpenWeather gives us wind_speed and irradiance, we'll set temperature and humidity to None or default values
                    db_data = (adjusted_timestamp, None, None, solar_irradiance, wind_speed, 'openweather')

                    # Insert into database
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO sensor_data (timestamp, temperature, humidity, irradiance, wind_speed, source)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (timestamp) DO NOTHING
                        """, db_data)

                    collected_count += 1
                    print(f"Collected row {collected_count}/50: {adjusted_timestamp} - Wind: {wind_speed} m/s, Irradiance: {solar_irradiance} W/m²")

                    # Move to next timestamp (every 30 minutes for distribution across the date range)
                    current_timestamp += timedelta(minutes=30)

                    # If we exceed Jan 30, reset to Jan 25 with next hour
                    if current_timestamp.date() > datetime(2026, 1, 30).date():
                        current_timestamp = start_date.replace(hour=(collected_count % 24))

                else:
                    print(f"Failed to fetch weather data for row {collected_count + 1}")

            except Exception as e:
                print(f"Error collecting data for row {collected_count + 1}: {e}")

            # Rate limiting - wait 2 seconds between API calls
            time.sleep(2)

        # Commit all changes
        conn.commit()
        print(f"\nSuccessfully collected and saved {collected_count} OpenWeather data rows to database")

        # Show summary
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = 'openweather'")
            final_count = cur.fetchone()[0]
            print(f"Total OpenWeather rows in database: {final_count}")

    except Exception as e:
        print(f"Error during data collection: {e}")
        conn.rollback()

    finally:
        conn.close()

if __name__ == "__main__":
    collect_openweather_data()
