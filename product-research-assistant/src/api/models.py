"""
Pydantic models for API request and response validation.

This module defines:
- QueryRequest: Input schema for agent queries
- QueryResponse: Output schema for agent responses  
- FeedbackRequest: Input schema for user feedback submission
"""
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for submitting queries to the AI agent."""
    
    query: str = Field(..., description="The user's question or request", min_length=1)


class QueryResponse(BaseModel):
    """Response model for agent query results."""
    
    id: str = Field(..., description="Unique identifier for this query")
    query: str = Field(..., description="The original query submitted")
    result: str = Field(..., description="The agent's response")
    intermediate_steps: Optional[List[Any]] = Field(
        None, 
        description="Optional list of intermediate steps taken by the agent"
    )


class FeedbackRequest(BaseModel):
    """Request model for submitting feedback on a query response."""
    
    query_id: str = Field(..., description="ID of the query being rated")
    rating: int = Field(..., description="User rating (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Optional feedback comment")
