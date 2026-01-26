import time
import random

# Function to simulate sensor readings
def get_sensor_data():
    return {
        "temperature": round(random.uniform(25, 40), 2),   # °C
        "humidity": round(random.uniform(40, 90), 2),      # %
        "irradiance": round(random.uniform(200, 1200), 2), # W/m^2
        "wind_speed": round(random.uniform(0, 15), 2)      # m/s
    }

if __name__ == "__main__":
    # Open (or create) a log file in append mode
    with open("sensor_logs.txt", "a") as f:
        for i in range(10):  # collect 10 samples
            data = get_sensor_data()
            log_line = (
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}, "
                f"{data['temperature']}, {data['humidity']}, "
                f"{data['irradiance']}, {data['wind_speed']}\n"
            )
            
            # Save to file
            f.write(log_line)
            
            # Show on screen
            print("Saved:", log_line.strip())
            
            # Wait 5 seconds before next reading
            time.sleep(5)

