import time
import random
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.db_connector import get_connection
from db.db_ingest import insert_sensor_data

# Function to simulate sensor readings
def get_sensor_data():
    return {
        "temperature": round(random.uniform(25, 40), 2),   # °C
        "humidity": round(random.uniform(40, 90), 2),      # %
        "irradiance": round(random.uniform(200, 1200), 2), # W/m^2
        "wind_speed": round(random.uniform(0, 15), 2)      # m/s
    }

if __name__ == "__main__":
    # Get the most recent timestamp from the database
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp FROM sensor_data ORDER BY timestamp DESC LIMIT 1')
    result = cursor.fetchone()
    
    if result:
        start_time = result[0]
    else:
        start_time = datetime.now() - timedelta(hours=1)  # Default to 1 hour ago if no data
    
    current_time = start_time + timedelta(minutes=30)  # Start from next 30-minute interval
    
    # Generate 20 data points
    for i in range(20):
        data = get_sensor_data()
        timestamp_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert into database
        insert_sensor_data(conn, timestamp_str, data['temperature'], data['humidity'], data['irradiance'], data['wind_speed'], "sim")
        
        # Also save to file
        log_line = (
            f"{timestamp_str}, "
            f"{data['temperature']}, {data['humidity']}, "
            f"{data['irradiance']}, {data['wind_speed']}\n"
        )
        
        with open("data/sensor_logs.txt", "a") as f:
            f.write(log_line)
        
        # Show on screen
        print("Added to DB:", log_line.strip())
        
        # Increment by 30 minutes
        current_time += timedelta(minutes=30)
    
    conn.close()

