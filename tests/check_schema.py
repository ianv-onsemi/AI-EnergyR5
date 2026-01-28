from db_connector import get_connection

conn = get_connection()
cur = conn.cursor()
cur.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'sensor_data' ORDER BY ordinal_position")
print('Table schema:')
for row in cur.fetchall():
    print(f'{row[0]}: {row[1]}')
conn.close()
