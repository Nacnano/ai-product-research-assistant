"""
Data ingestion script for loading product catalog into ChromaDB vector store.

This script:
1. Loads product data from CSV file
2. Formats product information for optimal retrieval
3. Chunks text data appropriately
4. Generates embeddings using FastEmbed
5. Stores in ChromaDB for semantic search

The script supports full refresh (deletes existing data) to ensure clean updates.
"""
import logging
import os
import shutil

import pandas as pd
from langchain_chroma import Chroma
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import CharacterTextSplitter

from src.core.config import settings

# Configure logging for informative progress tracking
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def prepare_product_content(row: pd.Series) -> str:
    """
    Format product attributes into a structured string for embedding.
    
    This function creates a consistent, searchable format that includes all
    relevant product information for semantic similarity matching.
    
    Args:
        row: A pandas Series containing product information
        
    Returns:
        str: Formatted product content with all attributes
    """
    return (
        f"Product ID: {row['product_id']}\n"
        f"Name: {row['product_name']}\n"
        f"Category: {row['category']}\n"
        f"Brand: {row['brand']}\n"
        f"Price: ${row['current_price']}\n"
        f"Stock: {row['stock_quantity']}\n"
        f"Description: {row['description']}\n"
        f"Rating: {row['average_rating']}"
    )


def ingest_data() -> None:
    """
    Ingest product data from CSV into ChromaDB vector store.
    
    Process flow:
    1. Load product catalog from CSV file
    2. Format each product into embeddable text
    3. Chunk text for optimal embedding size
    4. Generate embeddings using FastEmbed (BAAI/bge-small-en-v1.5)
    5. Store in ChromaDB with full refresh (clears existing data)
    
    This function performs a full refresh, deleting existing data to ensure
    consistency. For production, consider implementing incremental updates.
    
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        Exception: For other unexpected errors during processing
    """
    logger.info(f"Starting data ingestion from {settings.DATA_PATH}...")
    
    # Step 1: Load product data from CSV
    try:
        df = pd.read_csv(settings.DATA_PATH)
        logger.info(f"Successfully loaded {len(df)} products from CSV")
    except FileNotFoundError:
        logger.error(f"CSV file not found at {settings.DATA_PATH}. Please ensure the file exists.")
        return
    except Exception as e:
        logger.error(f"Unexpected error loading CSV data: {e}")
        return

    # Step 2: Format each product as structured text for embedding
    df['page_content'] = df.apply(prepare_product_content, axis=1)

    # Step 3: Load formatted data into LangChain documents
    loader = DataFrameLoader(df, page_content_column="page_content")
    documents = loader.load()
    
    logger.info(f"Successfully created {len(documents)} documents for processing.")

    # Step 4: Chunk documents for optimal embedding
    # Using large chunk size (1000) to keep product information together
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    logger.info(f"Split into {len(texts)} text chunks for embedding.")

    # Step 5: Initialize embedding model
    # Using FastEmbed with BGE-small model for efficient, quality embeddings
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # Step 6: Clear existing vector store for full refresh
    # This ensures data consistency but requires re-indexing all products
    if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        logger.info("Clearing existing vector store for full refresh...")
        try:
            shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)
            logger.info("Successfully cleared old vector store data")
        except OSError as e:
            logger.warning(f"Could not clear existing directory: {e}")

    # Step 7: Create and persist vector store
    logger.info("Creating ChromaDB vector store with embeddings...")
    try:
        Chroma.from_documents(
            documents=texts, 
            embedding=embeddings, 
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        logger.info(f"✓ Data ingestion complete! Vector store saved to {settings.CHROMA_PERSIST_DIRECTORY}")
        logger.info(f"  - Total products ingested: {len(documents)}")
        logger.info(f"  - Total vector chunks: {len(texts)}")
    except Exception as e:
        logger.error(f"✗ Failed to create vector store: {e}")


if __name__ == "__main__":
    ingest_data()
