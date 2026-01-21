from fastapi import APIRouter, HTTPException
from src.api.models import QueryRequest, QueryResponse, FeedbackRequest
from src.core.agent import get_agent_executor
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize agent once (or at startup)
agent_executor = get_agent_executor()

@router.post("/query", response_model=QueryResponse)
async def query_agent(request: QueryRequest):
    """
    Main endpoint to query the AI Agent.
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Invoke agent
        # We use invoke which returns a dict with 'output' key
        result = agent_executor.invoke({"input": request.query})
        
        return QueryResponse(
            query=request.query,
            result=result["output"]
            # We could attach intermediate steps if we enabled return_intermediate_steps=True in agent
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/queries")
async def get_history():
    """
    Retrieve query history.
    TODO: Implement database persistence for history.
    """
    return {"message": "History endpoint to be implemented with DB persistence."}

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit user feedback.
    TODO: Store in DB.
    """
    return {"message": "Feedback received", "data": feedback}

@router.get("/health")
async def health_check():
    return {"status": "healthy"}
