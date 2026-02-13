#!/usr/bin/env python3
"""Check table structure"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db.db_connector import get_connection

def check_structure():
    conn = get_connection()
    cur = conn.cursor()
    
    # Check table structure
    cur.execute("""SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'sensor_data'""")
    columns = cur.fetchall()
    print('Table columns:')
    for col in columns:
        print(f'  {col[0]}: {col[1]}')
    
    # Check constraints
    cur.execute("""SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'sensor_data'::regclass""")
    constraints = cur.fetchall()
    print('\nConstraints:')
    for con in constraints:
        print(f'  {con[0]}: {con[1]}')
    
    conn.close()

if __name__ == "__main__":
    check_structure()
