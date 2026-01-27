"""
Database module for the AI Product Research Assistant.

This module provides:
- SQLAlchemy models for query history and user feedback
- Database session management
- Database initialization utilities

The application uses SQLite for storing query history and feedback data.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# SQLite database URL - creates product_assistant.db in the current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///./product_assistant.db"

# Create database engine with SQLite-specific configuration
# check_same_thread=False allows multiple threads to access the same connection
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_pre_ping=True  # Verify connections before using them
)

# Session factory for database transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()

class QueryHistory(Base):
    """
    Model for storing query history.
    
    Each query sent to the AI agent is logged with its response
    for analytics and feedback tracking purposes.
    """
    __tablename__ = "query_history"

    id = Column(String, primary_key=True, index=True)  # UUID string
    query = Column(Text, nullable=False)  # User's input query
    response = Column(Text, nullable=False)  # Agent's response
    timestamp = Column(DateTime, default=datetime.utcnow)  # Query timestamp (UTC)
    
    # Relationship: one query can have multiple feedback entries
    feedbacks = relationship("Feedback", back_populates="query_match")


class Feedback(Base):
    """
    Model for storing user feedback on agent responses.
    
    Users can rate and comment on query responses to help
    improve the system's performance over time.
    """
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query_id = Column(String, ForeignKey("query_history.id"))  # References QueryHistory.id
    rating = Column(Integer, nullable=False)  # User rating (typically 1-5)
    comment = Column(Text, nullable=True)  # Optional feedback comment
    timestamp = Column(DateTime, default=datetime.utcnow)  # Feedback timestamp (UTC)

    # Relationship: feedback is linked to a specific query
    query_match = relationship("QueryHistory", back_populates="feedbacks")

def init_db() -> None:
    """
    Initialize the database by creating all tables.
    
    This function creates all tables defined by SQLAlchemy models
    if they don't already exist. Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency function to get database session.
    
    Provides a database session for FastAPI endpoints and ensures
    proper cleanup after each request. Use with FastAPI's Depends().
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
