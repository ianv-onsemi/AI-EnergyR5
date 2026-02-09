import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        dbname='energy_db',
        user='postgres',
        password='PdM',
        host='localhost',
        port='5432'
    )


try:
    conn = get_connection()
    with conn.cursor() as cur:
        # Get latest NASA POWER timestamp
        cur.execute("""
            SELECT MAX(timestamp) as latest_timestamp, COUNT(*) as total_rows
            FROM sensor_data 
            WHERE source = 'nasa_power'
        """)
        result = cur.fetchone()
        
        if result and result[0]:
            latest_ts = result[0]
            total_rows = result[1]
            
            # Calculate gap
            today = datetime.now()
            gap = today - latest_ts
            gap_days = gap.days
            
            print(f'Latest NASA POWER timestamp: {latest_ts}')
            print(f'Total NASA POWER rows: {total_rows}')
            print(f'Today: {today.strftime("%Y-%m-%d %H:%M:%S")}')
            print(f'Gap: {gap_days} days')
        else:
            print('No NASA POWER data found in database')
            
        # Also check all sources for context
        cur.execute("""
            SELECT source, COUNT(*), MAX(timestamp)
            FROM sensor_data 
            GROUP BY source
            ORDER BY MAX(timestamp) DESC
        """)
        all_sources = cur.fetchall()
        print('\n--- All Data Sources ---')
        for source in all_sources:
            print(f'Source: {source[0]}, Count: {source[1]}, Latest: {source[2]}')
            
    conn.close()
except Exception as e:
    print(f'Error: {e}')
