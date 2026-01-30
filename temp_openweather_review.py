import sys
sys.path.insert(0, 'db')
from db_connector import get_connection

conn = get_connection()
with conn.cursor() as cur:
    # Check all data sources
    cur.execute("SELECT DISTINCT source FROM sensor_data ORDER BY source")
    sources = cur.fetchall()
    print('All data sources in database:')
    for source in sources:
        print(f'  {source[0] if source[0] else "NULL"}')

    # Check OpenWeather data specifically
    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source LIKE '%openweather%' OR source LIKE '%weather%'")
    openweather_count = cur.fetchone()[0]
    print(f'\nOpenWeather data count: {openweather_count}')

    if openweather_count > 0:
        # Get sample OpenWeather data
        cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed, source FROM sensor_data WHERE source LIKE '%openweather%' OR source LIKE '%weather%' ORDER BY timestamp DESC LIMIT 5")
        openweather_rows = cur.fetchall()
        print('\nSample OpenWeather data:')
        for row in openweather_rows:
            print(f'  Timestamp: {row[0]}, Temp: {row[1]}, Humidity: {row[2]}, Irradiance: {row[3]}, Wind: {row[4]}, Source: {row[5]}')

        # Get summary statistics for OpenWeather data
        cur.execute("""
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
                ROUND(AVG(wind_speed)::numeric, 2) as avg_wind_speed,
                MIN(wind_speed) as min_wind_speed,
                MAX(wind_speed) as max_wind_speed
            FROM sensor_data
            WHERE source LIKE '%openweather%' OR source LIKE '%weather%'
        """)
        summary = cur.fetchone()
        if summary and summary[0] > 0:
            print('\nOpenWeather Data Summary:')
            print(f'  Total rows: {summary[0]}')
            print(f'  Time range: {summary[1]} to {summary[2]}')
            print(f'  Temperature: avg={summary[3]}, min={summary[4]}, max={summary[5]}')
            print(f'  Humidity: avg={summary[6]}, min={summary[7]}, max={summary[8]}')
            print(f'  Wind Speed: avg={summary[9]}, min={summary[10]}, max={summary[11]}')

conn.close()
