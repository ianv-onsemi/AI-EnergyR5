#!/usr/bin/env python3
"""
Script to clean the database by retaining only sim data
"""

import sys
import os

# Add db directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'db'))

from db_connector import get_connection

def clean_database():
    """Remove all non-sim data from the database"""
    try:
        conn = get_connection()

        # Count rows before cleaning
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sensor_data")
            total_before = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source = 'sim'")
            sim_before = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM sensor_data WHERE source != 'sim' OR source IS NULL")
            non_sim_before = cur.fetchone()[0]

        print(f"Before cleaning: Total={total_before}, Sim={sim_before}, Non-sim={non_sim_before}")

        # Delete non-sim data
        with conn.cursor() as cur:
            cur.execute("DELETE FROM sensor_data WHERE source != 'sim' OR source IS NULL")
            deleted_count = cur.rowcount
        conn.commit()

        # Count rows after cleaning
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM sensor_data")
            total_after = cur.fetchone()[0]

        conn.close()

        print(f"After cleaning: Total={total_after}, Deleted={deleted_count}")
        print("Database cleaned successfully - only sim data retained")

    except Exception as e:
        print(f"Error cleaning database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    clean_database()
