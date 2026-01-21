from langchain.tools import tool
from src.core.config import settings
import requests
import json

@tool
def web_search(query: str) -> str:
    """
    Useful for searching the internet for current market trends, competitor prices, 
    reviews, and general information not available in the internal catalog.
    """
    # 1. Check for Real API Keys
    if settings.TAVILY_API_KEY:
        try:
            from langchain_community.tools.tavily_search import TavilySearchResults
            tool = TavilySearchResults(api_wrapper={"tavily_api_key": settings.TAVILY_API_KEY})
            return tool.invoke(query)
        except Exception as e:
            return f"Error using Tavily search: {str(e)}"
            
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

    # 2. Mock Implementation (Default)
    # Return plausible mock data based on query keywords
    query_lower = query.lower()
    
    if "price" in query_lower or "cost" in query_lower:
        return """
        [Mock Search Result]
        - Market Price for Noise-Cancelling Headphones: $150 - $350 (Sony, Bose, AudioMax competitors).
        - Competitor Pricing:
            - SoundCore Life: $79.99
            - Bose QC45: $329.00
            - Sony WH-1000XM5: $398.00
        """
    elif "review" in query_lower or "rating" in query_lower:
        return """
        [Mock Search Result]
        - Top rated products in this category usually have 4.5+ stars.
        - Customers value battery life, comfort, and noise cancellation quality.
        - Recent reviews suggest a trend towards lightweight designs.
        """
    elif "trend" in query_lower:
        return """
        [Mock Search Result]
        - Current Market Trends:
            - Increased demand for eco-friendly materials.
            - Rise in smart-home integration for appliances.
            - Wireless and fast-charging capabilities are standard expectations.
        """
    else:
        return f"""
        [Mock Search Result]
        Found generic information relevant to "{query}". 
        Competitors are aggressive on pricing this season. 
        Stocks vary by region.
        """
