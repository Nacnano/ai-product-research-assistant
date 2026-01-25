import requests
import time
import sys
import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_results.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

@dataclass
class TestCase:
    name: str
    endpoint: str
    method: str
    payload: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    validation_key: Optional[str] = None

class colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

def wait_for_server(max_retries: int = 15):
    logger.info("Waiting for server to be ready...")
    for _ in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                logger.info(f"{colors.GREEN}Server is online.{colors.RESET}")
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    logger.error(f"{colors.RED}Server failed to start.{colors.RESET}")
    return False

def run_test_case(test: TestCase) -> Tuple[bool, Any]:
    logger.info(f"Running Test: {test.name}...")
    url = f"{BASE_URL}{test.endpoint}"
    
    try:
        start_time = time.time()
        if test.method == "GET":
            response = requests.get(url)
        elif test.method == "POST":
            response = requests.post(url, json=test.payload)
        else:
            logger.error(f"Unsupported method: {test.method}")
            return False, None
            
        elapsed = time.time() - start_time
        
        if response.status_code != test.expected_status:
            logger.error(f"{colors.RED}[FAIL] {test.name}{colors.RESET} - Status: {response.status_code}, Response: {response.text[:200]}")
            return False, None
            
        data = response.json()
        
        if test.validation_key and (test.validation_key not in data or not data[test.validation_key]):
             logger.warning(f"{colors.RED}[FAIL] {test.name}{colors.RESET} - Missing key '{test.validation_key}' in response: {str(data)[:200]}")
             return False, data

        logger.info(f"{colors.GREEN}[PASS] {test.name}{colors.RESET} ({elapsed:.2f}s) - Response: {str(data)[:100]}...")
        return True, data

    except Exception as e:
        logger.error(f"{colors.RED}[ERROR] {test.name}{colors.RESET}: {e}")
        return False, None

def main():
    if not wait_for_server():
        sys.exit(1)

    # 1. Basic Tests
    initial_tests = [
        TestCase(name="Health Check", endpoint="/health", method="GET", validation_key="status"),
        TestCase(name="Product Catalog Search (RAG)", endpoint="/query", method="POST", payload={"query": "What wireless headphones do we have in stock?"}, validation_key="result"),
        TestCase(name="Market Research (Web Search)", endpoint="/query", method="POST", payload={"query": "Current market price?"}, validation_key="result"),
    ]

    passed = 0
    failed = 0

    for test in initial_tests:
        success, _ = run_test_case(test)
        if success:
            passed += 1
        else:
            failed += 1

    # 2. Fetch History to get ID for Feedback
    logger.info("Fetching History to get Query ID...")
    success, history = run_test_case(TestCase(name="Fetch Query History", endpoint="/queries", method="GET"))
    
    query_id = None
    if success and isinstance(history, list) and len(history) > 0:
        query_id = history[0].get("id")
        passed += 1
        logger.info(f"Found Query ID: {query_id}")
    else:
        failed += 1
        logger.error("Failed to fetch history or history is empty.")

    # 3. Submit Feedback using ID
    if query_id:
        success, _ = run_test_case(TestCase(
            name="Submit Feedback", 
            endpoint="/feedback", 
            method="POST", 
            payload={"query_id": query_id, "rating": 5, "comment": "Great result!"}, 
            validation_key="message"
        ))
        if success:
             passed += 1
        else:
             failed += 1
    else:
        logger.warning(f"{colors.RED}[SKIP] Submit Feedback (No ID){colors.RESET}")
        failed += 1

    logger.info("========================================")
    logger.info(f"Test Summary: {passed} Passed, {failed} Failed")
    logger.info("========================================")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
