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
├── README.md             # Documentation for setup and usage
├── config.py             # Configuration settings (API keys, database credentials)
├── requirements.txt      # List of Python dependencies
│
├── api_wrappers/         # External API integration modules
│   ├── openweather.py    # OpenWeather API wrapper for weather data
│   └── nasa_power.py     # NASA POWER API wrapper for solar irradiance data
│
├── data/                 # Data files and logs
│   ├── sensor_logs.txt   # Plain text sensor log file
│   └── sensor_data.csv   # CSV file for sensor data
│
├── db/                   # Database setup and connectors
│   ├── db_connector.py   # Python script for DB connection
│   ├── db_ingest.py      # Data ingestion script
│   ├── test_connection.py # Quick connection test script
│   ├── schema.sql        # SQL table definitions
│   ├── sensor_stream_sim.py # Sensor stream simulation
│   └── api_ingest_openweather.py # OpenWeather API ingestion
│
├── docs/                 # Documentation and notes
│   ├── myNotes.txt       # Development notes and progress logs
│   └── TODO.md           # Task list and project roadmap
│
├── logs/                 # Log files
│   ├── ingestion.log     # Today's ingestion log
│   ├── ingestion.log.2026-01-20 # Yesterday's log (auto-rotated)
│   └── ingestion.log.2026-01-26 # Older log (auto-rotated)
│
├── notebooks/            # Jupyter notebooks for demos
│   └── data_pipeline_demo.py # Step-by-step interactive demo
│
├── preprocessing/        # Data cleaning and preprocessing scripts
│   └── preprocess.py     # Normalize and clean sensor logs
│
├── scripts/              # Utility scripts
│   ├── capture_weather_data.py # Automated weather data capture
│   ├── show_recent_data.py     # Display recent sensor data
│   └── run_ingest.bat          # Batch file for scheduled ingestion
│
├── sensors/              # Sensor data scripts
│   └── sensor_ingest.py  # Generate or simulate sensor readings
│
├── tests/                # Testing and validation scripts
│   ├── check_schema.py   # Schema validation
│   └── test_imports.py   # Import testing
│
└── web/                  # Web-related files
    ├── dashboard.py      # Streamlit dashboard
    ├── generate_html_table.py # HTML table generation
    ├── ingestion_trigger.py   # Flask endpoint for ingestion
    └── solar_wind_display.html # HTML interface for data display
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

---

## 📋 Project Phases

The project is organized into phases for systematic development. Below is the latest status of all phases with detailed sub-steps:

### Phase 1: Environment Setup ✅ Done
- Install PostgreSQL portable binaries
- Initialize database cluster (initdb)
- Start PostgreSQL manually (pg_ctl)
- Connect with psql

### Phase 2: Database Schema ✅ Done
- Create energy_db database
- Define sensor_data table schema
- Verify schema with \d sensor_data

### Phase 3: Python Integration ✅ Done
- Install psycopg2 driver
- Create db_ingest.py script
- Connect Python to PostgreSQL
- Insert test row via Python
- Fetch and display rows via Python

### Phase 4: Log Ingestion ✅ Done
- Adapt script to read sensor_logs.txt
- Insert multiple rows from file
- Verify ingestion with query output

### Phase 5: Enhancements ✅ Done
- Handle duplicate entries (unique timestamp + ON CONFLICT)
- Format timestamp output (seconds only)
- Optional: pretty table output
- Row count before/after ingestion
- Skip header line in text ingestion
- Modularize connection into db_connector.py
- Add test_connection.py script
- Show top/bottom rows in test script

### Phase 6: Next Steps ✅ Done
- Automate ingestion (batch file or cron job)
- Extend ingestion for CSV/real sensor streams
- Dashboard/visualization integration
- Add permanent log file output (logs/ingestion.log)
- Daily log rotation (TimedRotatingFileHandler)

### Phase 7: Visualization & Dashboard ✅ Done
- Plot temperature vs timestamp chart
- Add multiple charts (humidity, irradiance, wind speed)
- Build simple dashboard (Streamlit with sidebar)

### Phase 8: Real-Time Ingestion 🔄 Partial
- Simulate sensor streams (append rows every minute) ✅ Done
- Implement manual trigger for on-demand ingestion ✅ Done
- Enable continuous ingestion pipeline ⏳ Pending

### Phase 9: Predictive Analytics ⏳ Pending
- Calculate averages/min/max/moving averages
- Train ML model for forecasting (scikit-learn)

### Phase 10: Deployment & Scaling ⏳ Pending
- Containerize with Docker
- Deploy to cloud (AWS/Azure/GCP)

### Phase 11: Web-Sensor Data Integration 🔄 Partial
- Connect to OpenWeather API for local weather data ✅ Done
- Ingest NASA POWER API for solar irradiance and climate data ✅ Done
- Integrate PVOutput API for solar PV system performance ⏳ Pending
- Optional: Add other APIs (NOAA, Meteostat, etc.) ⏳ Pending
- Normalize and store web-sensor data into sensor_data table ✅ Done
- Combine local sensor + web API data for richer analytics ⏳ Pending
