import psycopg2
import pandas as pd

# Database connection
conn = psycopg2.connect(
    dbname="energy_db",
    user="postgres",
    password="PdM",
    host="localhost",
    port="5432"
)

# Fetch latest 20 rows from sensor_data
df = pd.read_sql("SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 20;", conn)

# Generate HTML table
html_table = df.to_html(index=False, classes='table table-striped')

# Create full HTML page
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Latest 20 Weather Data Rows</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }}
        h1 {{
            color: #333;
            text-align: center;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Latest 20 Weather Data Rows from SQL Database</h1>
        <p class="text-center">This table displays the most recent 20 rows of weather data captured from OpenWeather API and stored in the PostgreSQL database.</p>
        {html_table}
    </div>
</body>
</html>
"""

# Write to HTML file
with open("latest_weather_data.html", "w") as f:
    f.write(html_content)

print("HTML file 'latest_weather_data.html' generated successfully with latest 20 rows from database.")

conn.close()
