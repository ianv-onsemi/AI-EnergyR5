import sys
sys.path.insert(0, 'db')
from db_connector import get_connection

conn = get_connection()
with conn.cursor() as cur:
    # Get total count and data sources
    cur.execute("SELECT COUNT(*) FROM sensor_data")
    total_count = cur.fetchone()[0]

    cur.execute("SELECT DISTINCT source FROM sensor_data ORDER BY source")
    sources = cur.fetchall()

    print(f"Total rows in database: {total_count}")
    print("Data sources:")
    for source in sources:
        source_name = source[0] if source[0] else "NULL"
        cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = %s OR (source IS NULL AND %s IS NULL)", (source[0], source[0]))
        count = cur.fetchone()[0]
        print(f"  {source_name}: {count} rows")

    # Check OpenWeather data specifically
    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = 'openweather'")
    openweather_count = cur.fetchone()[0]
    print(f"\nOpenWeather data count: {openweather_count}")

    if openweather_count > 0:
        # Get sample OpenWeather data
        cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed, source FROM sensor_data WHERE source = 'openweather' ORDER BY timestamp LIMIT 5")
        openweather_rows = cur.fetchall()
        print("\nFirst 5 OpenWeather data rows:")
        for row in openweather_rows:
            print(f"  Timestamp: {row[0]}, Temp: {row[1]}, Humidity: {row[2]}, Irradiance: {row[3]}, Wind: {row[4]}, Source: {row[5]}")

        # Get summary statistics for OpenWeather data
        cur.execute("""
            SELECT
                COUNT(*) as total_rows,
                MIN(timestamp) as earliest_timestamp,
                MAX(timestamp) as latest_timestamp,
                ROUND(AVG(irradiance)::numeric, 2) as avg_irradiance,
                MIN(irradiance) as min_irradiance,
                MAX(irradiance) as max_irradiance,
                ROUND(AVG(wind_speed)::numeric, 2) as avg_wind_speed,
                MIN(wind_speed) as min_wind_speed,
                MAX(wind_speed) as max_wind_speed
            FROM sensor_data
            WHERE source = 'openweather'
        """)
        summary = cur.fetchone()
        if summary and summary[0] > 0:
            print("\nOpenWeather Data Summary:")
            print(f"  Total rows: {summary[0]}")
            print(f"  Time range: {summary[1]} to {summary[2]}")
            print(f"  Irradiance: avg={summary[3]}, min={summary[4]}, max={summary[5]}")
            print(f"  Wind Speed: avg={summary[6]}, min={summary[7]}, max={summary[8]}")
    else:
        print("\nNo OpenWeather data found in database.")

conn.close()
