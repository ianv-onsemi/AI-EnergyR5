import sys
import os
import logging
import time
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from db.db_connector import get_connection
from api_wrappers.nasa_power import get_solar_irradiance_data
from scripts.capture_weather_data import insert_weather_data

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def get_last_nasa_timestamp():
    """Get the latest timestamp from NASA POWER data specifically"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT MAX(timestamp) 
                FROM sensor_data 
                WHERE source = 'nasa_power'
            """)
            result = cur.fetchone()
            conn.close()
            return result[0] if result and result[0] else None
    except Exception as e:
        logger.error(f"Failed to get last NASA timestamp: {e}")
        return None

def fetch_historical_solar_data(start_date, end_date):
    """Fetch historical solar irradiance data from NASA POWER API for a date range"""
    solar_data_list = []
    current_date = start_date

    while current_date <= end_date:
        try:
            logger.info(f"Fetching solar data for {current_date.strftime('%Y-%m-%d')}")
            solar_data = get_solar_irradiance_data()
            if solar_data:
                # Adjust timestamp to current_date
                adjusted_timestamp = current_date.strftime("%Y-%m-%d %H:%M:%S")
                adjusted_data = (adjusted_timestamp, solar_data[1])
                solar_data_list.append(adjusted_data)
                logger.info(f"  -> Got irradiance: {solar_data[1]} W/m²")
            current_date += timedelta(days=1)
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to fetch solar data for {current_date}: {e}")
            current_date += timedelta(days=1)

    return solar_data_list

def backfill_nasa_data():
    """Backfill NASA POWER data from the last timestamp to today"""
    
    # Get last NASA POWER timestamp
    last_timestamp = get_last_nasa_timestamp()
    
    if not last_timestamp:
        logger.error("No NASA POWER data found in database - cannot determine start date")
        return {
            'success': False,
            'error': 'No existing NASA POWER data found'
        }
    
    logger.info(f"Last NASA POWER timestamp: {last_timestamp}")
    
    # Calculate date range to backfill
    start_date = last_timestamp.date() + timedelta(days=1)
    end_date = datetime.now().date()
    
    logger.info(f"Backfilling from {start_date} to {end_date}")
    
    if start_date > end_date:
        logger.info("No backfill needed - NASA POWER data is up to date")
        return {
            'success': True,
            'message': 'NASA POWER data is up to date',
            'total_rows': 0
        }
    
    # Fetch solar data for the date range
    solar_data_list = fetch_historical_solar_data(start_date, end_date)
    
    # Insert solar data
    solar_rows_inserted = 0
    if solar_data_list:
        try:
            conn = get_connection()
            for solar_data in solar_data_list:
                # Check if timestamp already exists
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM sensor_data WHERE timestamp = %s", (solar_data[0],))
                    if cur.fetchone()[0] == 0:
                        # Create combined data entry with NASA POWER source
                        combined_data = (solar_data[0], 0.0, 0.0, solar_data[1], 0.0)
                        insert_weather_data(conn, combined_data, source='nasa_power')
                        solar_rows_inserted += 1
                        logger.info(f"Inserted NASA POWER data for {solar_data[0]}")
                    else:
                        logger.info(f"Skipping duplicate timestamp: {solar_data[0]}")

            conn.close()
            logger.info(f"NASA POWER data inserted: {solar_rows_inserted} rows")
        except Exception as e:
            logger.error(f"Failed to insert NASA POWER data: {e}")
            return {
                'success': False,
                'error': str(e),
                'solar_rows': 0
            }
    
    return {
        'success': True,
        'total_rows': solar_rows_inserted,
        'solar_rows': solar_rows_inserted,
        'time_range': f'{start_date} to {end_date}',
        'message': f'Backfilled {solar_rows_inserted} rows of NASA POWER data'
    }

if __name__ == "__main__":
    logger.info("Starting NASA POWER data backfill...")
    
    result = backfill_nasa_data()
    
    print("\n=== BACKFILL RESULT ===")
    print(f"Success: {result.get('success', False)}")
    print(f"Total rows inserted: {result.get('total_rows', 0)}")
    print(f"Solar rows: {result.get('solar_rows', 0)}")
    print(f"Time range: {result.get('time_range', 'N/A')}")
    if result.get('message'):
        print(f"Message: {result['message']}")
    if result.get('error'):
        print(f"Error: {result['error']}")
