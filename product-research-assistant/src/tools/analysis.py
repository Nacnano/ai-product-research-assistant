"""
This module contains analytical tools for the AI agent.
"""
from langchain.tools import tool
from pydantic import BaseModel, Field
import json

class PriceAnalysisInput(BaseModel):
    price: float = Field(..., description="The selling price of the product")
    cost: float = Field(..., description="The cost of the product")

def calculate_margin(price: float, cost: float) -> float:
    """Calculate profit margin percentage"""
    if price == 0:
        return 0.0
    return ((price - cost) / price) * 100

@tool(args_schema=PriceAnalysisInput)
def price_analysis(price: float, cost: float) -> str:
    """
    Calculates the profit margin percentage given a price and a cost.
    Use this tool to perform precise margin calculations.
    Returns the margin percentage.
    """
    margin = calculate_margin(price, cost)
    return json.dumps({
        "price": price,
        "cost": cost,
        "margin_percent": round(margin, 2)
    })
