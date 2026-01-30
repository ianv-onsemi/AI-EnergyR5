import sys
sys.path.insert(0, 'db')
from db_connector import get_connection

conn = get_connection()
with conn.cursor() as cur:
    # Check sim data count and sample
    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = 'sim'")
    sim_count = cur.fetchone()[0]
    print(f'Sim data count: {sim_count}')

    cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed FROM sensor_data WHERE source = 'sim' ORDER BY timestamp DESC LIMIT 3")
    sim_rows = cur.fetchall()
    print('Sample sim data:')
    for row in sim_rows:
        print(f'  {row}')

    # Check unknown data count and sample
    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source != 'sim' OR source IS NULL")
    unknown_count = cur.fetchone()[0]
    print(f'\nUnknown data count: {unknown_count}')

    cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed, source FROM sensor_data WHERE source != 'sim' OR source IS NULL ORDER BY timestamp DESC LIMIT 3")
    unknown_rows = cur.fetchall()
    print('Sample unknown data:')
    for row in unknown_rows:
        print(f'  {row}')

conn.close()
