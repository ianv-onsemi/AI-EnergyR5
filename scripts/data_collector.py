import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from db.db_connector import get_connection

def validate_data_row(row, expected_length=5):
    """Validate data row format and content"""
    try:
        if len(row) != expected_length:
            return False

        # Handle different column layouts
        if expected_length == 9:  # Database schema: id,timestamp,temp,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield
            # Validate id (integer)
            int(row[0])
            # Validate timestamp format (second column)
            datetime.fromisoformat(row[1].replace(' ', 'T'))
            # Validate numeric fields (columns 2-5, 7-8), allowing blank strings for not-applicable
            for i in [2, 3, 4, 5, 7, 8]:  # temperature, humidity, irradiance, wind_speed, wind_power_density, solar_energy_yield
                val = row[i]
                if val != '':  # Allow blank strings
                    float(val)
            # Source column (index 6) can be any string
        elif expected_length == 6:  # Weather/NASA data: timestamp,temp,humidity,irradiance,wind_speed,source
            # Validate timestamp format
            datetime.fromisoformat(row[0].replace(' ', 'T'))
            # Validate numeric fields (skip source column)
            for i in range(1, 5):
                float(row[i])
        else:  # Legacy 5-column format
            # Validate timestamp format
            datetime.fromisoformat(row[0].replace(' ', 'T'))
            # Validate all numeric fields
            for i in range(1, expected_length):
                float(row[i])

        return True
    except (ValueError, IndexError, TypeError) as e:
        logger.debug(f"Validation error for row {row}: {e}")
        return False

def write_data_file(file_path, section_name, header, data_rows):
    """Write data to file with error handling"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'# Data collection last updated: {current_timestamp}\n')

            # Dynamically calculate summary
            actual_row_count = len(data_rows)
            f.write(f'# Summary: {section_name.lower()}={actual_row_count}\n')
            f.write(f'[{section_name}]\n')
            f.write(header + '\n')

            rows_written = 0
            for row in data_rows:
                try:
                    if validate_data_row(row, expected_length=len(header.split(','))):
                        f.write(','.join(str(x) for x in row) + '\n')
                        rows_written += 1
                    else:
                        logger.warning(f"Skipping invalid row: {row}")
                except Exception as write_error:
                    logger.warning(f"Failed to write row {row}: {write_error}")
                    continue

            logger.info(f"Successfully wrote {rows_written} rows to {file_path}")
            return True

    except IOError as file_error:
        logger.error(f"Failed to write to {file_path}: {file_error}")
        return False

def collect_sim_data():
    """Collect only sim data from sensor_logs.txt and database with complete database headers"""
    logger.info("Collecting sim data with complete database headers")

    # Get existing timestamps to avoid duplicates
    existing_timestamps = set()
    collection_file = 'data/collect1.txt'

    if os.path.exists(collection_file):
        try:
            with open(collection_file, 'r', encoding='utf-8') as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if line == '[sim]':
                        current_section = 'sim'
                    elif line.startswith('#') or not line:
                        continue
                    elif current_section == 'sim' and ',' in line and not line.startswith('id,'):
                        parts = line.split(',')
                        if len(parts) >= 2:  # Check timestamp in second column
                            existing_timestamps.add(parts[1])  # timestamp is second column now
        except Exception as e:
            logger.warning(f"Error reading existing file: {e}")

    # Collect sim data from sensor_logs.txt (legacy format - map to complete schema)
    sim_data = []
    sensor_logs_path = 'data/sensor_logs.txt'

    if os.path.exists(sensor_logs_path):
        try:
            with open(sensor_logs_path, 'r', encoding='utf-8') as f:
                row_number = 1
                for line in f:
                    line = line.strip()
                    if line and not line.lower().startswith('timestamp'):
                        parts = line.split(',')
                        if len(parts) == 5 and parts[0] not in existing_timestamps:
                            # Map legacy 5-column format to complete 9-column database schema
                            data_tuple = (
                                row_number,  # id (row number)
                                parts[0],    # timestamp
                                float(parts[1]) if parts[1] else 0.0,  # temperature
                                float(parts[2]) if parts[2] else 0.0,  # humidity
                                float(parts[3]) if parts[3] else 0.0,  # irradiance
                                float(parts[4]) if parts[4] else 0.0,  # wind_speed
                                'sim',       # source
                                '',          # wind_power_density - not available (blank)
                                ''           # solar_energy_yield - not available (blank)
                            )
                            if validate_data_row(data_tuple, expected_length=9):
                                sim_data.append(data_tuple)
                                existing_timestamps.add(parts[0])
                                row_number += 1
        except Exception as e:
            logger.error(f"Error reading sensor logs: {e}")

    # Collect additional sim data from database (complete schema)
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield
                    FROM sensor_data
                    WHERE source = 'sim'
                    ORDER BY timestamp
                """)
                rows = cur.fetchall()
            conn.close()

            for row in rows:
                timestamp_str = row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else ''
                if timestamp_str and timestamp_str not in existing_timestamps:
                    data_tuple = (
                        row[0] if row[0] is not None else 0,  # id
                        timestamp_str,  # timestamp
                        row[2] if row[2] is not None else 0.0,  # temperature
                        row[3] if row[3] is not None else 0.0,  # humidity
                        row[4] if row[4] is not None else 0.0,  # irradiance
                        row[5] if row[5] is not None else 0.0,  # wind_speed
                        row[6] if row[6] else 'sim',  # source
                        row[7] if row[7] is not None else '',  # wind_power_density (blank if None)
                        row[8] if row[8] is not None else ''   # solar_energy_yield (blank if None)
                    )
                    if validate_data_row(data_tuple, expected_length=9):
                        sim_data.append(data_tuple)
                        existing_timestamps.add(timestamp_str)
    except Exception as e:
        logger.error(f"Error fetching sim data from database: {e}")

    # Sort data by timestamp (second column)
    sim_data.sort(key=lambda x: x[1])

    # Write to collect1.txt with complete database headers
    header = 'id,timestamp,temperature,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield'
    success = write_data_file(collection_file, 'sim', header, sim_data)

    if success:
        logger.info(f"Sim data collection completed: {len(sim_data)} rows with complete database headers")
    else:
        logger.error("Failed to write sim data to file")

    return success

