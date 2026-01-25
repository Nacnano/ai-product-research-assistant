import logging
from typing import List, Any

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from src.core.config import settings
from src.tools.rag import product_catalog_rag
from src.tools.search import web_search
from src.tools.analysis import price_analysis

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def get_llm() -> BaseChatModel:
    """
    Factory function to return the configured LLM based on settings.
    
    Returns:
        BaseChatModel: Configured LangChain chat model.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            logger.error("GOOGLE_API_KEY is missing but LLM_PROVIDER is set to 'google'.")
            raise ValueError("GOOGLE_API_KEY is missing.")
            
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            google_api_key=settings.GOOGLE_API_KEY, 
            temperature=0,
            convert_system_message_to_human=True 
        )
    elif provider == "openai":
        return ChatOpenAI(
            model="gpt-4o", 
            temperature=0, 
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        logger.error(f"Unsupported LLM_PROVIDER: {provider}")
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

def get_agent_executor() -> AgentExecutor:
    """
    Initializes and returns an AgentExecutor with the configured tools and LLM.
    
    Returns:
        AgentExecutor: The executable agent.
    """
    # Initialize Tools
    tools = [product_catalog_rag, web_search, price_analysis]

    # Initialize LLM
    try:
        llm = get_llm()
    except Exception as e:
        logger.critical(f"Failed to initialize LLM: {e}")
        raise e

    # Define Prompt
    messages = [
        ("system", 
         "You are an expert AI Product Research Assistant for an e-commerce team. "
         "Your goal is to help with product research, market trend analysis, and pricing decisions.\n"
         "You have access to the following tools:\n"
         "- `product_catalog_rag`: Use this to find information about our internal products (stock, price, description, etc.). "
         "Always check this first if the query is about our inventory.\n"
         "- `web_search`: Use this to find external market data, competitor prices, and trends.\n"
         "- `price_analysis`: Use this to calculate profit margins precisely. Do not do math in your head.\n\n"
         "Logic & Routing:\n"
         "- If asked about effective pricing or margins, first get the internal price/cost, then use `price_analysis`.\n"
         "- If asked to compare with competitors, use `product_catalog_rag` to get our product details, then `web_search` to find competitors.\n"
         "- Always provide sources or reasoning for your answers.\n"
         "- Be concise and professional."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
    
    prompt = ChatPromptTemplate.from_messages(messages)

    # Create Agent
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create Executor
    # Using standard AgentExecutor for robust error handling and loop management
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor
