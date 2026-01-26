import time
from datetime import datetime
import random

# File where simulated sensor data will be appended
log_file = "data/sensor_logs.txt"

while True:
    # Generate fake sensor values
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temperature = round(random.uniform(20, 30), 2)   # Celsius
    humidity = round(random.uniform(40, 70), 2)      # %
    irradiance = round(random.uniform(200, 800), 2)  # W/m²
    wind_speed = round(random.uniform(0, 10), 2)     # m/s

    # Format row
    row = f"{timestamp},{temperature},{humidity},{irradiance},{wind_speed}\n"

    # Append to log file
    with open(log_file, "a") as f:
        f.write(row)

    print(f"Added row: {row.strip()}")

    # Wait 60 seconds before next reading
    #time.sleep(5)  #5sec
    #time.sleep(60) #1min
    time.sleep(300) #5min
