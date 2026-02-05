from flask import Flask, jsonify, request
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
import time
import requests
import schedule
import threading

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import our ingestion functions
from db.db_ingest import run_ingestion
from db.sensor_stream_sim import generate_sensor_data
from scripts.capture_weather_data import fetch_weather_data, insert_weather_data
from api_wrappers.nasa_power import get_solar_irradiance_data
from db.db_connector import get_connection

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Global variables for continuous ingestion
continuous_ingestion_active = False
last_ingestion_time = None

def retry_with_backoff(func, max_retries=3, base_delay=1):
    """Retry a function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)

def get_last_timestamp():
    """Get the latest timestamp from the database"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT MAX(timestamp) FROM sensor_data;")
            result = cur.fetchone()
            conn.close()
            return result[0] if result and result[0] else None
    except Exception as e:
        logger.error(f"Failed to get last timestamp: {e}")
        return None

def fetch_historical_weather_data(start_date, end_date):
    """Fetch historical weather data from OpenWeather API for a date range"""
    weather_data_list = []
    current_date = start_date

    while current_date <= end_date:
        try:
            # Note: OpenWeather free tier doesn't support historical data
            # This is a placeholder for future implementation with paid tier
            logger.info(f"Fetching weather data for {current_date.strftime('%Y-%m-%d')}")
            # For now, fetch current data as approximation
            weather_data = fetch_weather_data()
            if weather_data:
                # Adjust timestamp to current_date
                adjusted_timestamp = current_date.strftime("%Y-%m-%d %H:%M:%S")
                adjusted_data = (adjusted_timestamp, weather_data[1], weather_data[2], weather_data[3], weather_data[4])
                weather_data_list.append(adjusted_data)
            current_date += timedelta(days=1)
            time.sleep(1)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to fetch historical weather data for {current_date}: {e}")
            current_date += timedelta(days=1)

    return weather_data_list

def fetch_historical_solar_data(start_date, end_date):
    """Fetch historical solar irradiance data from NASA POWER API for a date range"""
    solar_data_list = []
    current_date = start_date

    while current_date <= end_date:
        try:
            logger.info(f"Fetching solar data for {current_date.strftime('%Y-%m-%d')}")
            # NASA POWER API can provide historical data
            # This is a simplified implementation
            solar_data = get_solar_irradiance_data()
            if solar_data:
                # Adjust timestamp to current_date
                adjusted_timestamp = current_date.strftime("%Y-%m-%d %H:%M:%S")
                adjusted_data = (adjusted_timestamp, solar_data[1])
                solar_data_list.append(adjusted_data)
            current_date += timedelta(days=1)
            time.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"Failed to fetch historical solar data for {current_date}: {e}")
            current_date += timedelta(days=1)

    return solar_data_list

