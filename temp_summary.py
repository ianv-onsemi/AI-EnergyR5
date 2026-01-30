import psycopg2
from db.db_connector import get_db_connection

def get_sim_summary():
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT
        COUNT(*) as total_rows,
        MIN(timestamp) as earliest_timestamp,
        MAX(timestamp) as latest_timestamp,
        ROUND(AVG(temperature)::numeric, 2) as avg_temperature,
        MIN(temperature) as min_temperature,
        MAX(temperature) as max_temperature,
        ROUND(AVG(humidity)::numeric, 2) as avg_humidity,
        MIN(humidity) as min_humidity,
        MAX(humidity) as max_humidity,
        ROUND(AVG(irradiance)::numeric, 2) as avg_irradiance,
        MIN(irradiance) as min_irradiance,
        MAX(irradiance) as max_irradiance,
        ROUND(AVG(wind_speed)::numeric, 2) as avg_wind_speed,
        MIN(wind_speed) as min_wind_speed,
        MAX(wind_speed) as max_wind_speed
    FROM sensor_data
    WHERE source = 'sim'
    """

    cursor.execute(query)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result

if __name__ == "__main__":
    summary = get_sim_summary()
    print("=== SIM DATA SUMMARY ===")
    print(f"Total Rows: {summary[0]}")
    print(f"Time Range: {summary[1]} to {summary[2]}")
    print(f"Temperature: Avg={summary[3]}, Min={summary[4]}, Max={summary[5]}")
    print(f"Humidity: Avg={summary[6]}, Min={summary[7]}, Max={summary[8]}")
    print(f"Irradiance: Avg={summary[9]}, Min={summary[10]}, Max={summary[11]}")
    print(f"Wind Speed: Avg={summary[12]}, Min={summary[13]}, Max={summary[14]}")
