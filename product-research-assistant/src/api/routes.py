"""
API route handlers for the AI Product Research Assistant.

This module defines all API endpoints:
- POST /query: Submit queries to the AI agent
- GET /queries: Retrieve query history
- POST /feedback: Submit feedback on query responses
- GET /health: Health check endpoint
"""
import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.database import Feedback, QueryHistory, get_db
from src.api.models import FeedbackRequest, QueryRequest, QueryResponse
from src.core.agent import get_agent_executor


router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize the AI agent executor once at module load time
agent_executor = get_agent_executor()

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Submit a query to the AI agent for processing.
    
    The agent will analyze the query and route it to the appropriate tools:
    - Product Catalog RAG for internal product information
    - Web Search for external market data
    - Price Analysis for margin calculations
    
    Args:
        request: Query request containing the user's question
        db: Database session (injected)
        
    Returns:
        QueryResponse with the agent's answer and query ID
        
    Raises:
        HTTPException: If query processing fails
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Invoke the agent with the user's query
        result = agent_executor.invoke({"input": request.query})
        
        output_text = result["output"]
        query_id = str(uuid.uuid4())

        # Store query and response in database for history tracking
        db_query = QueryHistory(
            id=query_id,
            query=request.query,
            response=output_text
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        
        return QueryResponse(   
            id=query_id,
            query=request.query,
            result=output_text
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/queries")
async def get_history(db: Session = Depends(get_db)):
    """
    Retrieve query history from the database.
    
    Returns the 50 most recent queries along with their responses
    and timestamps, ordered by most recent first.
    
    Args:
        db: Database session (injected)
        
    Returns:
        List of query history entries with id, query, response, and timestamp
    """
    history = db.query(QueryHistory).order_by(QueryHistory.timestamp.desc()).limit(50).all()
    return [
        {
            "id": h.id, 
            "query": h.query, 
            "response": h.response, 
            "timestamp": h.timestamp
        } 
        for h in history
    ]


@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submit user feedback for a specific query response.
    
    Allows users to rate responses and provide comments to help
    improve the system's performance over time.
    
    Args:
        feedback: Feedback data including query_id, rating, and optional comment
        db: Database session (injected)
        
    Returns:
        Confirmation message with submitted feedback data
        
    Raises:
        HTTPException: If the query ID is not found (404)
    """
    query_item = db.query(QueryHistory).filter(QueryHistory.id == feedback.query_id).first()
    if not query_item:
        raise HTTPException(status_code=404, detail="Query ID not found")

    db_feedback = Feedback(
        query_id=feedback.query_id,
        rating=feedback.rating,
        comment=feedback.comment
    )
    db.add(db_feedback)
    db.commit()
    
    return {"message": "Feedback received successfully", "data": feedback}


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API availability.
    
    Returns:
        Simple status indicator showing the API is running
    """
    return {"status": "healthy"}
