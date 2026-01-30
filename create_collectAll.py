from db.db_connector import get_connection
from datetime import datetime

# Connect to database
conn = get_connection()
cur = conn.cursor()

# Get current timestamp
retrieval_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Query all data ordered by timestamp
cur.execute('SELECT id, timestamp, temperature, humidity, irradiance, wind_speed, source FROM sensor_data ORDER BY timestamp;')
rows = cur.fetchall()

# Group by source
groups = {}
for row in rows:
    source = row[6] if row[6] else 'unknown'
    if source not in groups:
        groups[source] = []
    groups[source].append(row)

# Count per source
counts = {source: len(data) for source, data in groups.items()}
total = sum(counts.get(source, 0) for source in ['sim', 'openweather', 'nasa-power'])

# Create the file
with open('data/collectAll.txt', 'w') as f:
    # Top row: timestamp and summary
    summary = f"Data retrieved at: {retrieval_time} | Total rows: {total}"
    for source in ['sim', 'openweather', 'nasa-power']:
        if source in counts:
            summary += f" | {source}: {counts[source]}"
        else:
            summary += f" | {source}: 0"
    f.write(summary + '\n\n')

    # Write each group
    for source in ['sim', 'openweather', 'nasa-power']:
        if source in groups:
            f.write(f'--- {source.upper()} DATA ---\n')
            f.write('id,timestamp,temperature,humidity,irradiance,wind_speed,source\n')
            for row in groups[source]:
                f.write(f'{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{row[6]}\n')
            f.write('\n')

conn.close()
print('collectAll.txt created successfully.')