def perform_continuous_ingestion():
    """Perform continuous ingestion based on schedule and rules"""
    global last_ingestion_time

    current_time = datetime.now()
    current_hour = current_time.hour

    # Rule 2: Check if time is later than 8 PM
    if current_hour >= 20:  # 8 PM is 20:00
        logger.info("Scheduled ingestion triggered (after 8 PM)")

        # Get last timestamp from database
        last_timestamp = get_last_timestamp()
        if last_timestamp:
            # Calculate start date as day after last timestamp
            start_date = last_timestamp.date() + timedelta(days=1)
        else:
            # If no data, start from yesterday
            start_date = current_time.date() - timedelta(days=1)

        end_date = current_time.date()

        if start_date > end_date:
            logger.info("No new data needed - database is up to date")
            return {
                'success': True,
                'message': 'Database is up to date',
                'total_rows': 0,
                'time_range': f'{start_date} to {end_date}'
            }

        logger.info(f"Fetching data from {start_date} to {end_date}")

        # Fetch historical weather data
        weather_data_list = fetch_historical_weather_data(start_date, end_date)

        # Fetch historical solar data
        solar_data_list = fetch_historical_solar_data(start_date, end_date)

        # Insert weather data
        weather_rows_inserted = 0
        if weather_data_list:
            try:
                conn = get_connection()
                for weather_data in weather_data_list:
                    # Rule 1: Check if timestamp already exists
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM sensor_data WHERE timestamp = %s", (weather_data[0],))
                        if cur.fetchone()[0] == 0:
                            insert_weather_data(conn, weather_data)
                            weather_rows_inserted += 1
                conn.close()
                logger.info(f"Weather data inserted: {weather_rows_inserted} rows")
            except Exception as e:
                logger.error(f"Failed to insert weather data: {e}")

        # Insert solar data
        solar_rows_inserted = 0
        if solar_data_list:
            try:
                conn = get_connection()
                for solar_data in solar_data_list:
                    # Rule 1: Check if timestamp already exists
                    with conn.cursor() as cur:
                        cur.execute("SELECT COUNT(*) FROM sensor_data WHERE timestamp = %s", (solar_data[0],))
                        if cur.fetchone()[0] == 0:
                            # Create combined data entry
                            combined_data = (solar_data[0], 0.0, 0.0, solar_data[1], 0.0)
                            insert_weather_data(conn, combined_data)
                            solar_rows_inserted += 1
                conn.close()
                logger.info(f"Solar data inserted: {solar_rows_inserted} rows")
            except Exception as e:
                logger.error(f"Failed to insert solar data: {e}")

        total_rows = weather_rows_inserted + solar_rows_inserted
        last_ingestion_time = current_time

        return {
            'success': True,
            'total_rows': total_rows,
            'time_range': f'{start_date} to {end_date}',
            'weather_rows': weather_rows_inserted,
            'solar_rows': solar_rows_inserted
        }
    else:
        logger.info("Scheduled ingestion skipped - not yet 8 PM")
        return {
            'success': True,
            'message': 'Not yet 8 PM - skipping scheduled ingestion',
            'total_rows': 0
        }

def start_continuous_ingestion():
    """Start the continuous ingestion scheduler"""
    global continuous_ingestion_active

    if continuous_ingestion_active:
        logger.info("Continuous ingestion already active")
        return

    continuous_ingestion_active = True
    logger.info("Starting continuous ingestion scheduler")

    # Schedule daily check at 8 PM
    schedule.every().day.at("20:00").do(perform_continuous_ingestion)

    def run_scheduler():
        while continuous_ingestion_active:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Continuous ingestion scheduler started")

def stop_continuous_ingestion():
    """Stop the continuous ingestion scheduler"""
    global continuous_ingestion_active
    continuous_ingestion_active = False
    logger.info("Continuous ingestion scheduler stopped")

