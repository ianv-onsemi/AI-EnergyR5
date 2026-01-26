from db_connector import get_connection
from tabulate import tabulate   # for pretty tables

def main():
    # Step 1: Connect to DB
    conn = get_connection()

    try:
        with conn.cursor() as cur:
            # Step 2: Count rows
            cur.execute("SELECT COUNT(*) FROM sensor_data;")
            result = cur.fetchone()
            print("✅ Database connection test successful!")
            print(f"📊 sensor_data table has {result[0]} rows.")

            # Step 3: Show top 2 rows (earliest timestamps)
            cur.execute("SELECT * FROM sensor_data ORDER BY timestamp ASC LIMIT 2;")
            top_rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            print("\n🔎 Top 2 rows (earliest):")
            print(tabulate(top_rows, headers=headers, tablefmt="psql"))

            # Step 4: Show bottom 2 rows (latest timestamps)
            cur.execute("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 2;")
            bottom_rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            print("\n🔎 Bottom 2 rows (latest):")
            print(tabulate(bottom_rows, headers=headers, tablefmt="psql"))

    except Exception as e:
        print(f"❌ Query failed: {e}")

    # Step 5: Close connection
    conn.close()

if __name__ == "__main__":
    main()
