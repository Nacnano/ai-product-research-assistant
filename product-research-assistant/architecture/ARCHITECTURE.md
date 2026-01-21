# System Architecture

## Overview

The AI Product Research Assistant is a modular, agentic AI system designed to assist with product research, market analysis, and pricing. It typically intakes user questions, routes them to specific tools (RAG, Web Search, Price Analysis), and aggregates the results.

## Components

### 1. Data Ingestion Pipeline

- **Source:** `products_catalog.csv` (CSV File)
- **Processing:**
  - **Loader:** Pandas DataFrame Loader
  - **Chunking:** Character Text Splitter (One product per chunk usually sufficient)
  - **Embeddings:** `FastEmbedEmbeddings` (Local, BAAI/bge-small-en-v1.5) to avoid API costs/limits.
  - **Store:** `ChromaDB` (Local Vector Store)
- **Updates:**
  - Currently implemented as a full re-index on running `ingest.py`.
  - **Monthly Update Strategy:** Since the catalog changes monthly, a scheduled cron job would run the ingestion script. For optimization, we could implement a checksum comparison of rows to only embed new/changed products.

### 2. AI Agent

- **Framework:** LangChain (ReAct / Tool-calling Agent)
- **LLM:** OpenAI `gpt-4o` (or `gpt-3.5-turbo`)
- **Routing:** The agent autonomously decides which tool to call based on the user query description.

### 3. Tools

- **Product Catalog RAG:** Retrieves product details from ChromaDB.
- **Web Search:** Uses Mock data (default) or Serper/Tavily API for external data.
- **Price Analysis:** Deterministic Python function for margin calculations.

### 4. API Layer

- **Framework:** FastAPI
- **Endpoints:**
  - `POST /query`: Main interface.
  - `GET /health`: Health check.

## Scalability & Production Considerations

- **Latency:**
  - Local embeddings (FastEmbed) are fast but CPU bound.
  - Vector search in Chroma is fast for small datasets (1000s of items). For millions, we would switch to Qdrant or Pinecone.
- **Concurrency:**
  - FastAPI handles async requests multiple well.
  - The bottleneck is likely LLM API latency. Streaming responses (Server-Sent Events) would improve perceived latency.
- **Security:**
  - API Key authentication should be added for the REST API.
  - LLM inputs should be sanitized to prevent prompt injection (though less critical for internal tools).

## Limitations

- **Mock Search:** Web search is mocked by default to ensure runnability without external keys.
- **Memory:** The vector DB is loaded into memory (Chroma default). Large datasets might require a server-based vector DB.
- **History:** Chat history is not currently persisted in a database (in-memory only for the session).
