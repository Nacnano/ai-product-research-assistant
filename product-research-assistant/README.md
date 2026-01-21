# AI Product Research Assistant

An intelligent agentic AI system designed to assist product management teams with research, market trend analysis, and pricing decisions.

## Features

- **Product Catalog RAG**: Answers questions about internal inventory using Vector Search (ChromaDB).
- **Web Search**: Retrieves real-time market data (Competitor pricing, trends). _Note: Configured with a Mock provider by default._
- **Price Analysis**: deterministic margin calculations.
- **AI Agent**: Intelligent routing using LangChain's ReAct/Tool-calling capabilities.

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **AI/LLM**: LangChain, OpenAI (`gpt-4o` / `gpt-3.5-turbo`)
- **Vector DB**: ChromaDB (Local)
- **Embeddings**: `FastEmbed` (BAAI/bge-small-en-v1.5) - Local ONNX-based.
- **Infrastructure**: Docker

## Setup & Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional but recommended)
- OpenAI API Key
- Google Gemini API Key

### 1. Environment Setup

Clone the repository and create a virtual environment:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file (copy from `.env.example`) and add your API Keys:

```env
# For OpenAI
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai

# For Google Gemini
GOOGLE_API_KEY=AIza...
LLM_PROVIDER=google
```

### 3. Data Ingestion

Load the product catalog into the vector database:

```bash
# From root directory
python -m src.ingest
```

_Note: This uses local embeddings (FastEmbed), so no API cost is incurred for ingestion._

## Running the Application

### Local (Python)

Start the FastAPI server:

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Docker

Build and run with Docker Compose:

```bash
docker-compose up --build
```

## Testing the API

Use `curl` or Postman to query the agent.

**Example 1: Internal Product Search**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What wireless headphones do we have in stock?"}'
```

**Example 2: Market Research (Web Search)**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Current market price for noise-cancelling headphones?"}'
```

**Example 3: Price Analysis**

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Calculate margin for a product with price $100 and cost $60"}'
```

**Example 4: Health Check**

```bash
curl http://localhost:8000/health
```

## Limitations & Future Improvements

### Current Limitations

- **Web Search Mock**: The search tool uses mock data by default to verify functionality without requiring a Serper/Tavily API key. It can be switched to real API in `src/tools/search.py`.
- **Memory**: Vector DB is persisted locally on disk (`data/chroma_db`).
- **History**: Conversation history is not stored in a persistent relational DB yet.

### Future Improvements

- **Live Search**: Enable real web search integration.
- **Caching**: Implement Redis caching for frequent queries.
- **Frontend**: Build a React/Next.js dashboard.
- **Authentication**: Add JWT auth for the API.
