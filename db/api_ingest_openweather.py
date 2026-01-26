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
API_KEY = "0723d71a05e58ae3f7fc91e39a901e6b"   # <-- replace with your OpenWeather API key
CITY = "Manila"                 # <-- replace with your city
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# ----------------------------
# Fetch weather data
# ----------------------------
response = requests.get(URL)
data = response.json()

if response.status_code == 200:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temperature = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    irradiance = 0.0  # placeholder, OpenWeather doesn’t provide irradiance

    logging.info(f"Weather data: {timestamp}, {temperature}°C, {humidity}%, {wind_speed} m/s")

    # Insert into sensor_data table
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sensor_data (timestamp, temperature, humidity, irradiance, wind_speed)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (timestamp) DO NOTHING;
                """,
                (timestamp, temperature, humidity, irradiance, wind_speed)
            )
        conn.commit()
        logging.info("Weather data inserted successfully.")
    except Exception as e:
        logging.error(f"Insert failed: {e}")
else:
    logging.error(f"Failed to fetch data: {data}")

conn.close()
