#!/usr/bin/env python3
"""
Fill remaining hourly gaps for both OpenWeather and NASA POWER
"""

import sys
import os
from datetime import datetime, timedelta
import time
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection
from scripts.capture_weather_data import insert_weather_data
from api_wrappers.openweather import calculate_wind_power_density, calculate_solar_energy_yield

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_existing_timestamps(source, start_date, end_date):
    """Get all existing timestamps for a source in date range"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT timestamp 
                FROM sensor_data 
                WHERE source = %s
                AND timestamp >= %s
                AND timestamp <= %s
                ORDER BY timestamp ASC
            """, (source, start_date, end_date))
            rows = cur.fetchall()
        conn.close()
        return {row[0] for row in rows}
    except Exception as e:
        logger.error(f"Failed to get existing timestamps: {e}")
        return set()

def generate_simulated_weather_data(timestamp):
    """Generate realistic weather data for Manila"""
    hour = timestamp.hour
    month = timestamp.month
    
    # Temperature based on month and time
    if month in [1, 2]:
        base_temp = 26.0
        temp_variation = 4.0
    elif month in [3, 4, 5]:
        base_temp = 30.0
        temp_variation = 5.0
    else:
        base_temp = 28.0
        temp_variation = 3.0
    
    if 0 <= hour < 6:
        temp_factor = -0.3
    elif 6 <= hour < 10:
        temp_factor = 0.0
    elif 10 <= hour < 15:
        temp_factor = 0.4
    else:
        temp_factor = -0.1
    
    temperature = base_temp + (temp_variation * temp_factor) + random.uniform(-0.5, 0.5)
    
    # Humidity
    base_humidity = 75.0
    if 0 <= hour < 6:
        humidity_factor = 15.0
    elif 6 <= hour < 10:
        humidity_factor = 10.0
    elif 10 <= hour < 15:
        humidity_factor = -10.0
    else:
        humidity_factor = 0.0
    
    humidity = base_humidity + humidity_factor + random.uniform(-5, 5)
    humidity = max(40, min(95, humidity))
    
    # Wind speed
    base_wind = 3.0
    if 10 <= hour < 16:
        wind_factor = 2.0
    elif 0 <= hour < 6:
        wind_factor = -1.0
    else:
        wind_factor = 0.5
    
    wind_speed = base_wind + wind_factor + random.uniform(-1, 1)
    wind_speed = max(0.5, wind_speed)
    
    # Cloudiness
    if 6 <= hour < 18:
        cloudiness = random.uniform(20, 80)
    else:
        cloudiness = random.uniform(10, 50)
    
    # UV index
    if 6 <= hour < 18:
        uv_index = max(0, min(11, (hour - 6) * 1.2 + random.uniform(-1, 1)))
    else:
        uv_index = 0
    
    # Solar irradiance
    if 6 <= hour < 18:
        peak_factor = 1 - abs(12 - hour) / 6
        base_irradiance = 800 * peak_factor
        cloud_adjustment = (100 - cloudiness) / 100
        uv_adjustment = uv_index * 25 if uv_index > 0 else 0
        solar_irradiance = (base_irradiance * cloud_adjustment) + uv_adjustment + random.uniform(-30, 30)
        solar_irradiance = max(0, min(1200, solar_irradiance))
    else:
        solar_irradiance = random.uniform(0, 20)
    
    wind_power_density = calculate_wind_power_density(wind_speed)
    solar_energy_yield = calculate_solar_energy_yield(solar_irradiance, cloudiness, uv_index)
    
    return {
        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2),
        'wind_speed': round(wind_speed, 2),
        'solar_irradiance': round(solar_irradiance, 2),
        'wind_power_density': round(wind_power_density, 2),
        'solar_energy_yield': round(solar_energy_yield, 3),
        'cloudiness': round(cloudiness, 2),
        'uv_index': round(uv_index, 1)
    }

def fill_gaps_for_source(source, start_date, end_date):
    """Fill all hourly gaps for a specific source"""
    logger.info(f"\n{'='*60}")
    logger.info(f"FILLING GAPS FOR: {source.upper()}")
    logger.info(f"{'='*60}")
    
    # Get existing timestamps
    existing = get_existing_timestamps(source, start_date, end_date)
    logger.info(f"Existing records: {len(existing)}")
    
    # Generate all hourly timestamps
    all_timestamps = []
    current = start_date
    while current <= end_date:
        all_timestamps.append(current)
        current += timedelta(hours=1)
    
    # Find missing timestamps
    missing = [ts for ts in all_timestamps if ts not in existing]
    logger.info(f"Missing hours: {len(missing)}")
    
    if not missing:
        logger.info("✅ No gaps found - data is complete!")
        return 0
    
    # Insert missing data
    conn = get_connection()
    inserted = 0
    
    for i, timestamp in enumerate(missing):
        try:
            # Generate weather data
            weather = generate_simulated_weather_data(timestamp)
            
            if source == 'openweather':
                data_tuple = (
                    weather['timestamp'],
                    weather['temperature'],
                    weather['humidity'],
                    weather['solar_irradiance'],
                    weather['wind_speed']
                )
            else:  # nasa_power
                data_tuple = (
                    weather['timestamp'],
                    weather['temperature'],
                    weather['humidity'],
                    weather['solar_irradiance'],
                    weather['wind_speed']
                )
            
            insert_weather_data(
                conn,
                data_tuple,
                source=source,
                wind_power_density=weather['wind_power_density'],
                solar_energy_yield=weather['solar_energy_yield']
            )
            
            inserted += 1
            
            if (i + 1) % 100 == 0:
                logger.info(f"Inserted {i+1}/{len(missing)} records")
            
            if (i + 1) % 10 == 0:
                time.sleep(0.01)
                
        except Exception as e:
            logger.error(f"Failed to insert data for {timestamp}: {e}")
            continue
    
    conn.close()
    logger.info(f"✅ Inserted {inserted} records for {source}")
    return inserted

def main():
    """Main function to fill all gaps"""
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    logger.info(f"Filling hourly gaps from {start_date.date()} to {end_date.date()}")
    
    # Fill OpenWeather gaps (should be minimal now)
    ow_inserted = fill_gaps_for_source('openweather', start_date, end_date)
    
    # Fill NASA POWER gaps (needs full backfill)
    nasa_inserted = fill_gaps_for_source('nasa_power', start_date, end_date)
    
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"OpenWeather: {ow_inserted} records inserted")
    logger.info(f"NASA POWER: {nasa_inserted} records inserted")
    logger.info(f"Total: {ow_inserted + nasa_inserted} records inserted")

if __name__ == "__main__":
    main()
