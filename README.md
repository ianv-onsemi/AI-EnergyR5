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

#### my notes
'''bash
Perfect 🎉 — that package list shows your environment is now fully set up and healthy. You’ve got all the core libraries installed:
requests → API calls and HTTP requests
pandas → data handling and analysis
numpy → numerical computations
psycopg2-binary → PostgreSQL connector
scikit-learn → classical machine learning models
torch → PyTorch deep learning framework
matplotlib → static plotting
plotly → interactive charts
paho-mqtt → IoT sensor communication
Plus all their dependencies (like scipy, joblib, threadpoolctl, etc.). This means you’re ready to start coding your actual project.
PS D:\My Documents\tools\skul\bsu2024\bsu_mot512_thesis1\GithubVisualStudioCode\AI-EnergyForcastR4> python -m pip list
Package            Version
------------------ -----------
certifi            2026.1.4
charset-normalizer 3.4.4
contourpy          1.3.3
cycler             0.12.1
filelock           3.20.3
fonttools          4.61.1
fsspec             2026.1.0
idna               3.11
Jinja2             3.1.6
joblib             1.5.3
kiwisolver         1.4.9
MarkupSafe         3.0.3
matplotlib         3.10.8
mpmath             1.3.0
narwhals           2.15.0
networkx           3.6.1
numpy              2.4.1
packaging          25.0
paho-mqtt          2.1.0
pandas             2.3.3
pillow             12.1.0
pip                25.3
plotly             6.5.2
psycopg2-binary    2.9.11
pyparsing          3.3.1
python-dateutil    2.9.0.post0
pytz               2025.2
requests           2.32.5
scikit-learn       1.8.0
scipy              1.17.0
setuptools         80.9.0
six                1.17.0
sympy              1.14.0
threadpoolctl      3.6.0
torch              2.9.1
typing_extensions  4.15.0
tzdata             2025.3
urllib3            2.6.3

[always used for activating env; "venv\Scripts\activate.bat"]
[This starts PostgreSQL in the background, listening on port 5432.
Since you don’t have admin rights, it won’t be a Windows service — you’ll need to run this manually each time.
in <cmd> <"D:\My Documents\tools\postgresql\pgsql\bin\pg_ctl.exe" -D "D:\My Documents\tools\postgresql\pgsql\data" -l logfile start>]
[Stopping PostgreSQL. When you’re done, stop the server cleanly, This shuts down PostgreSQL safely:
in cmd> <"D:\My Documents\tools\postgresql\pgsql\bin\pg_ctl.exe" -D "D:\My Documents\tools\postgresql\pgsql\data" stop>]
[Restarting PostgreSQL, If you want to restart:
in cmd> <"D:\My Documents\tools\postgresql\pgsql\bin\pg_ctl.exe" -D "D:\My Documents\tools\postgresql\pgsql\data" restart>]

...notes 2026-jan-19;
Phase,Item,Status
Phase 1: Environment Setup,Install PostgreSQL portable binaries,Done
Phase 1: Environment Setup,Initialize database cluster (initdb),Done
Phase 1: Environment Setup,Start PostgreSQL manually (pg_ctl),Done
Phase 1: Environment Setup,Connect with psql,Done
Phase 2: Database Schema,Create energy_db database,Done
Phase 2: Database Schema,Define sensor_data table schema,Done
Phase 2: Database Schema,Verify schema with \d sensor_data,Done
Phase 3: Python Integration,Install psycopg2 driver,Done
Phase 3: Python Integration,Create db_ingest.py script,Done
Phase 3: Python Integration,Connect Python to PostgreSQL,Done
Phase 3: Python Integration,Insert test row via Python,Done
Phase 3: Python Integration,Fetch and display rows via Python,Done
Phase 4: Log Ingestion,Adapt script to read sensor_logs.txt,Done
Phase 4: Log Ingestion,Insert multiple rows from file,Done
Phase 4: Log Ingestion,Verify ingestion with query output,Done
Phase 5: Enhancements,Handle duplicate entries (unique timestamp + ON CONFLICT),Done
Phase 5: Enhancements,Format timestamp output (seconds only),Done
Phase 5: Enhancements,Optional: pretty table output,Pending
Phase 6: Next Steps,Automate ingestion (batch file or cron job),Pending
Phase 6: Next Steps,Extend ingestion for CSV/real sensor streams,Pending
Phase 6: Next Steps,Dashboard/visualization integration,Pending

...notes 2026-jan-20;
sql password = PdM
Phase,Item,Status
Phase 1: Environment Setup,Install PostgreSQL portable binaries,Done
Phase 1: Environment Setup,Initialize database cluster (initdb),Done
Phase 1: Environment Setup,Start PostgreSQL manually (pg_ctl),Done
Phase 1: Environment Setup,Connect with psql,Done
Phase 2: Database Schema,Create energy_db database,Done
Phase 2: Database Schema,Define sensor_data table schema,Done
Phase 2: Database Schema,Verify schema with \d sensor_data,Done
Phase 3: Python Integration,Install psycopg2 driver,Done
Phase 3: Python Integration,Create db_ingest.py script,Done
Phase 3: Python Integration,Connect Python to PostgreSQL,Done
Phase 3: Python Integration,Insert test row via Python,Done
Phase 3: Python Integration,Fetch and display rows via Python,Done
Phase 4: Log Ingestion,Adapt script to read sensor_logs.txt,Done
Phase 4: Log Ingestion,Insert multiple rows from file,Done
Phase 4: Log Ingestion,Verify ingestion with query output,Done
Phase 5: Enhancements,Handle duplicate entries (unique timestamp + ON CONFLICT),Done
Phase 5: Enhancements,Format timestamp output (seconds only),Done
Phase 5: Enhancements,Pretty table output (tabulate),Done
Phase 5: Enhancements,Row count before/after ingestion,Done
Phase 5: Enhancements,Skip header line in text ingestion,Done
Phase 5: Enhancements,Modularize connection into db_connector.py,Done
Phase 5: Enhancements,Add test_connection.py script,Done
Phase 5: Enhancements,Show top/bottom rows in test script,Done
Phase 6: Next Steps,Automate ingestion (batch file or cron job),Pending
Phase 6: Next Steps,Extend ingestion for CSV/real sensor streams,Pending
Phase 6: Next Steps,Dashboard/visualization integration,Pending
Phase 6: Next Steps,Add permanent log file output (logs/ingestion.log),Done
Phase 6: Next Steps,Daily log rotation (TimedRotatingFileHandler),Done
Phase 7: Visualization & Dashboard,Plot temperature vs timestamp chart,Pending
Phase 7: Visualization & Dashboard,Add multiple charts (humidity, irradiance, wind speed),Pending
Phase 7: Visualization & Dashboard,Build simple dashboard (Streamlit or Grafana),Pending
Phase 8: Real-Time Ingestion,Simulate sensor streams (append rows every minute),Pending
Phase 8: Real-Time Ingestion,Enable continuous ingestion pipeline,Pending
Phase 9: Predictive Analytics,Calculate averages/min/max/moving averages,Pending
Phase 9: Predictive Analytics,Train ML model for forecasting (scikit-learn),Pending
Phase 10: Deployment & Scaling,Containerize with Docker,Pending
Phase 10: Deployment & Scaling,Deploy to cloud (AWS/Azure/GCP),Pending
Phase 11: Web-Sensor Data Integration,Connect to OpenWeather API for local weather data,Done
Phase 11: Web-Sensor Data Integration,Ingest NASA POWER API for solar irradiance and climate data,Done
Phase 11: Web-Sensor Data Integration,Integrate PVOutput API for solar PV system performance,Pending
Phase 11: Web-Sensor Data Integration,Optional: Add other APIs (NOAA, Meteostat, etc.),Pending
Phase 11: Web-Sensor Data Integration,Normalize and store web-sensor data into sensor_data table,Done
Phase 11: Web-Sensor Data Integration,Combine local sensor + web API data for richer analytics,Pending
...Phase 6: Automate Ingestion
Step 2: Windows Batch File (simple automation)
    Open Notepad.
    Paste this:
        bat
        @echo off
        cd /d "D:\My Documents\tools\skul\bsu2024\bsu_mot512_thesis1\GithubVisualStudioCode\AI-EnergyForcastR4"
        python db\db_ingest.py
    Save as run_ingest.bat in your repo root.
    Double‑click it → ingestion runs, logs go to logs/ingestion.log.
Step 3: Schedule with Task Scheduler
    Open Task Scheduler (Windows search).
    Create a new task → “Run Ingestion Daily”.
    Set trigger → every day at 4:00 PM.
    Set action → run run_ingest.bat.
    Save → ingestion now runs automatically.

...notes 2026-jan-21;
Phase,Item,Status
Phase 1: Environment Setup,Install PostgreSQL portable binaries,Done
Phase 1: Environment Setup,Initialize database cluster (initdb),Done
Phase 1: Environment Setup,Start PostgreSQL manually (pg_ctl),Done
Phase 1: Environment Setup,Connect with psql,Done
Phase 2: Database Schema,Create energy_db database,Done
Phase 2: Database Schema,Define sensor_data table schema,Done
Phase 2: Database Schema,Verify schema with \d sensor_data,Done
Phase 3: Python Integration,Install psycopg2 driver,Done
Phase 3: Python Integration,Create db_ingest.py script,Done
Phase 3: Python Integration,Connect Python to PostgreSQL,Done
Phase 3: Python Integration,Insert test row via Python,Done
Phase 3: Python Integration,Fetch and display rows via Python,Done
Phase 4: Log Ingestion,Adapt script to read sensor_logs.txt,Done
Phase 4: Log Ingestion,Insert multiple rows from file,Done
Phase 4: Log Ingestion,Verify ingestion with query output,Done
Phase 5: Enhancements,Handle duplicate entries (unique timestamp + ON CONFLICT),Done
Phase 5: Enhancements,Format timestamp output (seconds only),Done
Phase 5: Enhancements,Pretty table output (tabulate),Done
Phase 5: Enhancements,Row count before/after ingestion,Done
Phase 5: Enhancements,Skip header line in text ingestion,Done
Phase 5: Enhancements,Modularize connection into db_connector.py,Done
Phase 5: Enhancements,Add test_connection.py script,Done
Phase 5: Enhancements,Show top/bottom rows in test script,Done
Phase 6: Next Steps,Automate ingestion (batch file or cron job),Done
Phase 6: Next Steps,Extend ingestion for CSV/real sensor streams,Done (simulation script ready)
Phase 6: Next Steps,Dashboard/visualization integration,Done (Streamlit dashboard running)
Phase 6: Next Steps,Add permanent log file output (logs/ingestion.log),Done
Phase 6: Next Steps,Daily log rotation (TimedRotatingFileHandler),Done
Phase 7: Visualization & Dashboard,Plot temperature vs timestamp chart,Done
Phase 7: Visualization & Dashboard,Add multiple charts (humidity, irradiance, wind speed),Done
Phase 7: Visualization & Dashboard,Build simple dashboard (Streamlit with sidebar),Done
Phase 8: Real-Time Ingestion,Simulate sensor streams (append rows every 5minute),Done
Phase 8: Real-Time Ingestion,Implement manual trigger for on-demand ingestion,Done
Phase 8: Real-Time Ingestion,Enable continuous ingestion pipeline,Pending
Phase 9: Predictive Analytics,Calculate averages/min/max/moving averages,Pending
Phase 9: Predictive Analytics,Train ML model for forecasting (scikit-learn),Pending
Phase 10: Deployment & Scaling,Containerize with Docker,Pending
Phase 10: Deployment & Scaling,Deploy to cloud (AWS/Azure/GCP),Pending
Phase 11: Web-Sensor Data Integration,Connect to OpenWeather API for local weather data,Done
Phase 11: Web-Sensor Data Integration,Ingest NASA POWER API for solar irradiance and climate data,Done
Phase 11: Web-Sensor Data Integration,Integrate PVOutput API for solar PV system performance,Pending
Phase 11: Web-Sensor Data Integration,Optional: Add other APIs (NOAA, Meteostat, etc.),Pending
Phase 11: Web-Sensor Data Integration,Normalize and store web-sensor data into sensor_data table,Done
Phase 11: Web-Sensor Data Integration,Combine local sensor + web API data for richer analytics,Pending
...Recap
    Use View → Terminal if `Ctrl+`` doesn’t work.
    Run dashboard → python -m streamlit run dashboard.py.
    Stop dashboard → Ctrl + C.
    Optional background run → Start-Process python "-m streamlit run dashboard.py".
    Now dashboard should run reliably.
    next to add OpenWeather API ingestion so dashboard shows both local sensor data and live weather data.
...notes 260127.
---via blackboxAI
## 📋 Recent Updates (January 2026)
### ✅ Completed Implementations
- **NASA POWER API Integration**: Implemented `api_wrappers/nasa_power.py` with real API calls and simulated fallback for solar irradiance data
- **Data Preprocessing Toolkit**: Completed `preprocessing/preprocess.py` with comprehensive data cleaning, normalization, and outlier detection functions
- **Weather Data Capture**: Added `capture_weather_data.py` for automated 20-row weather data ingestion from OpenWeather API
- **HTML Table Generation**: Created `generate_html_table.py` for dynamic database data visualization with Bootstrap styling
- **Database Schema**: Updated `db/schema.sql` with complete PostgreSQL table definitions and TimescaleDB extension support
- **Manual Trigger for Real-Time Ingestion**: Implemented on-demand data ingestion via HTML button in `solar_wind_display.html` with Flask backend in `ingestion_trigger.py`, integrating simulated sensor data with live OpenWeather and NASA POWER API calls
### 🔧 Key Features Added
- **API Wrappers**: OpenWeather (weather data) and NASA POWER (solar irradiance) with robust error handling
- **Data Processing**: Full preprocessing pipeline including cleaning, normalization, interpolation, and outlier detection
- **Web Visualization**: Automated HTML table generation from database queries
- **Batch Automation**: `run_ingest.bat` for scheduled data ingestion
- **Dashboard Integration**: Streamlit dashboard with table and chart views for sensor data analysis

### 📊 Current Status
- **Database**: PostgreSQL with TimescaleDB support, sensor_data table active
- **APIs**: OpenWeather and NASA POWER integrated with fallback simulation
- **Visualization**: Streamlit dashboard and HTML table generation working
- **Automation**: Batch file for scheduled ingestion, daily log rotation
- **Data Quality**: Preprocessing pipeline ready for ML model training
### 🎯 Next Priorities
- Phase 8: Enable continuous real-time ingestion pipeline
- Phase 9: Implement predictive analytics with ML models
- Phase 10: Containerization with Docker and cloud deployment
- Security: Move hardcoded credentials to environment variables
### 📋 Phase 8: Real-Time Ingestion - Completed Implementation
**Completed Features:**
- **Manual Trigger Button**: Added on-demand ingestion button to `solar_wind_display.html` for triggering real-time data ingestion without continuous loops.
- **Flask Backend Endpoint**: Implemented `/trigger_ingestion` endpoint in `ingestion_trigger.py` to handle button clicks and execute ingestion scripts.
- **Integrated Real-Time API Data**: Combined simulated sensor data with live API calls (OpenWeather for weather data, NASA POWER for solar irradiance) triggered by the button.
  - **OpenWeather API Integration**: Fetches live weather data (temperature, humidity, wind speed) with 10 data points from past 2 days.
  - **NASA POWER API Integration**: Fetches live solar irradiance data with 10 data points from past 2 days.
  - **Data Combination Logic**: Merges simulated sensor data with live API data for comprehensive ingestion.
- **Error Handling & Retries**: Added robust error handling with exponential backoff and retry mechanisms for API calls.
- **Database Insertion**: Ensures combined data is properly inserted into the sensor_data table with duplicate handling.
- **Health Monitoring**: Includes status feedback in the HTML interface after button trigger, displaying ingestion results (success/failure, rows inserted).
- **Configuration Management**: Integrated with existing config.py for API keys and settings.
**Dependent Files Updated:**
- `solar_wind_display.html`: Added manual trigger button and JavaScript for API calls and status display.
- `ingestion_trigger.py`: New Flask application with `/trigger_ingestion` endpoint handling data generation, API fetching, and database insertion.
- `db/sensor_stream_sim.py`: Updated to generate sensor data on-demand when triggered.
- `capture_weather_data.py`: Integrated into on-demand pipeline for weather data fetching.
- `api_wrappers/nasa_power.py`: Ensured integration for solar irradiance data fetching.
- `requirements.txt`: Added Flask for web framework support.
**Testing & Validation:**
- Manual trigger tested in HTML interface with status feedback.
- API integrations validated with fallback mechanisms.
- Database insertions confirmed with row count tracking.

Summary of Functional Checks (Phases 1-7)
Phase 1: Database Setup
PostgreSQL Connection: Successfully tested using db/test_connection.py - connection established, 15 rows counted, top/bottom 2 rows displayed correctly
Schema Creation: Verified db/schema.sql executes without errors, creating sensor_data table with proper columns
Data Verification: Confirmed timestamp format and data integrity in database
Phase 2: Data Ingestion
CSV Ingestion: Tested db/db_ingest.py - successfully ingested files, showed 15 rows before/after, 0 new rows added (duplicates handled)
Duplicate Handling: Verified ON CONFLICT logic prevents duplicate insertions
Logging: Confirmed ingestion logging functionality
Phase 3: Python Integration
psycopg2 Driver: Confirmed successful import and connection to PostgreSQL
db_ingest.py Script: Verified handles database connections and operations
Insert/Fetch Operations: Tested row insertion and retrieval functionality
Phase 4: Log Ingestion
sensor_logs.txt Adaptation: Script successfully adapted for log file ingestion
Multiple Row Insertion: Verified bulk data insertion capabilities
Output Verification: Confirmed proper data formatting and insertion
Phase 5: Enhancements
Duplicate Handling: Tested and confirmed duplicate prevention logic
Timestamp Formatting: Verified datetime formatting in database
Pretty Output: Confirmed tabulate library usage for formatted display
Row Counting: Verified accurate row count tracking
Modular Connection: Confirmed db_connector.py get_connection() function
test_connection.py: Verified displays top/bottom rows with proper formatting
Phase 6: Next Steps
Automated Ingestion: Fixed run_ingest.bat path to current directory, confirmed batch execution
CSV/Real Sensor Streams: Updated db/sensor_stream_sim.py to generate max 10 rows at 100ms intervals (tested successfully)
Dashboard Integration: Verified dashboard.py Streamlit app runs (with expected warnings for bare execution)
Permanent Log Output: Confirmed logs/ingestion.log creation and writing
Daily Log Rotation: Verified TimedRotatingFileHandler creates rotated logs (ingestion.log.2026-01-20, ingestion.log.2026-01-26)
Phase 7: Visualization & Dashboard
Streamlit Import: Confirmed library installation and import success
psycopg2 Import: Verified database connector availability
Dashboard Execution: Successfully ran dashboard script (warnings normal for bare mode)
Charts Implementation: Verified all four line charts (temperature, humidity, irradiance, wind speed) with timestamp indexing
Dashboard Structure: Confirmed sidebar navigation (Table View, Charts View, Summary View) and statistics display
Phase 8: Real-Time Ingestion (Partial)
README Alignment: Updated Phase 8, Step 2 documentation to reflect completed manual trigger implementation
Requirements Update: Added Flask to requirements.txt for web framework support
Completed Implementations: Added manual trigger for on-demand ingestion to completed features list