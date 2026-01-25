import sys
import os
import logging

# Ensure src is in python path
sys.path.append(os.getcwd())

from src.tools.rag import product_catalog_rag
from src.tools.search import web_search
from src.tools.analysis import price_analysis

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_rag():
    logger.info("Testing RAG Tool...")
    try:
        result = product_catalog_rag.invoke("headphones")
        logger.info(f"RAG Result Preview: {result[:100]}...")
        if "headphones" in result.lower() or "wireless" in result.lower():
             logger.info("RAG Test Passed.")
        else:
             logger.warning("RAG Test Warning: Result might be empty or irrelevant.")
    except Exception as e:
        logger.error(f"RAG Test Failed: {e}")

def test_search():
    logger.info("Testing Web Search Tool...")
    try:
        result = web_search.invoke("latest iPhone price")
        logger.info(f"Search Result Preview: {str(result)[:100]}...")
        logger.info("Search Test Passed.")
    except Exception as e:
        logger.error(f"Search Test Failed: {e}")

def test_analysis():
    logger.info("Testing Price Analysis Tool...")
    try:
        # Pass dictionary as input for the tool
        result = price_analysis.invoke({"price": 100, "cost": 70})
        logger.info(f"Analysis Result: {result}")
        
        if "30.0" in str(result):
            logger.info("Analysis Test Passed.")
        else:
            logger.warning("Analysis Test Warning: Unexpected result value.")

    except Exception as e:
        logger.error(f"Analysis Test Failed: {e}")

if __name__ == "__main__":
    logger.info("Starting Tool Verification...")
    test_rag()
    test_search()
    test_analysis()
    logger.info("Tool Verification Complete.")
