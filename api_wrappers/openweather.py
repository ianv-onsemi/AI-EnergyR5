import requests
from datetime import datetime
import math

API_KEY = "0723d71a05e58ae3f7fc91e39a901e6b"
CITY = "Manila"
LATITUDE = 14.5995  # Manila latitude
LONGITUDE = 120.9842  # Manila longitude

# One Call API 3.0 URL
ONECALL_URL = f"https://api.openweathermap.org/data/3.0/onecall?lat={LATITUDE}&lon={LONGITUDE}&appid={API_KEY}&units=metric&exclude=minutely,hourly,daily,alerts"

def calculate_wind_power_density(wind_speed_mps):
    """
    Calculate wind power density using P = 0.5 × ρ × v³
    ρ (air density) = 1.225 kg/m³ at sea level
    v = wind speed in m/s
    Returns power density in W/m²
    """
    air_density = 1.225  # kg/m³
    wind_speed_cubic = wind_speed_mps ** 3
    power_density = 0.5 * air_density * wind_speed_cubic
    return round(power_density, 2)

def calculate_solar_energy_yield(solar_irradiance, cloudiness, uv_index=None):
    """
    Estimate solar energy yield in kWh/m²/day
    Uses irradiance, cloudiness, and UV index for better accuracy
    """
    # Base calculation from irradiance (W/m² to kWh/m²/day)
    # Assuming 4 peak sun hours per day in tropical regions like Manila
    peak_sun_hours = 4.0

    # Adjust for cloudiness (0-100%)
    cloud_factor = (100 - cloudiness) / 100

    # UV index provides additional accuracy for solar intensity
    uv_factor = 1.0
    if uv_index is not None:
        # UV index typically ranges from 0-11+, higher UV means stronger solar radiation
        uv_factor = max(0.5, min(2.0, uv_index / 6))  # Normalize around typical values

    # Calculate daily energy yield
    daily_yield = (solar_irradiance * peak_sun_hours * cloud_factor * uv_factor) / 1000  # Convert to kWh

    return round(daily_yield, 3)

def get_weather_data():
    """
    Fetch enhanced weather data from OpenWeather One Call API 3.0
    Includes wind and solar energy calculations
    """
    try:
        # Try One Call API 3.0 first
        response = requests.get(ONECALL_URL, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Extract current weather data
        current = data.get('current', {})

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temperature = current.get('temp', 25)  # Default to 25°C if missing
        humidity = current.get('humidity', 70)  # Default to 70% if missing
        wind_speed = current.get('wind_speed', 2.0)  # Default to 2 m/s if missing
        cloudiness = current.get('clouds', 50)  # Default to 50% if missing
        uv_index = current.get('uvi', 6)  # Default to 6 if missing

        # Enhanced solar irradiance calculation using multiple factors
        base_irradiance = (100 - cloudiness) * 10  # Base calculation
        uv_adjustment = uv_index * 25  # UV index contribution
        solar_irradiance = round(base_irradiance + uv_adjustment, 2)

        # Calculate energy metrics
        wind_power_density = calculate_wind_power_density(wind_speed)
        solar_energy_yield = calculate_solar_energy_yield(solar_irradiance, cloudiness, uv_index)

        return {
            "timestamp": timestamp,
            "temperature": temperature,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "solar_irradiance": solar_irradiance,
            "wind_power_density": wind_power_density,
            "solar_energy_yield": solar_energy_yield
        }

    except Exception as e:
        print(f"One Call API failed: {e}, falling back to basic weather API")

        # Fallback to basic weather API
        try:
            BASIC_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
            response = requests.get(BASIC_URL, verify=False, timeout=10)
            response.raise_for_status()
            data = response.json()

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            temperature = data.get('main', {}).get('temp', 25)
            humidity = data.get('main', {}).get('humidity', 70)
            wind_speed = data.get('wind', {}).get('speed', 2.0)
            cloudiness = data.get('clouds', {}).get('all', 50)

            # Basic irradiance calculation (fallback)
            solar_irradiance = round((100 - cloudiness) * 10, 2)

            # Calculate energy metrics with basic data
            wind_power_density = calculate_wind_power_density(wind_speed)
            solar_energy_yield = calculate_solar_energy_yield(solar_irradiance, cloudiness)

            return {
                "timestamp": timestamp,
                "temperature": temperature,
                "humidity": humidity,
                "wind_speed": wind_speed,
                "solar_irradiance": solar_irradiance,
                "wind_power_density": wind_power_density,
                "solar_energy_yield": solar_energy_yield
            }

        except Exception as e2:
            print(f"Basic weather API also failed: {e2}")
            return None
