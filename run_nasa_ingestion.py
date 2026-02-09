import sys
import os
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

# Import the continuous ingestion function
from web.ingestion_trigger import perform_continuous_ingestion

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting NASA POWER data ingestion to backfill missing data...")
    
    try:
        # Run the continuous ingestion function
        result = perform_continuous_ingestion()
        
        logger.info(f"Ingestion completed: {result}")
        
        # Print summary
        print("\n=== INGESTION RESULT ===")
        print(f"Success: {result.get('success', False)}")
        print(f"Total rows inserted: {result.get('total_rows', 0)}")
        print(f"Weather rows: {result.get('weather_rows', 0)}")
        print(f"Solar rows: {result.get('solar_rows', 0)}")
        print(f"Time range: {result.get('time_range', 'N/A')}")
        if result.get('message'):
            print(f"Message: {result['message']}")
            
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        print(f"\nERROR: {e}")
