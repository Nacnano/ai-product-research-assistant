import requests
import time
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_api():
    url = "http://localhost:8000/query"
    payload = {"query": "What is the price of the latest iPhone and what is our profit margin if we sell it for $1200 with a cost of $900?"}
    
    logger.info(f"Testing API at {url}...")
    
    # Wait for server to start
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                logger.info("Server is ready.")
                break
        except requests.exceptions.ConnectionError:
            logger.info("Waiting for server...")
            time.sleep(2)
    else:
        logger.error("Server failed to start.")
        sys.exit(1)

    try:
        logger.info(f"Sending query: {payload['query']}")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        logger.info(f"API Response: {data}")
        
        if "result" in data and data["result"]:
             logger.info("API Verification Passed!")
        else:
             logger.warning("API Verification Warning: Empty result.")
    except Exception as e:
        logger.error(f"API Verification Failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
