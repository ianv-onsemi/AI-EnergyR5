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
├── clean_database.py     # Script to clean database (retain only sim data)
├── config.py             # Configuration settings (API keys, database credentials)
├── create_collectAll.py  # Script to create collectAll data collection
├── generate_past_data.py # Script to generate historical data
├── requirements.txt      # List of Python dependencies
├── review_openweather_data.py # Script to review OpenWeather data
├── temp_check_data.py    # Temporary script for data checking
├── temp_summary.py       # Temporary script for data summary
├── temp_test_endpoint.py # Temporary script for endpoint testing
├── update_collect1.py    # Script to update collect1 data
├── update_collectAll.py  # Script to update collectAll data
│
├── api_wrappers/         # External API integration modules
│   ├── nasa_power.py     # NASA POWER API wrapper for solar irradiance data
│   └── openweather.py    # OpenWeather API wrapper for weather data
│
├── data/                 # Data files and logs
│   ├── collect1.txt      # Collected data sim
│   ├── collect2.txt      # Collected data nasapower
│   ├── collect3.txt      # Collected data openweather
│   ├── collectAll.txt    # All collected data combined
│   ├── sensor_data.csv   # CSV file for sensor data
│   └── sensor_logs.txt   # Plain text sensor log file
│
├── db/                   # Database setup and connectors
│   ├── api_ingest_openweather.py # OpenWeather API ingestion
│   ├── db_connector.py   # Python script for DB connection
│   ├── db_ingest.py      # Data ingestion script
│   ├── schema.sql        # SQL table definitions
│   ├── sensor_stream_sim.py # Sensor stream simulation
│   └── test_connection.py # Quick connection test script
│
├── docs/                 # Documentation and notes
│   ├── myNotes.txt       # Development notes and progress logs
│   └── TODO.md           # Task list and project roadmap
│
├── logs/                 # Log files
│   ├── ingestion.log     # Today's ingestion log
│   ├── ingestion.log.2026-01-20 # Yesterday's log (auto-rotated)
│   ├── ingestion.log.2026-01-26 # Older log (auto-rotated)
│   └── ingestion.log.2026-01-27 # Older log (auto-rotated)
│
├── notebooks/            # Jupyter notebooks for demos
│   └── data_pipeline_demo.py # Step-by-step interactive demo
│
├── preprocessing/        # Data cleaning and preprocessing scripts
│   └── preprocess.py     # Normalize and clean sensor logs
│
├── scripts/              # Utility scripts
│   ├── capture_weather_data.py # Automated weather data capture
│   ├── count_data_sources.py   # Count data sources utility
│   ├── data_collector.py       # Data collection script
│   ├── run_ingest.bat          # Batch file for scheduled ingestion
│   └── show_recent_data.py     # Display recent sensor data
│
├── sensors/              # Sensor data scripts
│   ├── sensor_ingest.py  # Generate or simulate sensor readings
│   └── sensor_logs.txt   # Sensor logs
│
├── tests/                # Testing and validation scripts
│   ├── check_schema.py   # Schema validation
│   └── test_imports.py   # Import testing
│
└── web/                  # Web-related files
    ├── dashboard.html    # HTML interface for data display
    ├── dashboard.py      # Streamlit dashboard
    ├── generate_html_table.py # HTML table generation
    ├── ingestion_trigger.py   # Flask endpoint for ingestion
    ├── data/             # Web-specific data files
    │   └── sensor_logs.txt # Web sensor logs
    └── logs/             # Web-specific logs
        └── ingestion.log # Web ingestion log
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
- For detailed development notes and progress logs, refer to `mynotes.txt`

---

## 📖 User Guide



### Complete Step-by-Step Guide: Test Phase 8 Real-Time Data Collection and View Results in Web Interface

#### Overview
This guide walks you through testing Phase 8's real-time data collection features and viewing the results in the web interface. Phase 8 includes two data collection methods: manual trigger and scheduled ingestion. By the end of this guide, you'll see your collected data displayed in interactive charts and tables. Choose between the Command-Line Method for step-by-step terminal instructions or the HTML Interface Method for a user-friendly button-based experience.

