import logging
import os
import shutil
import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_chroma import Chroma
from src.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def prepare_product_content(row: pd.Series) -> str:
    """
    Format product attributes into a single string for embedding.
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
    Ingests product data from CSV, chunks it, generates embeddings, 
    and stores it in ChromaDB using FastEmbed.
    """
    logger.info(f"Starting data ingestion from {settings.DATA_PATH}...")
    
    # Load Data
    try:
        df = pd.read_csv(settings.DATA_PATH)
    except FileNotFoundError:
        logger.error(f"File not found at {settings.DATA_PATH}. Please ensure the data file exists.")
        return
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        return

    # Prepare content for embedding
    df['page_content'] = df.apply(prepare_product_content, axis=1)

    # structured fields are available in the original DataFrame if needed for metadata later
    loader = DataFrameLoader(df, page_content_column="page_content")
    documents = loader.load()
    
    logger.info(f"Successfully loaded {len(documents)} documents.")

    # Chunking
    # Using a large chunk size to keep product context intact as much as possible
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    logger.info(f"Prepared {len(texts)} text chunks.")

    # Embeddings & Vector Store
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # Clear existing DB for a full refresh
    if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        logger.info("Clearing existing vector store for full refresh...")
        try:
            shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)
        except OSError as e:
            logger.warning(f"Could not clear existing directory: {e}")

    logger.info("Creating vector store...")
    try:
        Chroma.from_documents(
            documents=texts, 
            embedding=embeddings, 
            persist_directory=settings.CHROMA_PERSIST_DIRECTORY
        )
        logger.info(f"Data ingestion complete. Vector store saved to {settings.CHROMA_PERSIST_DIRECTORY}")
    except Exception as e:
        logger.error(f"Failed to create vector store: {e}")

if __name__ == "__main__":
    ingest_data()
