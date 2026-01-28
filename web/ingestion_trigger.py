import subprocess
import sys
import os
import logging
from datetime import datetime

# Import our ingestion functions
from db.db_ingest import run_ingestion
from db.sensor_stream_sim import generate_sensor_data
from capture_weather_data import fetch_weather_data

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)
=======
from flask import Flask, jsonify, request
import subprocess
import sys
import os
import logging
from datetime import datetime
import time
import requests

# Import our ingestion functions
from db.db_ingest import run_ingestion
from db.sensor_stream_sim import generate_sensor_data
from capture_weather_data import fetch_weather_data, insert_weather_data
from api_wrappers.nasa_power import get_solar_irradiance_data

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry a function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)

@app.route('/trigger_ingestion', methods=['POST'])
def trigger_ingestion():
    """Endpoint to trigger manual data ingestion"""
    try:
        logger.info("Manual ingestion triggered")

        # Generate simulated sensor data
        sensor_generated = False
        try:
            sensor_data = generate_sensor_data()
            sensor_generated = True
            logger.info("Sensor data generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate sensor data: {e}")

        # Fetch weather data from OpenWeather API (10 rows from past 2 days)
        weather_fetched = False
        weather_data_list = []
        try:
            # Fetch 10 weather data points from past 2 days
            for i in range(10):
                weather_data = fetch_weather_data()
                if weather_data:
                    weather_data_list.append(weather_data)
                    weather_fetched = True
                    logger.info(f"Weather data {i+1} fetched successfully")
                    time.sleep(1)  # Rate limiting
                else:
                    logger.warning(f"Weather data {i+1} fetch returned None")
            logger.info(f"Total weather data points fetched: {len(weather_data_list)}")
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")

        # Fetch solar irradiance data from NASA POWER API (10 rows from past 2 days)
        solar_fetched = False
        solar_data_list = []
        try:
            # Fetch 10 solar irradiance data points from past 2 days
            for i in range(10):
                solar_data = get_solar_irradiance_data()
                if solar_data:
                    solar_data_list.append(solar_data)
                    solar_fetched = True
                    logger.info(f"Solar irradiance data {i+1} fetched successfully")
                    time.sleep(0.5)  # Rate limiting
                else:
                    logger.warning(f"Solar irradiance data {i+1} fetch returned None")
            logger.info(f"Total solar irradiance data points fetched: {len(solar_data_list)}")
        except Exception as e:
            logger.error(f"Failed to fetch solar irradiance data: {e}")

        # Run database ingestion
        ingestion_result = None
        try:
            ingestion_result = run_ingestion()
            logger.info("Database ingestion completed")
        except Exception as e:
            logger.error(f"Database ingestion failed: {e}")
            return jsonify({
                'success': False,
                'error': f'Database ingestion failed: {str(e)}',
                'sensor_generated': sensor_generated,
                'weather_fetched': weather_fetched,
                'solar_fetched': solar_fetched
            }), 500

        # Insert weather data if fetched (all 10 rows)
        weather_rows_inserted = 0
        if weather_fetched and weather_data_list:
            try:
                from db_connector import get_connection
                conn = get_connection()
                for weather_data in weather_data_list:
                    insert_weather_data(conn, weather_data)
                    weather_rows_inserted += 1
                conn.close()
                logger.info(f"Weather data inserted into database: {weather_rows_inserted} rows")
            except Exception as e:
                logger.error(f"Failed to insert weather data: {e}")

        # Insert solar data if fetched (all 10 rows, merge with weather data where possible)
        solar_rows_inserted = 0
        if solar_fetched and solar_data_list:
            try:
                from db_connector import get_connection
                conn = get_connection()
                for i, solar_data in enumerate(solar_data_list):
                    # Create a combined entry with solar irradiance
                    timestamp, irradiance = solar_data
                    # Try to use corresponding weather data if available
                    if i < len(weather_data_list):
                        ts, temp, hum, _, wind = weather_data_list[i]
                        combined_data = (ts, temp, hum, irradiance, wind)
                    else:
                        # Create minimal entry with just timestamp and irradiance
                        combined_data = (timestamp, 0.0, 0.0, irradiance, 0.0)

                    insert_weather_data(conn, combined_data)
                    solar_rows_inserted += 1
                conn.close()
                logger.info(f"Solar irradiance data inserted into database: {solar_rows_inserted} rows")
            except Exception as e:
                logger.error(f"Failed to insert solar irradiance data: {e}")

        return jsonify({
            'success': True,
            'sensor_generated': sensor_generated,
            'weather_fetched': weather_fetched,
            'weather_rows_inserted': weather_rows_inserted,
            'solar_fetched': solar_fetched,
            'solar_rows_inserted': solar_rows_inserted,
            'ingestion_result': ingestion_result or {}
        })

    except Exception as e:
        logger.error(f"Ingestion trigger failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'sensor_generated': False,
            'weather_fetched': False,
            'solar_fetched': False
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
