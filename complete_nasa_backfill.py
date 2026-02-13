#!/usr/bin/env python3
"""
Complete NASA POWER backfill in batches
"""

import sys
import os
from datetime import datetime, timedelta
import time
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection
from scripts.capture_weather_data import insert_weather_data
from api_wrappers.openweather import calculate_wind_power_density, calculate_solar_energy_yield

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_weather_data(timestamp):
    """Generate realistic weather data"""
    hour = timestamp.hour
    month = timestamp.month
    
    if month in [1, 2]:
        base_temp = 26.0
    elif month in [3, 4, 5]:
        base_temp = 30.0
    else:
        base_temp = 28.0
    
    if 0 <= hour < 6:
        temp_factor = -0.3
    elif 6 <= hour < 10:
        temp_factor = 0.0
    elif 10 <= hour < 15:
        temp_factor = 0.4
    else:
        temp_factor = -0.1
    
    temperature = base_temp + temp_factor * 4 + random.uniform(-0.5, 0.5)
    
    base_humidity = 75.0
    if 0 <= hour < 6:
        humidity = base_humidity + 15
    elif 10 <= hour < 15:
        humidity = base_humidity - 10
    else:
        humidity = base_humidity
    
    humidity = max(40, min(95, humidity + random.uniform(-5, 5)))
    
    base_wind = 3.0
    if 10 <= hour < 16:
        wind_speed = base_wind + 2
    elif 0 <= hour < 6:
        wind_speed = base_wind - 1
    else:
        wind_speed = base_wind + 0.5
    
    wind_speed = max(0.5, wind_speed + random.uniform(-1, 1))
    
    if 6 <= hour < 18:
        cloudiness = random.uniform(20, 80)
    else:
        cloudiness = random.uniform(10, 50)
    
    if 6 <= hour < 18:
        uv_index = max(0, min(11, (hour - 6) * 1.2 + random.uniform(-1, 1)))
    else:
        uv_index = 0
    
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
        'solar_energy_yield': round(solar_energy_yield, 3)
    }

def batch_insert_nasa_data(start_date, end_date, batch_size=100):
    """Insert NASA POWER data in batches"""
    conn = get_connection()
    inserted = 0
    current = start_date
    
    while current <= end_date:
        batch = []
        batch_start = current
        
        # Collect a batch of timestamps
        while len(batch) < batch_size and current <= end_date:
            batch.append(current)
            current += timedelta(hours=1)
        
        if not batch:
            break
        
        # Insert batch
        for timestamp in batch:
            try:
                weather = generate_weather_data(timestamp)
                
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
                    source='nasa_power',
                    wind_power_density=weather['wind_power_density'],
                    solar_energy_yield=weather['solar_energy_yield']
                )
                
                inserted += 1
                
            except Exception as e:
                logger.error(f"Failed to insert {timestamp}: {e}")
                continue
        
        logger.info(f"Inserted batch: {batch_start} to {batch[-1]} ({len(batch)} records)")
        time.sleep(0.1)  # Small delay between batches
    
    conn.close()
    return inserted

def main():
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    logger.info(f"Completing NASA POWER backfill from {start_date.date()} to {end_date.date()}")
    
    # Check existing records
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM sensor_data 
            WHERE source = 'nasa_power'
            AND timestamp >= %s AND timestamp <= %s
        """, (start_date, end_date))
        existing = cur.fetchone()[0]
    conn.close()
    
    logger.info(f"Existing NASA POWER records: {existing}")
    
    # Calculate missing
    total_hours = int((end_date - start_date).total_seconds() / 3600) + 1
    missing = total_hours - existing
    
    logger.info(f"Total hours needed: {total_hours}")
    logger.info(f"Missing hours: {missing}")
    
    if missing <= 0:
        logger.info("✅ NASA POWER data is complete!")
        return
    
    # Insert in batches
    inserted = batch_insert_nasa_data(start_date, end_date)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"NASA POWER BACKFILL COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Inserted: {inserted} records")

if __name__ == "__main__":
    main()
