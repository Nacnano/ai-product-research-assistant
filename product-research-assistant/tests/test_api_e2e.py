import requests
import time
import sys
import logging
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
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

def run_test_case(test: TestCase) -> bool:
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
            return False
            
        elapsed = time.time() - start_time
        
        if response.status_code != test.expected_status:
            logger.error(f"{colors.RED}[FAIL] {test.name}{colors.RESET} - Status: {response.status_code}, Response: {response.text[:200]}")
            return False
            
        data = response.json()
        
        if test.validation_key and (test.validation_key not in data or not data[test.validation_key]):
             logger.warning(f"{colors.RED}[FAIL] {test.name}{colors.RESET} - Missing key '{test.validation_key}' in response: {str(data)[:200]}")
             return False

        logger.info(f"{colors.GREEN}[PASS] {test.name}{colors.RESET} ({elapsed:.2f}s) - Response: {str(data)[:100]}...")
        return True

    except Exception as e:
        logger.error(f"{colors.RED}[ERROR] {test.name}{colors.RESET}: {e}")
        return False

def main():
    if not wait_for_server():
        sys.exit(1)

    test_cases = [
        # 1. System Health
        TestCase(
            name="Health Check",
            endpoint="/health",
            method="GET",
            validation_key="status"
        ),
        
        # 2. RAG Tool (Internal Data)
        TestCase(
            name="Product Catalog Search (RAG)",
            endpoint="/query",
            method="POST",
            payload={"query": "What wireless headphones do we have in stock?"},
            validation_key="result"
        ),
        
        # 3. Web Search Tool (External Data)
        TestCase(
            name="Market Research (Web Search)",
            endpoint="/query",
            method="POST",
            payload={"query": "Current market price for noise-cancelling headphones?"},
            validation_key="result"
        ),
        
        # 4. Analysis Tool (Calculation)
        TestCase(
            name="Price Analysis (Logic)",
            endpoint="/query",
            method="POST",
            payload={"query": "Calculate margin for a product with price $100 and cost $60"},
            validation_key="result"
        ),
        
        # 5. Complex Routing
        TestCase(
            name="Multi-Tool Complex Query",
            endpoint="/query",
            method="POST",
            payload={"query": "Should we adjust AudioMax headphones pricing vs competitors?"},
            validation_key="result"
        ),
        
        # 6. History
        TestCase(
            name="Fetch Query History",
            endpoint="/queries",
            method="GET"
        ),
        
        # 7. Feedback
        TestCase(
            name="Submit Feedback",
            endpoint="/feedback",
            method="POST",
            payload={"query_id": "test_id", "rating": 5, "comment": "Great result!"},
            validation_key="message"
        )
    ]

    logger.info("========================================")
    logger.info("  Starting Comprehensive API Test Suite ")
    logger.info("========================================")

    passed = 0
    failed = 0

    for test in test_cases:
        if run_test_case(test):
            passed += 1
        else:
            failed += 1
            
    logger.info("========================================")
    logger.info(f"Test Summary: {passed} Passed, {failed} Failed")
    logger.info("========================================")

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
