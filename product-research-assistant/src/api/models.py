from pydantic import BaseModel
from typing import List, Optional, Any

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    query: str
    result: str
    intermediate_steps: Optional[List[Any]] = None

class FeedbackRequest(BaseModel):
    query_id: str
    rating: int
    comment: Optional[str] = None
