"""
Price analysis tool for calculating profit margins deterministically.

This module provides tools for precise margin calculations without relying on LLM math.
The LLM should use these tools for calculations and then format the results.
"""
import json

from langchain.tools import tool
from pydantic import BaseModel, Field


class PriceAnalysisInput(BaseModel):
    """Input schema for price analysis calculations."""
    
    price: float = Field(..., description="The selling price of the product", gt=0)
    cost: float = Field(..., description="The cost of the product", ge=0)


def calculate_margin(price: float, cost: float) -> float:
    """
    Calculate profit margin percentage using a deterministic formula.
    
    Formula: ((price - cost) / price) × 100
    
    Args:
        price: The selling price of the product
        cost: The cost to produce or acquire the product
        
    Returns:
        float: Profit margin as a percentage (0-100)
        
    Note:
        Returns 0.0 if price is 0 to avoid division by zero
    """
    if price == 0:
        return 0.0
    return ((price - cost) / price) * 100

@tool(args_schema=PriceAnalysisInput)
def price_analysis(price: float, cost: float) -> str:
    """
    Calculate the profit margin percentage for a product.
    
    This tool performs precise margin calculations deterministically.
    Use this tool instead of doing math yourself to ensure accuracy.
    The margin is calculated as: ((price - cost) / price) × 100
    
    Args:
        price: The selling price of the product (must be positive)
        cost: The cost of the product (must be non-negative)
        
    Returns:
        str: JSON string containing price, cost, and calculated margin percentage
        
    Example:
        Input: price=100, cost=70
        Output: {"price": 100, "cost": 70, "margin_percent": 30.0}
    """
    margin = calculate_margin(price, cost)
    return json.dumps({
        "price": price,
        "cost": cost,
        "margin_percent": round(margin, 2)
    })
