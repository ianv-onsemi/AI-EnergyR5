-- Create the energy_db database
CREATE DATABASE energy_db;

-- Connect to energy_db
\c energy_db;

-- Create sensor_data table for time-series sensor readings
CREATE TABLE sensor_data (
    rn SERIAL PRIMARY KEY,    -- Row number
    timestamp TIMESTAMP,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    wind_speed DECIMAL(5,2),
    cloudiness DECIMAL(5,2),  -- Cloudiness percentage (blank if not applicable)
    uv_index DECIMAL(5,2),    -- UV Index (blank if not applicable)
    irradiance DECIMAL(7,2),
    source VARCHAR(50)
);

-- Optional: Add TimescaleDB extension for better time-series performance
-- CREATE EXTENSION IF NOT EXISTS timescaledb;
-- SELECT create_hypertable('sensor_data', 'timestamp');
