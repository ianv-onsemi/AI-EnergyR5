import psycopg2
from tabulate import tabulate
from datetime import datetime, timedelta

def get_connection():
    """Establish database connection"""
    return psycopg2.connect(
        dbname="energy_db",
        user="postgres",
        password="PdM",
        host="localhost",
        port="8000"
    )

def show_recent_weather_data():
    """Show the 10 most recent weather data entries (with temperature, humidity, wind speed)"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get weather data (entries with temperature > 0 and irradiance = 0, indicating weather-only data)
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed
                FROM sensor_data
                WHERE temperature > 0 AND irradiance = 0
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            weather_rows = cur.fetchall()

        conn.close()

        if weather_rows:
            print("\n=== RECENT WEATHER DATA (Step 2.1 - OpenWeather API) ===")
            print(f"Showing {len(weather_rows)} most recent entries:")
            headers = ["Timestamp", "Temperature (°C)", "Humidity (%)", "Irradiance (W/m²)", "Wind Speed (m/s)"]
            print(tabulate(weather_rows, headers=headers, tablefmt="grid"))
        else:
            print("\n=== RECENT WEATHER DATA (Step 2.1 - OpenWeather API) ===")
            print("No weather data found in database.")

    except Exception as e:
        print(f"Error fetching weather data: {e}")

def show_recent_solar_data():
    """Show the 10 most recent solar irradiance data entries"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get solar irradiance data (entries with irradiance > 0)
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed
                FROM sensor_data
                WHERE irradiance > 0
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            solar_rows = cur.fetchall()

        conn.close()

        if solar_rows:
            print("\n=== RECENT SOLAR IRRADIANCE DATA (Step 2.2 - NASA POWER API) ===")
            print(f"Showing {len(solar_rows)} most recent entries:")
            headers = ["Timestamp", "Temperature (°C)", "Humidity (%)", "Irradiance (W/m²)", "Wind Speed (m/s)"]
            print(tabulate(solar_rows, headers=headers, tablefmt="grid"))
        else:
            print("\n=== RECENT SOLAR IRRADIANCE DATA (Step 2.2 - NASA POWER API) ===")
            print("No solar irradiance data found in database.")

    except Exception as e:
        print(f"Error fetching solar irradiance data: {e}")

def show_combined_recent_data():
    """Show the 10 most recent combined data entries"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get the 10 most recent entries
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed
                FROM sensor_data
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            combined_rows = cur.fetchall()

        conn.close()

        if combined_rows:
            print("\n=== MOST RECENT COMBINED DATA (Weather + Solar) ===")
            print(f"Showing {len(combined_rows)} most recent entries:")
            headers = ["Timestamp", "Temperature (°C)", "Humidity (%)", "Irradiance (W/m²)", "Wind Speed (m/s)"]
            print(tabulate(combined_rows, headers=headers, tablefmt="grid"))
        else:
            print("\n=== MOST RECENT COMBINED DATA (Weather + Solar) ===")
            print("No data found in database.")

    except Exception as e:
        print(f"Error fetching combined data: {e}")

if __name__ == "__main__":
    print("Fetching recent data from database...")
    print("=" * 60)

    show_recent_weather_data()
    show_recent_solar_data()
    show_combined_recent_data()

    print("\n" + "=" * 60)
    print("Data retrieval complete.")