#### Prerequisites (What You Need First)
Before starting, make sure you have:
- PostgreSQL database running (see PostgreSQL Database Management section above)
- Python environment with all packages installed (`pip install -r requirements.txt`)
- Internet connection (needed for weather and solar data APIs)
- Your project folder open in VS Code or terminal

#### Command-Line Method

##### Step 1: Prepare Your Environment

1. **Check if PostgreSQL is running**:
   - Open Command Prompt: Press `Win + R`, type `cmd`, press Enter
   - Navigate to PostgreSQL: `cd "D:\My Documents\tools\postgresql\pgsql\bin"`
   - Check status: `pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" status`
   - If not running, start it: `pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" -l logfile start`

2. **Verify database connection**:
   - In your project folder, run: `python db/test_connection.py`
   - You should see existing sensor data in a table format

##### Step 2: Test Manual Data Collection

Manual collection lets you trigger data ingestion instantly via a web API call.

1. **Open your first Command Prompt window** and navigate to the web folder:
   ```bash
   cd "d:\My Documents\ee\1_Tester_cee\AI\AI-EnergyR5\web"
   ```

2. **Start the web server**:
   ```bash
   python ingestion_trigger.py
   ```
   - You should see: "Running on http://0.0.0.0:5000"
   - Keep this window open - the server is now running

