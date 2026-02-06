import requests
import psycopg2
import logging
from datetime import datetime

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ----------------------------
# Database connection
# ----------------------------
conn = psycopg2.connect(
    dbname="energy_db",
    user="postgres",
    password="PdM",   # <-- replace with your DB password
    host="localhost",
    port="5432"
)

# ----------------------------
# OpenWeather API setup
# ----------------------------
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from api_wrappers.openweather import get_weather_data

# ----------------------------
# Fetch enhanced weather data with energy calculations
# ----------------------------
weather_data = get_weather_data()

if weather_data:
    timestamp = weather_data["timestamp"]
    temperature = weather_data["temperature"]
    humidity = weather_data["humidity"]
    wind_speed = weather_data["wind_speed"]
    irradiance = weather_data["solar_irradiance"]
    wind_power_density = weather_data["wind_power_density"]
    solar_energy_yield = weather_data["solar_energy_yield"]

    logging.info(f"Enhanced weather data: {timestamp}")
    logging.info(f"Temperature: {temperature}°C, Humidity: {humidity}%, Wind Speed: {wind_speed} m/s")
    logging.info(f"Solar Irradiance: {irradiance} W/m², Wind Power Density: {wind_power_density} W/m²")
    logging.info(f"Solar Energy Yield: {solar_energy_yield} kWh/m²/day")

    # Insert into sensor_data table with new energy fields
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sensor_data (timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING;
                """,
                (timestamp, temperature, humidity, irradiance, wind_speed, "openweather", wind_power_density, solar_energy_yield)
            )
        conn.commit()
        logging.info("Enhanced weather data inserted successfully.")
    except Exception as e:
        logging.error(f"Insert failed: {e}")
        logging.error(f"Data attempted: {weather_data}")

else:
    logging.error("Failed to fetch weather data from OpenWeather API")

conn.close()
