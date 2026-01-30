#!/usr/bin/env python3
"""
Test script to verify that the weather summary now includes irradiance statistics
"""

import requests
import json

def test_weather_summary():
    """Test the fetch_weather_data_from_db endpoint to check summary data"""
    try:
        # Make request to the endpoint
        response = requests.get('http://127.0.0.1:5000/fetch_weather_data_from_db')

        if response.status_code == 200:
            data = response.json()

            if data.get('success'):
                print("✅ Endpoint call successful")

                summary = data.get('summary')
                if summary:
                    print("✅ Summary data found")

                    # Check if irradiance statistics are present
                    irradiance = summary.get('irradiance')
                    if irradiance:
                        print("✅ Irradiance statistics found in summary:")
                        print(f"   - Average: {irradiance.get('avg')}")
                        print(f"   - Min: {irradiance.get('min')}")
                        print(f"   - Max: {irradiance.get('max')}")
                    else:
                        print("❌ Irradiance statistics missing from summary")

                    # Print full summary for verification
                    print("\n📊 Full Summary Data:")
                    print(json.dumps(summary, indent=2))

                    print(f"\n📈 Rows fetched: {data.get('rows_fetched', 0)}")

                else:
                    print("❌ No summary data in response")

            else:
                print(f"❌ Endpoint returned error: {data.get('error')}")

        else:
            print(f"❌ HTTP Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_weather_summary()