@app.route('/')
def serve_dashboard():
    """Serve the dashboard.html file"""
    try:
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        if os.path.exists(dashboard_path):
            with open(dashboard_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/html'}
        else:
            return 'Dashboard not found', 404
    except Exception as e:
        logger.error(f"Failed to serve dashboard: {e}")
        return 'Error serving dashboard', 500

@app.route('/check_postgres_status', methods=['GET'])
def check_postgres_status():
    """Check PostgreSQL server status"""
    try:
        # Path to pg_ctl.exe on Windows
        pg_ctl_path = r"D:\My Documents\tools\postgresql\pgsql\bin\pg_ctl.exe"
        data_dir = r"D:\My Documents\tools\postgresql\pgsql\data"

        result = subprocess.run([pg_ctl_path, "-D", data_dir, "status"],
                               capture_output=True, text=True)

        if result.returncode == 0:
            return jsonify({'success': True, 'status': 'running', 'message': result.stdout.strip()})
        else:
            return jsonify({'success': False, 'status': 'not running', 'message': result.stderr.strip()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/verify_db_connection', methods=['GET'])
def verify_db_connection():
    """Verify database connection by running test_connection.py"""
    try:
        result = subprocess.run([sys.executable, "../db/test_connection.py"],
                               capture_output=True, text=True, cwd=os.path.dirname(__file__))

        if result.returncode == 0:
            return jsonify({'success': True, 'output': result.stdout.strip()})
        else:
            return jsonify({'success': False, 'error': result.stderr.strip()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/test_automatic_ingestion', methods=['POST'])
def test_automatic_ingestion():
    """Test automatic ingestion function"""
    try:
        result = perform_continuous_ingestion()
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



@app.route('/view_logs', methods=['GET'])
def view_logs():
    """View ingestion logs"""
    try:
        log_path = os.path.join(os.path.dirname(__file__), '..', 'logs', 'ingestion.log')
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                content = f.read()
            return jsonify({'success': True, 'logs': content})
        else:
            return jsonify({'success': False, 'error': 'Log file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/final_db_check', methods=['GET'])
def final_db_check():
    """Final database check (same as verify_db_connection)"""
    return verify_db_connection()

@app.route('/get_weather_data_from_db', methods=['GET'])
def get_weather_data_from_db():
    """Get recent weather data from database and return as JSON"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            # Get the 10 most recent entries with weather data (temperature, humidity, wind_speed)
            cur.execute("""
                SELECT timestamp, temperature, humidity, wind_speed, source
                FROM sensor_data
                WHERE temperature IS NOT NULL AND temperature != 0.0
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
        conn.close()

        # Format data for JSON response
        weather_data = []
        for row in rows:
            weather_data.append({
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else '',
                'temperature': float(row[1]) if row[1] else 0.0,
                'humidity': float(row[2]) if row[2] else 0.0,
                'wind_speed': float(row[3]) if row[3] else 0.0,
                'source': row[4] if row[4] else 'Database'
            })

        return jsonify({
            'success': True,
            'data': weather_data,
            'count': len(weather_data)
        })

    except Exception as e:
        logger.error(f"Failed to get weather data from database: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_sim_summary():
    """Get summary statistics for sim data"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
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
                    ROUND(AVG(irradiance)::numeric, 2) as avg_irradiance,
                    MIN(irradiance) as min_irradiance,
                    MAX(irradiance) as max_irradiance,
                    ROUND(AVG(wind_speed)::numeric, 2) as avg_wind_speed,
                    MIN(wind_speed) as min_wind_speed,
                    MAX(wind_speed) as max_wind_speed
                FROM sensor_data
                WHERE source = 'sim'
            """)
            result = cur.fetchone()
        conn.close()

        if result and result[0] > 0:  # Check if there are any rows
            return {
                'total_rows': result[0],
                'time_range': f"{result[1].strftime('%Y-%m-%d %H:%M:%S') if result[1] else 'N/A'} to {result[2].strftime('%Y-%m-%d %H:%M:%S') if result[2] else 'N/A'}",
                'temperature': {
                    'avg': float(result[3]) if result[3] else 0.0,
                    'min': float(result[4]) if result[4] else 0.0,
                    'max': float(result[5]) if result[5] else 0.0
                },
                'humidity': {
                    'avg': float(result[6]) if result[6] else 0.0,
                    'min': float(result[7]) if result[7] else 0.0,
                    'max': float(result[8]) if result[8] else 0.0
                },
                'irradiance': {
                    'avg': float(result[9]) if result[9] else 0.0,
                    'min': float(result[10]) if result[10] else 0.0,
                    'max': float(result[11]) if result[11] else 0.0
                },
                'wind_speed': {
                    'avg': float(result[12]) if result[12] else 0.0,
                    'min': float(result[13]) if result[13] else 0.0,
                    'max': float(result[14]) if result[14] else 0.0
                }
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get sim summary: {e}")
        return None

def get_weather_summary():
    """Get summary statistics for weather data (non-sim sources including NULL)"""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
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
                    ROUND(AVG(irradiance)::numeric, 2) as avg_irradiance,
                    MIN(irradiance) as min_irradiance,
                    MAX(irradiance) as max_irradiance,
                    ROUND(AVG(wind_speed)::numeric, 2) as avg_wind_speed,
                    MIN(wind_speed) as min_wind_speed,
                    MAX(wind_speed) as max_wind_speed
                FROM sensor_data
                WHERE source != 'sim' OR source IS NULL
            """)
            result = cur.fetchone()
        conn.close()

        if result and result[0] > 0:  # Check if there are any rows
            return {
                'total_rows': result[0],
                'time_range': f"{result[1].strftime('%Y-%m-%d %H:%M:%S') if result[1] else 'N/A'} to {result[2].strftime('%Y-%m-%d %H:%M:%S') if result[2] else 'N/A'}",
                'temperature': {
                    'avg': float(result[3]) if result[3] else 0.0,
                    'min': float(result[4]) if result[4] else 0.0,
                    'max': float(result[5]) if result[5] else 0.0
                },
                'humidity': {
                    'avg': float(result[6]) if result[6] else 0.0,
                    'min': float(result[7]) if result[7] else 0.0,
                    'max': float(result[8]) if result[8] else 0.0
                },
                'irradiance': {
                    'avg': float(result[9]) if result[9] else 0.0,
                    'min': float(result[10]) if result[10] else 0.0,
                    'max': float(result[11]) if result[11] else 0.0
                },
                'wind_speed': {
                    'avg': float(result[12]) if result[12] else 0.0,
                    'min': float(result[13]) if result[13] else 0.0,
                    'max': float(result[14]) if result[14] else 0.0
                }
            }
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get weather summary: {e}")
        return None

@app.route('/fetch_sim_data_from_db', methods=['GET'])
def fetch_sim_data_from_db():
    """Fetch sim data from database and update collect1.txt"""
    try:
        logger.info("Fetching sim data from database")

        # Validate database connection
        conn = get_connection()
        if not conn:
            raise Exception("Failed to establish database connection")

        with conn.cursor() as cur:
            # Get ALL sim data entries
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed
                FROM sensor_data
                WHERE source = 'sim'
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()
        conn.close()

        if not rows:
            logger.warning("No sim data found in database")
            return jsonify({
                'success': False,
                'error': 'No sim data found in database'
            }), 404

        # Validate and format data for JSON response
        sim_data = []
        for row in rows:
            try:
                # Data validation
                if len(row) != 5:
                    logger.warning(f"Invalid row length: expected 5, got {len(row)}")
                    continue

                timestamp = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else ''
                temperature = float(row[1]) if row[1] is not None else 0.0
                humidity = float(row[2]) if row[2] is not None else 0.0
                irradiance = float(row[3]) if row[3] is not None else 0.0
                wind_speed = float(row[4]) if row[4] is not None else 0.0

                sim_data.append({
                    'timestamp': timestamp,
                    'temperature': temperature,
                    'humidity': humidity,
                    'irradiance': irradiance,
                    'wind_speed': wind_speed
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Data validation error for row: {e}")
                continue

        # Get summary information
        summary = get_sim_summary()

        # Update collect1.txt with the fetched data (with error handling)
        data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'collect1.txt')
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            with open(data_file_path, 'w', encoding='utf-8') as f:
                f.write(f'# Data collection last updated: {current_timestamp}\n')
                # Dynamically calculate row count
                actual_row_count = len(sim_data)
                f.write(f'# Summary: sim={actual_row_count}\n')
                f.write('[sim]\n')
                f.write('timestamp,temperature,humidity,irradiance,wind_speed\n')

                rows_written = 0
                for row in rows:
                    try:
                        timestamp_str = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else current_timestamp
                        temp_val = row[1] if row[1] is not None else 0.0
                        hum_val = row[2] if row[2] is not None else 0.0
                        irr_val = row[3] if row[3] is not None else 0.0
                        wind_val = row[4] if row[4] is not None else 0.0

                        f.write(f'{timestamp_str},{temp_val},{hum_val},{irr_val},{wind_val}\n')
                        rows_written += 1
                    except Exception as write_error:
                        logger.warning(f"Failed to write row to file: {write_error}")
                        continue

                logger.info(f"Successfully wrote {rows_written} rows to collect1.txt")

        except IOError as file_error:
            logger.error(f"Failed to write to collect1.txt: {file_error}")
            return jsonify({
                'success': False,
                'error': f'File write error: {str(file_error)}'
            }), 500

        logger.info(f"Sim data fetched and collect1.txt updated: {len(sim_data)} rows")

        return jsonify({
            'success': True,
            'rows_fetched': len(sim_data),
            'data': sim_data,
            'summary': summary,
            'message': f'Sim data fetched and collect1.txt updated with {len(sim_data)} rows'
        })

    except Exception as e:
        logger.error(f"Failed to fetch sim data from database: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/fetch_weather_data_from_db', methods=['GET'])
def fetch_weather_data_from_db():
    """Fetch weather data from database and update collect2.txt"""
    try:
        logger.info("Fetching weather data from database")

        conn = get_connection()
        with conn.cursor() as cur:
            # Get ALL weather data entries (non-sim sources including NULL)
            cur.execute("""
                SELECT timestamp, temperature, humidity, irradiance, wind_speed, source
                FROM sensor_data
                WHERE source != 'sim' OR source IS NULL
                ORDER BY timestamp DESC
            """)
            rows = cur.fetchall()
        conn.close()

        if not rows:
            return jsonify({
                'success': False,
                'error': 'No weather data found in database'
            }), 404

        # Format data for JSON response
        weather_data = []
        for row in rows:
            weather_data.append({
                'timestamp': row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else '',
                'temperature': float(row[1]) if row[1] else 0.0,
                'humidity': float(row[2]) if row[2] else 0.0,
                'irradiance': float(row[3]) if row[3] else 0.0,
                'wind_speed': float(row[4]) if row[4] else 0.0,
                'source': row[5] if row[5] else 'Database'
            })

        # Get summary information
        summary = get_weather_summary()

        # Update collect2.txt with the fetched data
        data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'collect2.txt')
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(data_file_path, 'w') as f:
            f.write(f'# Data collection last updated: {current_timestamp}\n')
            if summary:
                f.write(f'# Summary: weather={summary["total_rows"]}\n')
            f.write('[weather]\n')
            f.write('timestamp,temperature,humidity,irradiance,wind_speed,source\n')
            for row in rows:
                timestamp_str = row[0].strftime('%Y-%m-%d %H:%M:%S') if row[0] else current_timestamp
                f.write(f'{timestamp_str},{row[1] or 0.0},{row[2] or 0.0},{row[3] or 0.0},{row[4] or 0.0},{row[5] or "Database"}\n')

        logger.info(f"Weather data fetched and collect2.txt updated: {len(rows)} rows")

        return jsonify({
            'success': True,
            'rows_fetched': len(rows),
            'data': weather_data,
            'summary': summary,
            'message': f'Weather data fetched and collect2.txt updated with {len(rows)} rows'
        })

    except Exception as e:
        logger.error(f"Failed to fetch weather data from database: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/fetch_openweather', methods=['POST'])
def fetch_openweather():
    """Fetch data from OpenWeather API"""
    try:
        logger.info("Fetching data from OpenWeather API")

        # Fetch weather data from OpenWeather API (10 rows from past 2 days)
        weather_fetched = False
        weather_data_list = []
        try:
            # Fetch 10 weather data points from past 2 days
            for i in range(10):
                weather_data = fetch_weather_data()
                if weather_data:
                    weather_data_list.append(weather_data)
                    weather_fetched = True
                    logger.info(f"Weather data {i+1} fetched successfully")
                    time.sleep(1)  # Rate limiting
                else:
                    logger.warning(f"Weather data {i+1} fetch returned None")
            logger.info(f"Total weather data points fetched: {len(weather_data_list)}")
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return jsonify({
                'success': False,
                'error': f'Failed to fetch weather data: {str(e)}'
            }), 500

        # Insert weather data if fetched (all 10 rows)
        weather_rows_inserted = 0
        if weather_fetched and weather_data_list:
            try:
                conn = get_connection()
                for weather_data in weather_data_list:
                    insert_weather_data(conn, weather_data)
                    weather_rows_inserted += 1
                conn.close()
                logger.info(f"Weather data inserted into database: {weather_rows_inserted} rows")
            except Exception as e:
                logger.error(f"Failed to insert weather data: {e}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to insert weather data: {str(e)}'
                }), 500

        return jsonify({
            'success': True,
            'weather_fetched': weather_fetched,
            'weather_rows_inserted': weather_rows_inserted,
            'weather_data_points': len(weather_data_list)
        })

    except Exception as e:
        logger.error(f"OpenWeather API fetch failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/data/collect1.txt', methods=['GET'])
def serve_collect1():
    """Serve the collect1.txt file (sim data)"""
    try:
        data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'collect1.txt')
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain'}
        else:
            return 'File not found', 404
    except Exception as e:
        logger.error(f"Failed to serve collect1.txt: {e}")
        return 'Error serving file', 500

@app.route('/data/collect2.txt', methods=['GET'])
def serve_collect2():
    """Serve the collect2.txt file (nasa_power data)"""
    try:
        data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'collect2.txt')
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain'}
        else:
            return 'File not found', 404
    except Exception as e:
        logger.error(f"Failed to serve collect2.txt: {e}")
        return 'Error serving file', 500

@app.route('/data/collect3.txt', methods=['GET'])
def serve_collect3():
    """Serve the collect3.txt file (openweather data)"""
    try:
        data_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'collect3.txt')
        if os.path.exists(data_file_path):
            with open(data_file_path, 'r') as f:
                content = f.read()
            return content, 200, {'Content-Type': 'text/plain'}
        else:
            return 'File not found', 404
    except Exception as e:
        logger.error(f"Failed to serve collect3.txt: {e}")
        return 'Error serving file', 500

@app.route('/trigger_ingestion', methods=['POST'])
def trigger_ingestion():
    """Endpoint to trigger manual data ingestion"""
    logger.info("Manual ingestion triggered - starting process")

    try:
        # Initialize response data
        response_data = {
            'success': False,
            'sensor_generated': False,
            'weather_fetched': False,
            'weather_rows_inserted': 0,
            'solar_fetched': False,
            'solar_rows_inserted': 0,
            'ingestion_result': {},
            'error': None
        }

        # Step 1: Generate simulated sensor data
        logger.info("Step 1: Generating simulated sensor data")
        try:
            sensor_data = generate_sensor_data()
            response_data['sensor_generated'] = True
            logger.info("Sensor data generated successfully")
        except Exception as e:
            logger.error(f"Failed to generate sensor data: {e}")
            response_data['error'] = f"Sensor generation failed: {str(e)}"
            return jsonify(response_data), 500

        # Step 2: Fetch weather data from OpenWeather API (10 rows)
        logger.info("Step 2: Fetching weather data from OpenWeather API")
        weather_data_list = []
        try:
            for i in range(10):
                logger.info(f"Fetching weather data point {i+1}/10")
                weather_data = fetch_weather_data()
                if weather_data:
                    weather_data_list.append(weather_data)
                    logger.info(f"Weather data {i+1} fetched successfully")
                else:
                    logger.warning(f"Weather data {i+1} fetch returned None")
                time.sleep(1)  # Rate limiting

            if weather_data_list:
                response_data['weather_fetched'] = True
                logger.info(f"Total weather data points fetched: {len(weather_data_list)}")
            else:
                logger.warning("No weather data fetched")
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            response_data['error'] = f"Weather fetch failed: {str(e)}"
            return jsonify(response_data), 500

        # Step 3: Fetch solar irradiance data from NASA POWER API (10 rows)
        logger.info("Step 3: Fetching solar irradiance data from NASA POWER API")
        solar_data_list = []
        try:
            for i in range(10):
                logger.info(f"Fetching solar irradiance data point {i+1}/10")
                solar_data = get_solar_irradiance_data()
                if solar_data:
                    solar_data_list.append(solar_data)
                    logger.info(f"Solar irradiance data {i+1} fetched successfully")
                else:
                    logger.warning(f"Solar irradiance data {i+1} fetch returned None")
                time.sleep(0.5)  # Rate limiting

            if solar_data_list:
                response_data['solar_fetched'] = True
                logger.info(f"Total solar irradiance data points fetched: {len(solar_data_list)}")
            else:
                logger.warning("No solar irradiance data fetched")
        except Exception as e:
            logger.error(f"Failed to fetch solar irradiance data: {e}")
            response_data['error'] = f"Solar fetch failed: {str(e)}"
            return jsonify(response_data), 500

        # Step 4: Run database ingestion
        logger.info("Step 4: Running database ingestion")
        try:
            ingestion_result = run_ingestion()
            response_data['ingestion_result'] = ingestion_result or {}
            logger.info("Database ingestion completed")
        except Exception as e:
            logger.error(f"Database ingestion failed: {e}")
            response_data['error'] = f"Database ingestion failed: {str(e)}"
            return jsonify(response_data), 500

        # Step 5: Insert weather data if fetched
        logger.info("Step 5: Inserting weather data into database")
        if response_data['weather_fetched'] and weather_data_list:
            try:
                conn = get_connection()
                for weather_data in weather_data_list:
                    insert_weather_data(conn, weather_data)
                    response_data['weather_rows_inserted'] += 1
                conn.close()
                logger.info(f"Weather data inserted into database: {response_data['weather_rows_inserted']} rows")
            except Exception as e:
                logger.error(f"Failed to insert weather data: {e}")
                response_data['error'] = f"Weather data insertion failed: {str(e)}"
                return jsonify(response_data), 500

        # Step 6: Insert solar data if fetched
        logger.info("Step 6: Inserting solar irradiance data into database")
        if response_data['solar_fetched'] and solar_data_list:
            try:
                conn = get_connection()
                for i, solar_data in enumerate(solar_data_list):
                    # Create a combined entry with solar irradiance
                    timestamp, irradiance = solar_data
                    # Try to use corresponding weather data if available
                    if i < len(weather_data_list):
                        ts, temp, hum, _, wind = weather_data_list[i]
                        combined_data = (ts, temp, hum, irradiance, wind)
                    else:
                        # Create minimal entry with just timestamp and irradiance
                        combined_data = (timestamp, 0.0, 0.0, irradiance, 0.0)

                    insert_weather_data(conn, combined_data)
                    response_data['solar_rows_inserted'] += 1
                conn.close()
                logger.info(f"Solar irradiance data inserted into database: {response_data['solar_rows_inserted']} rows")
            except Exception as e:
                logger.error(f"Failed to insert solar irradiance data: {e}")
                response_data['error'] = f"Solar data insertion failed: {str(e)}"
                return jsonify(response_data), 500

        # Success response
        response_data['success'] = True
        logger.info("Manual ingestion completed successfully")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Ingestion trigger failed with unexpected error: {e}")
        return jsonify({
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'sensor_generated': False,
            'weather_fetched': False,
            'weather_rows_inserted': 0,
            'solar_fetched': False,
            'solar_rows_inserted': 0,
            'ingestion_result': {}
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
