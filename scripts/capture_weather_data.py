import requests
import psycopg2
import logging
from datetime import datetime
import time
import os

# ----------------------------
# Logging setup
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ----------------------------
# OpenWeather API setup
# ----------------------------
API_KEY = os.getenv("OPENWEATHER_API_KEY", "0723d71a05e58ae3f7fc91e39a901e6b")   # Use env var or fallback
CITY = os.getenv("WEATHER_CITY", "Manila")                 # Use env var or fallback
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

def fetch_weather_data():
    """
    Fetch current weather data from OpenWeather API.
    Returns tuple: (timestamp, temperature, humidity, irradiance_placeholder, wind_speed)
    """
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        data = response.json()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        irradiance = 0.0  # placeholder, OpenWeather doesn't provide irradiance

        logger.info(f"Weather data fetched: {timestamp}, {temperature}°C, {humidity}%, {wind_speed} m/s")
        return (timestamp, temperature, humidity, irradiance, wind_speed)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch weather data: {e}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected API response format: {e}")
        return None

def insert_weather_data(conn, weather_data, source=None, wind_power_density=None, solar_energy_yield=None):
    """
    Insert weather data tuple into sensor_data table.
    """
    try:
        timestamp, temperature, humidity, irradiance, wind_speed = weather_data
        with conn.cursor() as cur:
            if source:
                cur.execute(
                    """
                    INSERT INTO sensor_data (timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp) DO NOTHING;
                    """,
                    (timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO sensor_data (timestamp, temperature, humidity, irradiance, wind_speed, wind_power_density, solar_energy_yield)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (timestamp) DO NOTHING;
                    """,
                    (timestamp, temperature, humidity, irradiance, wind_speed, wind_power_density, solar_energy_yield)
                )
        conn.commit()
        logger.info("Weather data inserted successfully.")
    except Exception as e:
        logger.error(f"Insert failed: {e}")
        raise



# Legacy batch mode (for backward compatibility)
if __name__ == "__main__":
    # Database connection
    conn = psycopg2.connect(
        dbname="energy_db",
        user="postgres",
        password="PdM",   # <-- replace with your DB password
        host="localhost",
        port="5432"
    )

    # ----------------------------
    # Fetch and insert 20 rows of weather data
    # ----------------------------
    for i in range(20):
        weather_data = fetch_weather_data()
        if weather_data:
            try:
                insert_weather_data(conn, weather_data)
            except Exception as e:
                logger.error(f"Failed to insert weather data {i+1}: {e}")
        else:
            logger.error(f"Failed to fetch weather data {i+1}")

        # Wait 1 second between requests to avoid rate limiting
        time.sleep(1)

    conn.close()
