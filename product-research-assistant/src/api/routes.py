from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.api.models import QueryRequest, QueryResponse, FeedbackRequest
from src.core.agent import get_agent_executor
from src.api.database import get_db, init_db, QueryHistory, Feedback
import logging
import uuid
from typing import List

router = APIRouter()
logger = logging.getLogger(__name__)

agent_executor = get_agent_executor()

@router.on_event("startup")
def on_startup():
    init_db()

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Main endpoint to query the AI Agent.
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        result = agent_executor.invoke({"input": request.query})
        
        output_text = result["output"]
        query_id = str(uuid.uuid4())

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
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def get_history(db: Session = Depends(get_db)):
    """
    Retrieve query history from DB.
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
    Submit user feedback for a query.
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
    
    return {"message": "Feedback received", "data": feedback}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
