from langchain_community.vectorstores import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.tools import tool
from src.core.config import settings

def get_retriever():
    """
    Returns a retriever for the product catalog.
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
    Useful for answering questions about product availability, stock, prices, descriptions, 
    and ratings from the internal product catalog. 
    Use this tool when you need to look up specific product details or list products.
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    if not docs:
        return "No relevant products found in the catalog."
    
    result = ""
    for doc in docs:
        result += f"{doc.page_content}\n---\n"
    
    return result
