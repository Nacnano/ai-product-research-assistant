from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from src.core.config import settings
from src.tools.rag import product_catalog_rag
from src.tools.search import web_search
from src.tools.analysis import price_analysis

def get_llm():
    """
    Factory function to return the configured LLM.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "google":
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is missing but LLM_PROVIDER is set to 'google'.")
        return ChatGoogleGenerativeAI(
            model="gemini-pro", 
            google_api_key=settings.GOOGLE_API_KEY, 
            temperature=0,
            convert_system_message_to_human=True # Gemini Pro often handles system messages better as human input
        )
    elif provider == "openai":
        if not settings.OPENAI_API_KEY:
            # Fallback warning or error, but let's assume user might want to try running without key until hit
            pass 
        return ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=settings.OPENAI_API_KEY)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")

def get_agent_executor():
    """
    Returns an AgentExecutor configured with tools and LLM.
    """
    # 1. Initialize Tools
    tools = [product_catalog_rag, web_search, price_analysis]

    # 2. Initialize LLM
    try:
        llm = get_llm()
    except Exception as e:
        print(f"Error initializing LLM: {e}")
        # Return a dummy or fail gracefully if needed, but for now let's raise
        raise e

    # 3. Define Prompt
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

    # 4. Create Agent definition
    agent = create_tool_calling_agent(llm, tools, prompt)

    # 5. Custom Executor to avoid ImportError or version issues
    class SimpleAgentExecutor:
        def __init__(self, agent, tools):
            self.agent = agent
            self.tools = {t.name: t for t in tools}
            self.verbose = True

        def invoke(self, inputs: dict):
            # Basic loop
            steps = []
            max_steps = 5
            
            # Start loop
            for i in range(max_steps):
                # Invoke agent with current inputs + steps
                # agent input usually needs: input, agent_scratchpad
                # but create_tool_calling_agent expects 'intermediate_steps' variable (list of (action, observation))
                
                # Format steps for agent
                # LangChain tool calling agent expects intermediate_steps
                
                output = self.agent.invoke({
                    "input": inputs["input"], 
                    "intermediate_steps": steps
                })
                
                # Output is either AgentAction (or list of them) or AgentFinish
                if isinstance(output, list):
                    actions = output
                else:
                    # It might be AgentFinish or single Action
                    if hasattr(output, "return_values"): 
                        # AgentFinish
                        return {"output": output.return_values["output"]}
                    actions = [output]

                # If it's AgentFinish (which is not a list)
                if not isinstance(output, list) and "AgentFinish" in str(type(output)):
                     return {"output": output.return_values["output"]}

                # Execute actions
                for action in actions:
                    if "AgentFinish" in str(type(action)):
                        return {"output": action.return_values["output"]}
                        
                    tool_name = action.tool
                    tool_input = action.tool_input
                    
                    if self.verbose:
                        print(f"Calling Tool: {tool_name} with {tool_input}")
                    
                    tool_obj = self.tools.get(tool_name)
                    if tool_obj:
                        observation = tool_obj.invoke(tool_input)
                    else:
                        observation = f"Error: Tool {tool_name} not found."
                    
                    if self.verbose:
                         print(f"Tool Output: {str(observation)[:200]}...")

                    steps.append((action, observation))
            
            return {"output": "Agent stopped due to max iterations."}

    # 5. Create Executor
    # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    agent_executor = SimpleAgentExecutor(agent, tools)
    
    return agent_executor
