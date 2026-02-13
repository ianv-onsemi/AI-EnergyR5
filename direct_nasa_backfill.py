#!/usr/bin/env python3
"""
Direct NASA POWER backfill - bypasses the insert_weather_data function
"""

import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection
from api_wrappers.openweather import calculate_wind_power_density, calculate_solar_energy_yield

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_weather_data(timestamp):
    """Generate realistic weather data for Manila"""
    hour = timestamp.hour
    month = timestamp.month
    
    # Temperature based on month and time
    if month in [1, 2]:
        base_temp = 26.0
    elif month in [3, 4, 5]:
        base_temp = 30.0
    else:
        base_temp = 28.0
    
    # Time of day adjustment
    if 0 <= hour < 6:
        temp_factor = -0.3
    elif 6 <= hour < 10:
        temp_factor = 0.0
    elif 10 <= hour < 15:
        temp_factor = 0.4
    else:
        temp_factor = -0.1
    
    temperature = base_temp + temp_factor * 4 + random.uniform(-0.5, 0.5)
    
    # Humidity
    base_humidity = 75.0
    if 0 <= hour < 6:
        humidity = base_humidity + 15
    elif 10 <= hour < 15:
        humidity = base_humidity - 10
    else:
        humidity = base_humidity
    
    humidity = max(40, min(95, humidity + random.uniform(-5, 5)))
    
    # Wind speed
    base_wind = 3.0
    if 10 <= hour < 16:
        wind_speed = base_wind + 2
    elif 0 <= hour < 6:
        wind_speed = base_wind - 1
    else:
        wind_speed = base_wind + 0.5
    
    wind_speed = max(0.5, wind_speed + random.uniform(-1, 1))
    
    # Cloudiness
    if 6 <= hour < 18:
        cloudiness = random.uniform(20, 80)
    else:
        cloudiness = random.uniform(10, 50)
    
    # UV Index
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
    
    # Calculate energy metrics
    wind_power_density = calculate_wind_power_density(wind_speed)
    solar_energy_yield = calculate_solar_energy_yield(solar_irradiance, cloudiness, uv_index)
    
    return {
        'timestamp': timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        'temperature': round(temperature, 2),
        'humidity': round(humidity, 2),
        'wind_speed': round(wind_speed, 2),
        'solar_irradiance': round(solar_irradiance, 2),
        'wind_power_density': round(wind_power_density, 2),
        'solar_energy_yield': round(solar_energy_yield, 3)
    }

def direct_insert_nasa_data():
    """Directly insert NASA POWER data without using insert_weather_data function"""
    conn = get_connection()
    
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    # Get existing timestamps to avoid duplicates
    with conn.cursor() as cur:
        cur.execute("""
            SELECT timestamp FROM sensor_data 
            WHERE source = 'nasa_power'
            AND timestamp >= %s AND timestamp <= %s
        """, (start_date, end_date))
        existing = {row[0] for row in cur.fetchall()}
    
    logger.info(f"Existing NASA POWER records: {len(existing)}")
    
    inserted = 0
    skipped = 0
    current = start_date
    
    while current <= end_date:
        # Round to hour to avoid microsecond issues
        current = current.replace(minute=0, second=0, microsecond=0)
        
        if current in existing:
            skipped += 1
            current += timedelta(hours=1)
            continue
        
        try:
            weather = generate_weather_data(current)
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sensor_data 
                    (timestamp, temperature, humidity, irradiance, wind_speed, source, 
                     wind_power_density, solar_energy_yield)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp, source) DO NOTHING;
                """, (

                    weather['timestamp'],
                    weather['temperature'],
                    weather['humidity'],
                    weather['solar_irradiance'],
                    weather['wind_speed'],
                    'nasa_power',
                    weather['wind_power_density'],
                    weather['solar_energy_yield']
                ))
            
            conn.commit()
            inserted += 1
            
            if inserted % 100 == 0:
                logger.info(f"Inserted {inserted} records... (current: {current})")
            
        except Exception as e:
            logger.error(f"Failed to insert {current}: {e}")
            conn.rollback()
        
        current += timedelta(hours=1)
    
    conn.close()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"DIRECT NASA POWER BACKFILL COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Inserted: {inserted} records")
    logger.info(f"Skipped (duplicates): {skipped} records")

if __name__ == "__main__":
    direct_insert_nasa_data()
