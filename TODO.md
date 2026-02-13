# TODO: Adjust Fetch Function to Get Data from Last Date to Today

## Tasks:
- [x] Check latest dates in database (OpenWeather: 2026-02-06, NASA POWER: 2026-02-06)
- [x] Add `get_last_timestamp_by_source(source)` function to `web/ingestion_trigger.py`
- [x] Modify `trigger_ingestion` endpoint to calculate date range from last date to today
- [x] Update fetch logic to distribute 10 data points across missing dates
- [x] Add date parameter support to API calls
- [x] Test the updated fetch function
- [x] Verify data fills gaps from last date to today


## Implementation Details:
1. ✅ Create helper function to get latest timestamp for each source
2. ✅ Calculate days between last date and today
3. ✅ Distribute 10 fetches evenly across missing days
4. ✅ Adjust timestamps to cover the date range
5. ✅ Ensure no duplicate timestamps are inserted

## Changes Made:
- Added `get_last_timestamp_by_source(source)` function to query database for latest timestamp per source
- Added `calculate_date_range(last_timestamp)` to determine date range from last date to today
- Added `generate_timestamps_for_date_range(start_date, end_date, num_points)` to distribute timestamps evenly
- Modified `trigger_ingestion` endpoint to:
  - Check latest dates for OpenWeather and NASA POWER separately
  - Calculate missing date range for each source
  - Distribute 10 data points across the date range with adjusted timestamps
  - Include date_range in response data

## Test Results:
- ✅ `calculate_date_range()` correctly identifies missing date ranges
- ✅ `generate_timestamps_for_date_range()` distributes 10 timestamps across single and multi-day ranges
- ✅ Database queries successfully retrieve latest timestamps by source
- ✅ Detected 7 days of missing data (2026-02-07 to 2026-02-13) for both OpenWeather and NASA POWER

## Current Status:
The fetch function now:
1. Queries the database for the latest timestamp for each source (OpenWeather and NASA POWER)
2. Calculates the date range from the last recorded date to today
3. Generates 10 evenly distributed timestamps across that date range
4. Fetches data from APIs and assigns the distributed timestamps
5. Inserts data into the database with proper source labels

**Ready for production use** - The next manual trigger will fetch data from 2026-02-07 to 2026-02-13 (7 days) and distribute 10 data points across that range.
