import streamlit as st
import psycopg2
import pandas as pd

# ----------------------------
# Connect to PostgreSQL
# ----------------------------
conn = psycopg2.connect(
    dbname="energy_db",
    user="postgres",
    password="PdM",   # <-- replace with your DB password
    host="localhost",
    port="5432"
)

# ----------------------------
# Load data into Pandas
# ----------------------------
df = pd.read_sql("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 500;", conn)

# ----------------------------
# Streamlit Dashboard
# ----------------------------
st.title("🌞 Energy Sensor Dashboard")

# Sidebar navigation
page = st.sidebar.radio("Choose a view:", ["Table View", "Charts View", "Summary View"])

if page == "Table View":
    st.subheader("Latest Sensor Data (Raw Table)")
    st.dataframe(df)

elif page == "Charts View":
    st.subheader("Temperature Trend")
    st.line_chart(df.set_index("timestamp")[["temperature"]])

    st.subheader("Humidity Trend")
    st.line_chart(df.set_index("timestamp")[["humidity"]])

    st.subheader("Irradiance Trend")
    st.line_chart(df.set_index("timestamp")[["irradiance"]])

    st.subheader("Wind Speed Trend")
    st.line_chart(df.set_index("timestamp")[["wind_speed"]])

elif page == "Summary View":
    st.subheader("Basic Statistics")
    st.write("Average values from latest 500 rows:")

    summary = df[["temperature", "humidity", "irradiance", "wind_speed"]].mean()
    st.write(summary)

    st.write("Minimum values:")
    st.write(df[["temperature", "humidity", "irradiance", "wind_speed"]].min())

    st.write("Maximum values:")
    st.write(df[["temperature", "humidity", "irradiance", "wind_speed"]].max())

conn.close()