def collect_weather_data():
    """Collect weather data (OpenWeather) to collect2.txt with same format as sim data"""
    logger.info("Collecting weather data with complete database headers")

    weather_data = []
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cur:
                # Get weather data (non-sim sources) with all columns
                cur.execute("""
                    SELECT id, timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield
                    FROM sensor_data
                    WHERE source != 'sim' OR source IS NULL
                    ORDER BY timestamp
                """)
                rows = cur.fetchall()
            conn.close()

            for row in rows:
                timestamp_str = row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else ''
                if timestamp_str:
                    # Mirror the database structure with blank for not applicable
                    data_tuple = (
                        row[0] if row[0] is not None else 0,  # id
                        timestamp_str,  # timestamp
                        row[2] if row[2] is not None else 0.0,  # temperature
                        row[3] if row[3] is not None else 0.0,  # humidity
                        row[4] if row[4] is not None else 0.0,  # irradiance
                        row[5] if row[5] is not None else 0.0,  # wind_speed
                        row[6] if row[6] else 'openweather',  # source
                        row[7] if row[7] is not None else '',  # wind_power_density (blank if None)
                        row[8] if row[8] is not None else ''   # solar_energy_yield (blank if None)
                    )
                    if validate_data_row(data_tuple, expected_length=9):
                        weather_data.append(data_tuple)
    except Exception as e:
        logger.error(f"Error fetching weather data from database: {e}")

    # Write to collect2.txt with same header as collect1.txt
    header = 'id,timestamp,temperature,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield'
    success = write_data_file('data/collect2.txt', 'weather', header, weather_data)

    if success:
        logger.info(f"Weather data collection completed: {len(weather_data)} rows with complete database headers")
    else:
        logger.error("Failed to write weather data to file")

    return success

def collect_nasa_data():
    """Collect NASA POWER data to collect3.txt with same format as sim and weather data"""
    logger.info("Collecting NASA POWER data with complete database headers")

    nasa_data = []
    try:
        conn = get_connection()
        if conn:
            with conn.cursor() as cur:
                # Get NASA data (high irradiance values) with all columns
                cur.execute("""
                    SELECT id, timestamp, temperature, humidity, irradiance, wind_speed, source, wind_power_density, solar_energy_yield
                    FROM sensor_data
                    WHERE irradiance > 100 AND (source = 'nasa_power' OR source IS NULL)
                    ORDER BY timestamp
                """)
                rows = cur.fetchall()
            conn.close()

            for row in rows:
                timestamp_str = row[1].strftime('%Y-%m-%d %H:%M:%S') if row[1] else ''
                if timestamp_str:
                    # Mirror the database structure with blank for not applicable
                    data_tuple = (
                        row[0] if row[0] is not None else 0,  # id
                        timestamp_str,  # timestamp
                        row[2] if row[2] is not None else 0.0,  # temperature
                        row[3] if row[3] is not None else 0.0,  # humidity
                        row[4] if row[4] is not None else 0.0,  # irradiance
                        row[5] if row[5] is not None else 0.0,  # wind_speed
                        row[6] if row[6] else 'nasa_power',  # source
                        row[7] if row[7] is not None else '',  # wind_power_density (blank if None)
                        row[8] if row[8] is not None else ''   # solar_energy_yield (blank if None)
                    )
                    if validate_data_row(data_tuple, expected_length=9):
                        nasa_data.append(data_tuple)
    except Exception as e:
        logger.error(f"Error fetching NASA data from database: {e}")

    # Write to collect3.txt with same header as collect1.txt and collect2.txt
    header = 'id,timestamp,temperature,humidity,irradiance,wind_speed,source,wind_power_density,solar_energy_yield'
    success = write_data_file('data/collect3.txt', 'nasa_power', header, nasa_data)

    if success:
        logger.info(f"NASA data collection completed: {len(nasa_data)} rows with complete database headers")
    else:
        logger.error("Failed to write NASA data to file")

    return success

def collect_data():
    """Main function to collect all data types separately"""
    logger.info("Starting data collection process")

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Collect each data type to separate files
    sim_success = collect_sim_data()
    weather_success = collect_weather_data()
    nasa_success = collect_nasa_data()

    if sim_success and weather_success and nasa_success:
        logger.info("All data collection completed successfully")
        print("Data collection completed successfully")
    else:
        logger.warning("Some data collection operations failed")
        print("Data collection completed with warnings")

if __name__ == '__main__':
    collect_data()
