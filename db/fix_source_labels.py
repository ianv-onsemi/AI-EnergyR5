#!/usr/bin/env python3
"""
Fix source labels for existing sensor_data rows.
Updates NULL source rows to appropriate source values based on data patterns.
"""

import sys
import os
import psycopg2
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.db_connector import get_connection


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def fix_source_labels():
    """Update existing rows with NULL or empty source to proper source labels."""
    conn = get_connection()
    
    try:
        with conn.cursor() as cur:
            # First, let's see what we have
            cur.execute("SELECT source, COUNT(*) FROM sensor_data GROUP BY source;")
            results = cur.fetchall()
            logger.info("Current source distribution:")
            for source, count in results:
                source_str = source if source else "NULL/Empty"
                logger.info(f"  - {source_str}: {count} rows")
            
            # Count rows with NULL source
            cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source IS NULL;")
            null_count = cur.fetchone()[0]
            logger.info(f"\nRows with NULL source: {null_count}")
            
            if null_count == 0:
                logger.info("No NULL source rows to fix.")
                return
            
            # Strategy: 
            # 1. Rows with irradiance > 0 and NULL source -> nasa_power
            # 2. Rows with temperature/humidity and NULL source -> openweather
            # 3. Remaining NULL rows -> openweather (default)
            
            # Update rows with significant irradiance to nasa_power
            cur.execute("""
                UPDATE sensor_data 
                SET source = 'nasa_power'
                WHERE source IS NULL 
                AND irradiance > 0;
            """)
            nasa_updated = cur.rowcount
            logger.info(f"Updated {nasa_updated} rows to 'nasa_power' (have irradiance > 0)")
            
            # Update remaining NULL rows to openweather
            cur.execute("""
                UPDATE sensor_data 
                SET source = 'openweather'
                WHERE source IS NULL;
            """)
            openweather_updated = cur.rowcount
            logger.info(f"Updated {openweather_updated} rows to 'openweather' (default for weather data)")
            
            conn.commit()
            
            # Show final distribution
            cur.execute("SELECT source, COUNT(*) FROM sensor_data GROUP BY source ORDER BY source;")
            final_results = cur.fetchall()
            logger.info("\nFinal source distribution:")
            for source, count in final_results:
                source_str = source if source else "NULL/Empty"
                logger.info(f"  - {source_str}: {count} rows")
                
    except Exception as e:
        logger.error(f"Failed to fix source labels: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_source_labels()
