from db.db_connector import get_connection
from datetime import datetime

# Connect to database
conn = get_connection()
cur = conn.cursor()

# Get current timestamp
retrieval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Query sim data ordered by timestamp
cur.execute("SELECT timestamp, temperature, humidity, irradiance, wind_speed FROM sensor_data WHERE source = 'sim' ORDER BY timestamp;")
rows = cur.fetchall()

# Count sim rows
sim_count = len(rows)

# Create the file
with open('data/collect1.txt', 'w') as f:
    # Top row: timestamp and summary
    f.write(f'# Data collection last updated: {retrieval_time}\n')
    f.write(f'# Summary: sim={sim_count}\n')
    f.write('[sim]\n')
    f.write('timestamp,temperature,humidity,irradiance,wind_speed\n')
    for row in rows:
        f.write(f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]}\n')

conn.close()
print('collect1.txt updated successfully.')
