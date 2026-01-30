import random
from datetime import datetime, timedelta
from db.db_connector import get_connection
from db.db_ingest import insert_sensor_data

def generate_past_data(hours=50):
    """Generate sensor data for the past 'hours' hours, 1 per hour, and insert into database."""
    conn = get_connection()
    current_time = datetime.now()

    for i in range(hours):
        # Calculate timestamp for i hours ago
        timestamp = (current_time - timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S")

        # Generate fake sensor values
        temperature = round(random.uniform(20, 30), 2)   # Celsius
        humidity = round(random.uniform(40, 70), 2)      # %
        irradiance = round(random.uniform(200, 800), 2)  # W/m²
        wind_speed = round(random.uniform(0, 10), 2)     # m/s

        # Insert into database
        insert_sensor_data(conn, timestamp, temperature, humidity, irradiance, wind_speed, source="sim")
        print(f"Inserted data for {timestamp}")

    conn.close()
    print(f"Generated and inserted {hours} rows of sim data.")

if __name__ == "__main__":
    generate_past_data(50)
