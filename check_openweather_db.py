import sys
sys.path.insert(0, 'db')
from db_connector import get_connection

conn = get_connection()
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = 'openweather'")
    count = cur.fetchone()[0]
    print(f'OpenWeather rows in database: {count}')

    if count > 0:
        cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed, source FROM sensor_data WHERE source = 'openweather' ORDER BY timestamp DESC LIMIT 3")
        rows = cur.fetchall()
        print('Sample OpenWeather data:')
        for row in rows:
            print(f'  {row}')

conn.close()
