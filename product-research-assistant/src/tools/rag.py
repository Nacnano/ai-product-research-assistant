"""
Product Catalog RAG (Retrieval-Augmented Generation) tool.

This module provides a tool for querying the internal product catalog
using vector similarity search with ChromaDB and FastEmbed embeddings.
"""
from langchain.tools import tool
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import Chroma

from src.core.config import settings


def get_retriever():
    """
    Initialize and return a retriever for the product catalog vector store.
    
    Returns:
        VectorStoreRetriever: Configured retriever that returns top 5 most relevant products
        
    Raises:
        Exception: If vector store directory doesn't exist or is corrupted
    """
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    db = Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    return db.as_retriever(search_kwargs={"k": 5})

@tool
def product_catalog_rag(query: str) -> str:
    """
    Query the internal product catalog using semantic similarity search.
    
    This tool is useful for answering questions about:
    - Product availability and stock levels
    - Product prices and cost information
    - Product descriptions and specifications
    - Product ratings and reviews
    - Filtering products by category, brand, or other attributes
    
    Args:
        query: The search query or question about products
        
    Returns:
        str: Formatted string containing relevant product information,
             or message indicating no results found
             
    Example queries:
        - "What wireless headphones do we have in stock?"
        - "Show me high-rated electronics under $100"
        - "Which products from AudioMax brand are bestsellers?"
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return "No relevant products found in the catalog for your query."
    
    # Format results as readable text
    result = ""
    for doc in docs:
        result += f"{doc.page_content}\n---\n"
    
    return result
