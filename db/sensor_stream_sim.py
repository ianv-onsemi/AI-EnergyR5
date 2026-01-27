import time
from datetime import datetime
import random
import os

# File where simulated sensor data will be appended
log_file = "data/sensor_logs.txt"

def generate_sensor_data():
    """
    Generate a single row of simulated sensor data and append to log file.
    Returns the generated data as a tuple.
    """
    # Generate fake sensor values
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temperature = round(random.uniform(20, 30), 2)   # Celsius
    humidity = round(random.uniform(40, 70), 2)      # %
    irradiance = round(random.uniform(200, 800), 2)  # W/m²
    wind_speed = round(random.uniform(0, 10), 2)     # m/s

    # Format row
    row = f"{timestamp},{temperature},{humidity},{irradiance},{wind_speed}\n"

    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Append to log file
    with open(log_file, "a") as f:
        f.write(row)

    print(f"Generated sensor data: {row.strip()}")
    return (timestamp, temperature, humidity, irradiance, wind_speed)

# Legacy continuous mode (for backward compatibility)
if __name__ == "__main__":
    row_count = 0
    max_rows = 10
    while row_count < max_rows:
        generate_sensor_data()
        row_count += 1
        # Wait 100ms before next reading
        time.sleep(0.1)
    print(f"Simulation complete: Generated {max_rows} rows")
