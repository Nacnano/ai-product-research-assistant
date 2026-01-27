"""
Web search tool for retrieving market information and competitor data.

This module provides a tool that can search the internet for:
- Current market prices and trends
- Competitor information
- Product reviews and ratings
- General market research

Supports multiple search APIs (Tavily, Serper) with automatic fallback to mock data.
"""
import json

import requests
from langchain.tools import tool

from src.core.config import settings


@tool
def web_search(query: str) -> str:
    """
    Search the internet for current market trends, competitor prices, and product reviews.
    
    This tool provides external market intelligence not available in the internal catalog.
    It attempts to use configured search APIs (Tavily or Serper) with fallback to mock data.
    
    Args:
        query: The search query
        
    Returns:
        str: Search results as formatted text
        
    Example queries:
        - "Current market price for noise-cancelling headphones?"
        - "Latest reviews for Sony WH-1000XM5"
        - "Trending products in home fitness equipment"
    """
    # Try Tavily search API if available
    if settings.TAVILY_API_KEY:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            tavily_tool = TavilySearchResults(api_wrapper={"tavily_api_key": settings.TAVILY_API_KEY})
            return tavily_tool.invoke(query)
        except Exception as e:
            return f"Error using Tavily search: {str(e)}"
    
    # Try Serper search API if available        
    if settings.SERPER_API_KEY:
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": query})
            headers = {
                'X-API-KEY': settings.SERPER_API_KEY,
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.text
        except Exception as e:
            return f"Error using Serper search: {str(e)}"

    # Fallback to mock search data when no API keys are configured
    # This provides realistic sample data for testing and demonstration
    query_lower = query.lower()
    
    if "price" in query_lower or "cost" in query_lower:
        return """
[Mock Web Search Results - Pricing Data]

Market Overview:
- Noise-Cancelling Headphones: $150 - $350 (premium segment)

Competitor Pricing Analysis:
- SoundCore Life Q30: $79.99 (budget-friendly option)
- Bose QuietComfort 45: $329.00 (premium brand)
- Sony WH-1000XM5: $398.00 (flagship model)

Note: Prices are approximate and may vary by retailer and region.
        """
    elif "review" in query_lower or "rating" in query_lower:
        return """
[Mock Web Search Results - Reviews & Ratings]

Customer Review Insights:
- Top-rated products typically achieve 4.5+ star ratings
- Key factors customers value:
  * Battery life (20+ hours preferred)
  * Comfort for extended wear
  * Active noise cancellation quality
  * Sound clarity and bass response

Recent Trends:
- Growing preference for lightweight, portable designs
- Increased focus on multi-device connectivity
        """
    elif "trend" in query_lower:
        return """
[Mock Web Search Results - Market Trends]

Current Market Trends (2024):
- Sustainability: Rising demand for eco-friendly materials and packaging
- Smart Home Integration: Increased interest in IoT-enabled appliances
- Wireless Technology: Fast-charging and extended battery life are standard expectations
- Health & Wellness: Growing market for home fitness and wellness products

Consumer Behavior:
- Price sensitivity remains high in electronics category
- Strong preference for products with comprehensive warranty coverage
        """
    else:
        return f"""
[Mock Web Search Results]

General Market Intelligence for: "{query}"

Key Findings:
- Competitive activity is high this season with aggressive pricing strategies
- Product availability varies significantly by region and retailer
- Consumer demand shows seasonal fluctuations
- Online reviews indicate strong interest in quality and value

Recommendation: Cross-reference with internal product data for comprehensive analysis.
        """
