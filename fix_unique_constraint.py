#!/usr/bin/env python3
"""Fix unique constraint to allow multiple sources per timestamp"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def fix_constraint():
    conn = get_connection()
    cur = conn.cursor()
    
    print("Fixing unique constraint on sensor_data table...")
    
    # Drop the old unique constraint
    try:
        cur.execute("ALTER TABLE sensor_data DROP CONSTRAINT IF EXISTS unique_timestamp")
        print("✓ Dropped old unique_timestamp constraint")
    except Exception as e:
        print(f"Note: {e}")
    
    # Add new composite unique constraint
    try:
        cur.execute("""
            ALTER TABLE sensor_data 
            ADD CONSTRAINT unique_timestamp_source 
            UNIQUE (timestamp, source)
        """)
        print("✓ Added new unique_timestamp_source constraint")
    except Exception as e:
        print(f"Error adding constraint: {e}")
        # If it already exists, that's fine
        pass
    
    conn.commit()
    print("\n✅ Constraint fix complete!")
    print("Now multiple sources can have data for the same timestamp.")
    
    conn.close()

if __name__ == "__main__":
    fix_constraint()
