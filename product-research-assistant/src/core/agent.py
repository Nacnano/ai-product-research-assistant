"""
AI Agent module for intelligent query routing and tool orchestration.

This module implements the core agent logic that:
- Analyzes user queries
- Routes queries to appropriate tools (RAG, Web Search, Price Analysis)
- Orchestrates multi-tool  workflows
- Provides reasoning for tool selection

Supports multiple LLM providers (OpenAI, Google Gemini) with a factory pattern.
"""
import logging
from typing import Any

from langchain.agents import create_tool_calling_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.tools.analysis import price_analysis
from src.tools.rag import product_catalog_rag
from src.tools.search import web_search

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def get_llm() -> BaseChatModel:
    """
    Factory function to initialize and return the configured LLM.
    
    Selects the appropriate LLM provider based on settings.LLM_PROVIDER.
    Supports multiple providers to offer flexibility in model choice.
    
    Returns:
        BaseChatModel: Initialized  LangChain chat model (Google Gemini or OpenAI)
    
    Raises:
        ValueError: If LLM_PROVIDER is unsupported or required API key is missing
        
    Supported Providers:
        - "google": Google Gemini 2.0 Flash (gemini-2.0-flash-exp)
        - "openai": OpenAI GPT-4 (gpt-4o)
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            error_msg = "GOOGLE_API_KEY is required when LLM_PROVIDER='google'"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp", 
            google_api_key=settings.GOOGLE_API_KEY, 
            temperature=0,  # Deterministic responses for consistency
            max_retries=10,  # Robust retry logic for API failures
            convert_system_message_to_human=True  # Required for Gemini compatibility
        )
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            error_msg = "OPENAI_API_KEY is required when LLM_PROVIDER='openai'"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        return ChatOpenAI(
            model="gpt-4o", 
            temperature=0,  # Deterministic responses for consistency
            openai_api_key=settings.OPENAI_API_KEY
        )
    else:
        error_msg = f"Unsupported LLM_PROVIDER: '{provider}'. Must be 'google' or 'openai'"
        logger.error(error_msg)
        raise ValueError(error_msg)

def get_agent_executor() -> Any:
    """
    Initialize and return an agent executor with configured tools and LLM.
    
    This function creates a custom agent executor that wraps the LangChain agent
    for better compatibility and control. The agent has access to three main tools:
    - product_catalog_rag: For internal product queries
    - web_search: For external market intelligence
    - price_analysis: For deterministic margin calculations
    
    Returns:
        SimpleAgentExecutor: Custom agent executor with tool orchestration logic
        
    Raises:
        Exception: If LLM initialization fails
    """
    # Initialize the three core tools
    tools = [product_catalog_rag, web_search, price_analysis]

    # Initialize the configured LLM (Google Gemini or OpenAI)
    try:
        llm = get_llm()
        logger.info(f"Successfully initialized LLM: {settings.LLM_PROVIDER}")
    except Exception as e:
        logger.critical(f"Failed to initialize LLM: {e}")
        raise

    # Define the agent's system prompt with clear instructions
    messages = [
        ("system", 
         "You are an expert AI Product Research Assistant for an e-commerce product management team.\n"
         "Your goal is to provide data-driven insights for product stocking, pricing, and market trend analysis.\n\n"
         "You have access to the following tools:\n\n"
         "1. **product_catalog_rag**: Use this to find information about internal products including:\n"
         "   - Product availability and stock levels\n"
         "   - Current prices and cost data\n"
         "   - Product descriptions and specifications\n"
         "   - Customer ratings and reviews\n"
         "   - Filtering by category, brand, or other attributes\n"
         "   ALWAYS check this first for questions about inventory.\n\n"
         "2. **web_search**: Use this to find external market information including:\n"
         "   - Current market prices and competitor pricing\n"
         "   - Product reviews and consumer sentiment\n"
         "   - Market trends and industry insights\n"
         "   Use when external data is needed for competitive analysis.\n\n"
         "3. **price_analysis**: Use this for precise profit margin calculations.\n"
         "   - Calculates: ((price - cost) / price) × 100\n"
         "   - Do NOT do math calculations yourself - always use this tool for accuracy.\n\n"
         "**Decision Logic & Routing:**\n"
         "- For pricing or margin questions: First get internal price/cost data (product_catalog_rag), "
         "then use price_analysis for calculations.\n"
         "- For competitive analysis: Get internal product details (product_catalog_rag), "
         "then search for competitor information (web_search).\n"
         "- For market trends: Use web_search to gather external intelligence.\n"
         "- Always provide sources or explain your reasoning.\n"
         "- Be concise, data-driven, and professional in your responses."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
    
    prompt = ChatPromptTemplate.from_messages(messages)

    # Create the tool-calling agent with LLM and tools
    agent = create_tool_calling_agent(llm, tools, prompt)

    class SimpleAgentExecutor:
        """
        Custom agent executor for orchestrating tool calls and managing agent execution.
        
        This class wraps the LangChain agent with custom execution logic to ensure
        compatibility and provide better control over the agent's behavior.
        
        Attributes:
            agent: The LangChain tool-calling agent
            tools: Dictionary mapping tool names to tool objects
            verbose: Whether to log execution details
        """
        
        def __init__(self, agent, tools):
            """
            Initialize the agent executor.
            
            Args:
                agent: LangChain tool-calling agent
                tools: List of available tools
            """
            self.agent = agent
            self.tools = {t.name: t for t in tools}
            self.verbose = True

        def invoke(self, inputs: dict):
            """
            Execute the agent with the given inputs.
            
            Runs the agent in a loop, executing tools as needed until:
            - The agent provides a final answer (AgentFinish)
            - Maximum iterations are reached
            - An error occurs
            
            Args:
                inputs: Dictionary with "input" key containing the user's query
                
            Returns:
                dict: Dictionary with "output" key containing the agent's response
            """
            steps = []
            max_steps = 8  # Prevent infinite loops
            
            for i in range(max_steps):
                try:
                    # Invoke agent with current input and intermediate steps
                    output = self.agent.invoke({
                        "input": inputs["input"], 
                        "intermediate_steps": steps
                    })
                except Exception as e:
                    logger.error(f"Error during agent invocation at step {i+1}: {e}")
                    return {
                        "output": f"I apologize, but I encountered an error: {str(e)}"
                    }
                
                # Check if agent has finished (AgentFinish)
                if not isinstance(output, list) and "AgentFinish" in str(type(output)):
                    return {"output": output.return_values["output"]}

                # Handle tool actions (may be list or single action)
                actions = output if isinstance(output, list) else [output]
                
                for action in actions:
                    # Check again for AgentFinish in action list
                    if "AgentFinish" in str(type(action)):
                        return {"output": action.return_values["output"]}

                    tool_name = action.tool
                    tool_input = action.tool_input
                    
                    if self.verbose:
                        logger.info(f"→ Calling tool: '{tool_name}' with input: {str(tool_input)[:100]}...")
                    
                    # Execute the requested tool
                    tool_obj = self.tools.get(tool_name)
                    if tool_obj:
                        try:
                            observation = tool_obj.invoke(tool_input)
                            if self.verbose:
                                logger.info(f"← Tool result: {str(observation)[:150]}...")
                        except Exception as e:
                            observation = f"Error executing tool '{tool_name}': {e}"
                            logger.error(observation)
                    else:
                        observation = f"Error: Tool '{tool_name}' not found in available tools."
                        logger.error(observation)
                    
                    # Store the action and its result for next iteration
                    steps.append((action, observation))
            
            # Reached max iterations without finishing
            logger.warning(f"Agent stopped after {max_steps} iterations without finishing")
            return {"output": "I apologize, but I need more steps to complete this request. Please try a more specific question."}

    # Create and return the custom executor
    agent_executor = SimpleAgentExecutor(agent, tools)
    logger.info("Agent executor initialized successfully")
    
    return agent_executor
