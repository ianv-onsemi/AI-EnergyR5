# AI-EnergyR5
AI-Driven Predictive Maintenance for Renewable Energy Assets 
# AI-Driven Predictive Maintenance for Renewable Energy Assets

This project develops a cross-platform application for predictive maintenance of renewable energy assets (wind turbines, solar panels, inverters, batteries). It uses IoT sensor data, external weather/solar APIs, and AI/ML models to forecast failures and optimize maintenance schedules.

---

## 🚀 Features
- Real-time sensor data ingestion (temperature, humidity, irradiance, wind speed).
- External API integration (OpenWeather, NASA POWER, Tomorrow.io).
- Local PostgreSQL + TimescaleDB storage for time-series data.
- Preprocessing scripts for normalization, cleaning, and interpolation.
- Ready for deployment on Raspberry Pi 4, but fully compatible with Mac and Windows laptops during development.

---

## 🛠️ Development Setup

### 1. Clone Repository
```bash
AI-EnergyR5/
│
├── db/                     # Database setup and connectors
│   ├── db_connector.py     # Python script to handles DB connection
│   ├── db_ingest.py        # Python script to ingestion script (imports connector)
│   ├── test_connection.py  # Python script for quick connection test
│   └── schema.sql          # SQL table definitions
│
├── data/
│   ├── sensor_logs.txt   # plain text log file
│   └── sensor_data.csv   # CSV file
│
├── .env
├── requirements.txt      # List of Python dependencies
├── README.md             # Documentation for setup and usage
├── logs/
│   └── ingestion.log         # today's log
│   └── ingestion.log.2026-01-20  # yesterday's log, auto-created at midnight
│
├── sensors/              # Scripts for sensor data (real or simulated)
│   └── sensor_ingest.py  # First script: generate or simulate sensor readings
│
├── api_wrappers/         # External API modules
│   └── openweather.py    # First wrapper: fetch weather data
│   └── nasa_power.py     # Second wrapper: fetch solar/irradiance data
│
├── preprocessing/        # Data cleaning scripts
│   └── preprocess.py     # First script: normalize and clean sensor logs
│
└── notebooks/            # Jupyter notebooks for demos
    └── data_pipeline_demo.ipynb  # Step-by-step interactive demo
```

### 2. PostgreSQL Database Management

This project uses PostgreSQL as the database backend. Follow these steps to turn PostgreSQL on and off:

#### Turn PostgreSQL On (Start the Server)
1. **Open Command Prompt Window**:
   - Press `Win + R`, type `cmd`, and press Enter
   - Or search for "Command Prompt" in the Start menu

2. **Navigate to PostgreSQL Bin Directory**:
   - In the Command Prompt window, type the following command and press Enter:
     ```
     cd "D:\My Documents\tools\postgresql\pgsql\bin"
     ```

3. **Start PostgreSQL Server**:
   - In the same Command Prompt window, type the following command and press Enter:
     ```
     pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" -l logfile start
     ```
   - This starts PostgreSQL in the background on port 5432
   - You should see a message indicating the server is starting
   - The server will continue running until manually stopped

4. **Verify PostgreSQL is Running** (Optional):
   - In the same Command Prompt window, type the following command and press Enter:
     ```
     pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" status
     ```
   - Should show: "pg_ctl: server is running (PID: XXXX)"

#### Turn PostgreSQL Off (Stop the Server)
1. **Open Command Prompt Window**:
   - Press `Win + R`, type `cmd`, and press Enter
   - Or search for "Command Prompt" in the Start menu

2. **Navigate to PostgreSQL Bin Directory**:
   - In the Command Prompt window, type the following command and press Enter:
     ```
     cd "D:\My Documents\tools\postgresql\pgsql\bin"
     ```

3. **Stop PostgreSQL Server**:
   - In the same Command Prompt window, type the following command and press Enter:
     ```
     pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" stop
     ```
   - This performs a clean shutdown of the database server
   - You should see a message indicating the server is stopping

#### Notes
- PostgreSQL must be running before you can connect to the database from Python scripts
- The database connection settings are configured in `db/db_connector.py` with default values:
  - Host: `localhost`
  - Port: `5432`
  - Database: `energy_db`
  - User: `postgres`
  - Password: `PdM`
- To test the database connection, run: `python db/test_connection.py`

#### Notes

For detailed development notes and progress logs, refer to `mynotes.txt`.
