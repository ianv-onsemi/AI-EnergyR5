-- Create the energy_db database
CREATE DATABASE energy_db;

-- Connect to energy_db
\c energy_db;

-- Create sensor_data table for time-series sensor readings
CREATE TABLE sensor_data (
    timestamp TIMESTAMP PRIMARY KEY,
    temperature DECIMAL(5,2),
    humidity DECIMAL(5,2),
    irradiance DECIMAL(7,2),
    wind_speed DECIMAL(5,2)
);

-- Optional: Add TimescaleDB extension for better time-series performance
-- CREATE EXTENSION IF NOT EXISTS timescaledb;
-- SELECT create_hypertable('sensor_data', 'timestamp');