3. **Open a second Command Prompt window** (don't close the first one):
   - Navigate to the same web folder: `cd "d:\My Documents\ee\1_Tester_cee\AI\AI-EnergyR5\web"`

4. **Trigger data collection manually**:
   ```bash
   curl -X POST http://localhost:5000/trigger_ingestion
   ```
   - This sends a request to collect new sensor data
   - The response will show how many data points were collected

5. **Check the server window** (first Command Prompt):
   - You should see messages like:
     - "Collecting weather data from OpenWeather API..."
     - "Collecting solar data from NASA POWER API..."
     - "Data collection completed. Rows added: 20"

6. **Verify data was saved to database**:
   ```bash
   python ..\db\test_connection.py
   ```
   - You should see new rows added to your sensor data table
   - Look for recent timestamps in the data

##### Step 3: Test Automatic Data Collection (Optional)

Automatic collection runs daily after 8 PM, but you can test the function directly.

1. **In a Python session or new Command Prompt**, run:
   ```bash
   python -c "from web.ingestion_trigger import perform_continuous_ingestion; result = perform_continuous_ingestion(); print('Result:', result)"
   ```

2. **What you'll see**:
   - **Before 8 PM**: `{'success': True, 'message': 'Not yet 8 PM - skipping scheduled ingestion', 'total_rows': 0}`
   - **After 8 PM**: The system will collect historical data and show rows added

##### Step 4: View Your Data in the Web Interface

Now that you've collected data, let's see it in the web dashboard!

1. **Open a new Command Prompt window** and navigate to the web folder:
   ```bash
   cd "d:\My Documents\ee\1_Tester_cee\AI\AI-EnergyR5\web"
   ```

2. **Start the Streamlit dashboard**:
   ```bash
   python dashboard.py
   ```
   - This opens your default web browser automatically
   - The dashboard will load and show your sensor data

3. **Explore the dashboard**:
   - **Table View**: See all your sensor data in a neat table format
     - Columns: timestamp, temperature, humidity, irradiance, wind_speed
     - Data is sorted by timestamp (newest first)
   - **Charts View**: Interactive charts showing trends over time
     - Temperature chart (line graph over time)
     - Humidity chart
     - Irradiance (solar power) chart
     - Wind speed chart
     - Hover over points to see exact values
   - **Summary View**: Statistics and insights
     - Average values for each sensor type
     - Min/max values
     - Recent data trends

4. **Alternative: View HTML Table**:
   ```bash
   python generate_html_table.py
   ```
   - This creates an HTML file you can open in any browser
   - Shows the same data in a formatted table

##### Step 5: Check Logs and Verify Everything Worked

1. **View the ingestion logs**:
   - Open `logs/ingestion.log` in your project folder
   - Look for recent entries showing:
     - When data collection started
     - How many rows were added
     - Any error messages (if something went wrong)

2. **Final database check**:
   ```bash
   python db/test_connection.py
   ```
   - Confirm all your new data is there
   - Count should be higher than before you started

#### HTML Interface Method

For a more user-friendly experience, start directly with the interactive HTML interface that provides clickable buttons for all Phase 8 steps and routines.

##### Prerequisites
- Python environment with all packages installed (`pip install -r requirements.txt`)
- Internet connection for API data
- PostgreSQL database (will be started via HTML interface)

##### Step 1: Launch the HTML Interface

1. **Navigate to the web folder**:
   ```bash
   cd "d:\My Documents\ee\1_Tester_cee\AI\AI-EnergyR5\web"
   ```

2. **Start the Flask web server and open HTML interface**:
   ```bash
   python ingestion_trigger.py
   ```
   - The server will start and run on `http://0.0.0.0:5000`
   - You should see: "Running on http://0.0.0.0:5000"
   - Keep this window open
   - Access the dashboard at: `http://10.243.119.221:5000` (or `http://localhost:5000` if running locally)

##### Step 2: Use the Interactive Buttons

The HTML page provides buttons for each Phase 8 routine with function descriptions:

**System Setup Buttons:**
- **Start Flask Web Server**: Launches the Flask server (already running when you open the page)
- **Check PostgreSQL Status**: Verifies if PostgreSQL database server is running
- **Verify DB Connection**: Tests database connectivity and shows existing data

**Data Collection Buttons:**
- **Trigger Data Ingestion**: Manually collects sensor data from APIs (weather + solar)
- **Test Automatic Ingestion**: Simulates scheduled data collection (time-based)

**Visualization Buttons:**
- **Start Streamlit Dashboard**: Launches interactive charts and analytics dashboard
- **View HTML Table**: Generates and displays data in HTML table format

**Monitoring Buttons:**
- **View Ingestion Logs**: Shows recent log entries with timestamps and status
- **Final DB Check**: Performs final verification of data storage

##### Step 3: Monitor Routine Completion

Each button provides real-time feedback on routine completion:

- **Success Indicators**: Green alerts showing "Success!" with details like rows added, data fetched, etc.
- **Progress Messages**: Loading spinners and "Processing..." messages during execution
- **Error Handling**: Red alerts for failures with specific error messages
- **Status Updates**: Real-time updates on data collection progress, API calls, and database operations

##### Step 4: Complete the Full Phase 8 Routine

Follow this sequence for complete Phase 8 testing:

1. **Environment Setup**:
   - Click "Check PostgreSQL Status" → Should show "running"
   - Click "Verify DB Connection" → Should display existing sensor data table

2. **Data Collection**:
   - Click "Trigger Data Ingestion" → Collects 10 weather + 10 solar data points
   - Click "Test Automatic Ingestion" → Tests scheduled collection logic

3. **Data Visualization**:
   - Click "Start Streamlit Dashboard" → Opens interactive charts at http://localhost:8501
   - Click "View HTML Table" → Shows data in formatted HTML table

4. **Verification**:
   - Click "View Ingestion Logs" → Check for successful data collection entries
   - Click "Final DB Check" → Confirm new data rows were added to database

##### Step 5: Error Logs and Troubleshooting

The bottom of the HTML page includes 5 rows for error logs and troubleshooting:

1. **Real-time Error Display**: Errors appear immediately below buttons with red alerts
2. **Log Viewer**: "View Ingestion Logs" button shows detailed server logs
3. **Status Messages**: Each button shows success/failure status with details
4. **Network Issues**: API failures and connection problems are logged
5. **Database Errors**: Connection failures and query errors are displayed

#### What You Should See in the Web Interface

After following these steps, your web dashboard should show:
- **Recent sensor readings** with timestamps from when you triggered collection
- **Interactive charts** plotting temperature, humidity, irradiance, and wind speed over time
- **Real data** from OpenWeather API (weather) and NASA POWER API (solar irradiance)
- **Clean, organized display** that's easy to read and understand

#### Troubleshooting

If something doesn't work:

- **"Command not found"**: Make sure you're in the correct folder
- **"Connection failed"**: Check if PostgreSQL is running (Step 1)
- **"Import error"**: Run `pip install -r requirements.txt`
- **No data collected**: Check your internet connection and API keys in `config.py`
- **Dashboard won't open**: Make sure no other programs are using port 8501

**Common Issues and Solutions:**
- **"Flask server not responding"**: Restart `python ingestion_trigger.py`
- **"PostgreSQL not running"**: Use "Check PostgreSQL Status" button to diagnose
- **"API key errors"**: Check `config.py` for valid API keys
- **"No data collected"**: Verify internet connection and API limits
- **"Streamlit won't start"**: Check if port 8501 is available

#### Quick Reference Commands

```bash
# Check PostgreSQL status
pg_ctl.exe -D "D:\My Documents\tools\postgresql\pgsql\data" status

# Start web server for data collection
cd web
python ingestion_trigger.py

# Trigger manual data collection
curl -X POST http://localhost:5000/trigger_ingestion

# Start web dashboard to view data
streamlit run dashboard.py

# Check database contents
python db/test_connection.py

# Test automatic collection
python -c "from web.ingestion_trigger import perform_continuous_ingestion; print(perform_continuous_ingestion())"
```

This complete guide takes you from setting up the environment to collecting data and viewing beautiful charts in your web browser. The Phase 8 system automatically combines simulated sensor data with real weather and solar data, giving you a comprehensive view of your renewable energy system's performance!

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

### Phase 8: Real-Time Ingestion ✅ Done
- Simulate sensor streams (append rows every minute) ✅ Done
- Implement manual trigger for on-demand ingestion ✅ Done
- Enable continuous ingestion pipeline ✅ Done
- HTML interface integration for Phase 8 steps ✅ Done

### Phase 9: Web-Sensor Data Integration 🔄 Partial
- Connect to OpenWeather API for local weather data ✅ Done
- Ingest NASA POWER API for solar irradiance and climate data ✅ Done
- Integrate PVOutput API for solar PV system performance ⏳ Pending
- Optional: Add other APIs (NOAA, Meteostat, etc.) ⏳ Pending
- Normalize and store web-sensor data into sensor_data table ✅ Done
- Combine local sensor + web API data for richer analytics ⏳ Pending

#### Database Table Model
The `sensor_data` table stores web sensor data with the following 9 headers:

| Header Label | Data Type | Description | Source API |
|--------------|-----------|-------------|------------|
| Row Number | SERIAL | Auto-incrementing row identifier | Database |
| Timestamp | TIMESTAMP | Date and time of data collection | System/API |
| Temperature (°C) | DECIMAL(5,2) | Air temperature in Celsius | OpenWeather |
| Humidity (%) | DECIMAL(5,2) | Relative humidity percentage | OpenWeather |
| Wind Speed (m/s) | DECIMAL(5,2) | Wind speed in meters per second | OpenWeather |
| Cloudiness (%) | DECIMAL(5,2) | Cloud cover percentage | OpenWeather |
| UV Index | DECIMAL(3,1) | Ultraviolet index value | OpenWeather |
| Irradiance (W/m²) | DECIMAL(7,2) | Solar irradiance in watts per square meter | NASA POWER |
| Source | VARCHAR(50) | Data source identifier (openweather/nasa_power) | System |

### Phase 10: Predictive Analytics ⏳ Pending
- Calculate averages/min/max/moving averages
- Train ML model for forecasting (scikit-learn)

### Phase 11: Deployment & Scaling ⏳ Pending
- Containerize with Docker
- Deploy to cloud (AWS/Azure/GCP)
