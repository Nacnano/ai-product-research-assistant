import pandas as pd
from langchain_community.document_loaders import DataFrameLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from src.core.config import settings
import os
import shutil

def ingest_data():
    """
    Ingests product data from CSV, chunks it, generates embeddings, 
    and stores it in ChromaDB.
    """
    print(f"Loading data from {settings.DATA_PATH}...")
    
    # 1. Load Data
    try:
        df = pd.read_csv(settings.DATA_PATH)
    except FileNotFoundError:
        print(f"Error: File not found at {settings.DATA_PATH}")
        return

    # Prepare data for embedding - Create a 'page_content' column that combines relevant fields
    # We want the LLM to be able to search by name, category, brand, description, etc.
    df['page_content'] = df.apply(lambda x: f"Product ID: {x['product_id']}\nName: {x['product_name']}\nCategory: {x['category']}\nBrand: {x['brand']}\nPrice: ${x['current_price']}\nStock: {x['stock_quantity']}\nDescription: {x['description']}\nRating: {x['average_rating']}", axis=1)

    # 2. metadata
    # We keep structered fields as metadata for filtering
    # df = df[['product_id', 'product_name', 'category', 'brand', 'current_price', 'stock_quantity', 'average_rating', 'page_content']]
    
    loader = DataFrameLoader(df, page_content_column="page_content")
    documents = loader.load()
    
    print(f"Loaded {len(documents)} documents.")

    # 3. Chunking (Optional for small descriptions, but good practice)
    # Since our 'documents' are already logical distinct units (products), aggressive chunking might split a product definition.
    # However, if description is long, we might need it. 
    # For this assignment, 1 product = 1 document is likely best to keep context together.
    # We will use a large chunk size just to be safe, essentially no-op splitting unless huge.
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    
    print(f"Prepared {len(texts)} text chunks.")

    # 4. Embeddings & Vector Store
    # Switching to FastEmbed for speed (no heavy Torch dependency)
    from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
    embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")

    # Clear existing DB if we are doing a full refresh (Simple Monthly Update Strategy)
    # For a real system update, we would check for diffs.
    if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        print("Clearing existing vector store for full refresh...")
        shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)

    print("Creating vector store...")
    db = Chroma.from_documents(
        headers=None,
        documents=texts, 
        embedding=embeddings, 
        persist_directory=settings.CHROMA_PERSIST_DIRECTORY
    )
    
    print(f"Data ingestion complete. Vector store saved to {settings.CHROMA_PERSIST_DIRECTORY}")

if __name__ == "__main__":
    ingest_data()
