import requests
import json

# Test the fetch_sim_data_from_db endpoint
try:
    response = requests.get('http://localhost:5000/fetch_sim_data_from_db')
    if response.status_code == 200:
        data = response.json()
        print('Fetch sim data endpoint response:')
        print(f'Success: {data.get("success")}')
        print(f'Rows fetched: {data.get("rows_fetched")}')
        print(f'Message: {data.get("message")}')
        if 'summary' in data and data['summary']:
            summary = data['summary']
            print(f'Summary - Total rows: {summary.get("total_rows")}')
            print(f'Time range: {summary.get("time_range")}')
    else:
        print(f'Endpoint returned status code: {response.status_code}')
except Exception as e:
    print(f'Error testing endpoint: {e}')
