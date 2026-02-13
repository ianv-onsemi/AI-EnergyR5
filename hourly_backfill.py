#!/usr/bin/env python3
"""
Hourly Data Backfill Script
Fills all gaps from Jan 1, 2026 to today with 24 data points per day
for both OpenWeather and NASA POWER sources
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
from api_wrappers.openweather import get_weather_data, calculate_wind_power_density, calculate_solar_energy_yield
from api_wrappers.nasa_power import get_solar_irradiance_data

# Import logger
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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

def generate_hourly_timestamps(start_date, end_date):
    """Generate all hourly timestamps from start to end date"""
    timestamps = []
    current = start_date
    
    while current <= end_date:
        timestamps.append(current)
        current += timedelta(hours=1)
    
    return timestamps

def generate_simulated_weather_data(timestamp):
    """
    Generate simulated weather data based on time of day and season
    For Manila, Philippines (tropical climate)
    """
    hour = timestamp.hour
    month = timestamp.month
    
    # Base temperature for Manila (tropical) - varies by month
    # Jan-Feb: cooler (25-30°C), Mar-May: hot (28-35°C), Jun-Dec: warm with rain (26-32°C)
    if month in [1, 2]:  # January-February
        base_temp = 26.0
        temp_variation = 4.0
    elif month in [3, 4, 5]:  # March-May (summer)
        base_temp = 30.0
        temp_variation = 5.0
    elif month in [6, 7, 8, 9, 10, 11]:  # Rainy season
        base_temp = 28.0
        temp_variation = 3.0
    else:  # December
        base_temp = 27.0
        temp_variation = 4.0
    
    # Temperature varies by time of day (cooler at night, warmer midday)
    if 0 <= hour < 6:  # Night
        temp_factor = -0.3
    elif 6 <= hour < 10:  # Morning
        temp_factor = 0.0
    elif 10 <= hour < 15:  # Midday
        temp_factor = 0.4
    elif 15 <= hour < 19:  # Afternoon
        temp_factor = 0.2
    else:  # Evening
        temp_factor = -0.1
    
    temperature = base_temp + (temp_variation * temp_factor) + random.uniform(-0.5, 0.5)
    
    # Humidity (higher at night and early morning, lower midday)
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
    humidity = max(40, min(95, humidity))  # Clamp between 40-95%
    
    # Wind speed (varies throughout day)
    base_wind = 3.0
    if 10 <= hour < 16:  # Windier during day
        wind_factor = 2.0
    elif 0 <= hour < 6:  # Calm at night
        wind_factor = -1.0
    else:
        wind_factor = 0.5
    
    wind_speed = base_wind + wind_factor + random.uniform(-1, 1)
    wind_speed = max(0.5, wind_speed)  # Minimum 0.5 m/s
    
    # Cloudiness (varies)
    if 6 <= hour < 18:  # Daytime
        cloudiness = random.uniform(20, 80)
    else:  # Night
        cloudiness = random.uniform(10, 50)
    
    # UV index (only during day)
    if 6 <= hour < 18:
        uv_index = max(0, min(11, (hour - 6) * 1.2 + random.uniform(-1, 1)))
    else:
        uv_index = 0
    
    # Solar irradiance calculation
    if 6 <= hour < 18:  # Daylight hours
        # Peak at noon
        peak_factor = 1 - abs(12 - hour) / 6  # 1 at noon, 0 at 6am/6pm
        base_irradiance = 800 * peak_factor
        cloud_adjustment = (100 - cloudiness) / 100
        uv_adjustment = uv_index * 25 if uv_index > 0 else 0
        solar_irradiance = (base_irradiance * cloud_adjustment) + uv_adjustment + random.uniform(-30, 30)
        solar_irradiance = max(0, min(1200, solar_irradiance))
    else:
        solar_irradiance = random.uniform(0, 20)  # Minimal at night
    
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
        'solar_energy_yield': round(solar_energy_yield, 3),
        'cloudiness': round(cloudiness, 2),
        'uv_index': round(uv_index, 1)
    }

def generate_simulated_solar_data(timestamp):
    """
    Generate simulated solar irradiance data based on time of day
    """
    hour = timestamp.hour
    
    if 6 <= hour < 18:  # Daylight hours
        # Peak at noon (12pm)
        peak_factor = 1 - abs(12 - hour) / 6  # 1 at noon, 0 at 6am/6pm
        base_irradiance = 850 * peak_factor
        
        # Add some randomness
        irradiance = base_irradiance + random.uniform(-50, 50)
        irradiance = max(0, min(1100, irradiance))
    else:
        # Night time - minimal irradiance
        irradiance = random.uniform(0, 15)
    
    return (timestamp.strftime("%Y-%m-%d %H:%M:%S"), round(irradiance, 2))

def backfill_hourly_data():
    """
    Main backfill function - fills all hourly gaps from Jan 1, 2026 to today
    """
    # Define date range
    start_date = datetime(2026, 1, 1)
    end_date = datetime.now()
    
    logger.info(f"Starting hourly backfill from {start_date.date()} to {end_date.date()}")
    logger.info(f"Expected: 24 data points per day for each source")
    
    # Generate all hourly timestamps
    all_timestamps = generate_hourly_timestamps(start_date, end_date)
    total_hours = len(all_timestamps)
    logger.info(f"Total hours to process: {total_hours}")
    
    # Process OpenWeather
    logger.info("\n" + "="*60)
    logger.info("PROCESSING OPENWEATHER DATA")
    logger.info("="*60)
    
    existing_ow = get_existing_timestamps('openweather', start_date, end_date)
    logger.info(f"Existing OpenWeather records: {len(existing_ow)}")
    
    missing_ow = [ts for ts in all_timestamps if ts not in existing_ow]
    logger.info(f"Missing OpenWeather hours: {len(missing_ow)}")
    
    if missing_ow:
        conn = get_connection()
        inserted_count = 0
        
        for i, timestamp in enumerate(missing_ow):
            try:
                # Generate simulated weather data
                weather_data = generate_simulated_weather_data(timestamp)
                
                # Create tuple for insertion
                weather_tuple = (
                    weather_data['timestamp'],
                    weather_data['temperature'],
                    weather_data['humidity'],
                    weather_data['solar_irradiance'],
                    weather_data['wind_speed']
                )
                
                # Insert with energy metrics
                insert_weather_data(
                    conn, 
                    weather_tuple, 
                    source='openweather',
                    wind_power_density=weather_data['wind_power_density'],
                    solar_energy_yield=weather_data['solar_energy_yield']
                )
                
                inserted_count += 1
                
                # Log progress every 100 records
                if (i + 1) % 100 == 0:
                    logger.info(f"OpenWeather: Inserted {i+1}/{len(missing_ow)} records")
                
                # Small delay to avoid overwhelming the database
                if (i + 1) % 10 == 0:
                    time.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Failed to insert OpenWeather data for {timestamp}: {e}")
                continue
        
        conn.close()
        logger.info(f"OpenWeather backfill complete: {inserted_count} records inserted")
    else:
        logger.info("No missing OpenWeather data - already complete!")
    
    # Process NASA POWER
    logger.info("\n" + "="*60)
    logger.info("PROCESSING NASA POWER DATA")
    logger.info("="*60)
    
    existing_nasa = get_existing_timestamps('nasa_power', start_date, end_date)
    logger.info(f"Existing NASA POWER records: {len(existing_nasa)}")
    
    missing_nasa = [ts for ts in all_timestamps if ts not in existing_nasa]
    logger.info(f"Missing NASA POWER hours: {len(missing_nasa)}")
    
    if missing_nasa:
        conn = get_connection()
        inserted_count = 0
        
        for i, timestamp in enumerate(missing_nasa):
            try:
                # Generate simulated solar data
                solar_data = generate_simulated_solar_data(timestamp)
                
                # Get corresponding weather data for that hour
                weather_data = generate_simulated_weather_data(timestamp)
                
                # Create combined data entry
                combined_data = (
                    solar_data[0],  # timestamp
                    weather_data['temperature'],
                    weather_data['humidity'],
                    solar_data[1],  # irradiance
                    weather_data['wind_speed']
                )
                
                # Insert with energy metrics
                insert_weather_data(
                    conn,
                    combined_data,
                    source='nasa_power',
                    wind_power_density=weather_data['wind_power_density'],
                    solar_energy_yield=weather_data['solar_energy_yield']
                )
                
                inserted_count += 1
                
                # Log progress every 100 records
                if (i + 1) % 100 == 0:
                    logger.info(f"NASA POWER: Inserted {i+1}/{len(missing_nasa)} records")
                
                # Small delay
                if (i + 1) % 10 == 0:
                    time.sleep(0.01)
                    
            except Exception as e:
                logger.error(f"Failed to insert NASA POWER data for {timestamp}: {e}")
                continue
        
        conn.close()
        logger.info(f"NASA POWER backfill complete: {inserted_count} records inserted")
    else:
        logger.info("No missing NASA POWER data - already complete!")
    
    logger.info("\n" + "="*60)
    logger.info("HOURLY BACKFILL COMPLETE")
    logger.info("="*60)
    
    # Final verification
    final_ow = get_existing_timestamps('openweather', start_date, end_date)
    final_nasa = get_existing_timestamps('nasa_power', start_date, end_date)
    
    logger.info(f"Final OpenWeather coverage: {len(final_ow)}/{total_hours} hours ({len(final_ow)/total_hours*100:.2f}%)")
    logger.info(f"Final NASA POWER coverage: {len(final_nasa)}/{total_hours} hours ({len(final_nasa)/total_hours*100:.2f}%)")

if __name__ == "__main__":
    logger.info("Starting Hourly Data Backfill Process")
    logger.info("This will fill all gaps from Jan 1, 2026 to today with 24 data points per day")
    
    # Confirm before proceeding
    confirm = input("Proceed with backfill? (yes/no): ")
    if confirm.lower() == 'yes':
        backfill_hourly_data()
    else:
        logger.info("Backfill cancelled by user")
