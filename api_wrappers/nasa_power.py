import requests
from datetime import datetime, timedelta
import random

# NASA POWER API parameters
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
LATITUDE = 14.5995  # Manila latitude
LONGITUDE = 120.9842  # Manila longitude
PARAMETERS = "ALLSKY_SFC_SW_DWN"  # All-sky surface shortwave downward irradiance (W/m²)

def get_solar_irradiance_data():
    """
    Fetch daily solar irradiance data from NASA POWER API for Manila.
    Falls back to simulated data if API fails.
    """
    try:
        # Try multiple dates in case of missing data
        for days_back in range(1, 8):  # Try last 7 days
            target_date = datetime.now() - timedelta(days=days_back)
            start_date = target_date.strftime("%Y%m%d")
            end_date = start_date

            params = {
                "start": start_date,
                "end": end_date,
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "community": "RE",
                "parameters": PARAMETERS,
                "format": "JSON",
                "header": "true"
            }

            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract irradiance value
            irradiance = data["properties"]["parameter"][PARAMETERS][start_date]

            # Check if data is valid (not -999 or similar missing value indicators)
            if irradiance and irradiance > 0:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                return (timestamp, irradiance)

        # If all API calls fail or return invalid data, use simulated data
        print("NASA POWER API returned invalid data, using simulated irradiance")
        return get_simulated_irradiance()

    except Exception as e:
        print(f"Error fetching NASA POWER data: {e}, using simulated data")
        return get_simulated_irradiance()

def get_simulated_irradiance():
    """
    Generate simulated solar irradiance data for Manila.
    Based on typical tropical solar irradiance patterns.
    """
    # Simulate based on time of day (higher during midday)
    current_hour = datetime.now().hour

    # Base irradiance with time-of-day variation
    if 6 <= current_hour <= 18:  # Daylight hours
        base_irradiance = 800  # Peak around 800 W/m²
        # Add some variation based on hour
        hour_factor = 1 - abs(12 - current_hour) / 6  # Peak at noon
        irradiance = base_irradiance * hour_factor + random.uniform(-50, 50)
    else:
        irradiance = random.uniform(0, 50)  # Low irradiance at night

    irradiance = max(0, min(1200, irradiance))  # Clamp between 0-1200 W/m²

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (timestamp, round(irradiance, 2))

if __name__ == "__main__":
    data = get_solar_irradiance_data()
    if data:
        print(f"Timestamp: {data[0]}, Solar Irradiance: {data[1]} W/m²")
    else:
        print("Failed to fetch solar irradiance data")
