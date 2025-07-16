from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.tools import tool
# Not using async load_mcp_tools
# from langchain_mcp_adapters.tools import load_mcp_tools
from pdf_mcp.mcp.tools_impl import TOOLS  # Use our predefined tools
import logging
import requests
import json
import re
from pdf_mcp.mcp.prompts_impl import PROMPTS
from pdf_mcp.config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State(TypedDict):
    """Simple state for the workflow."""
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    final_output: Optional[str]
    branch: str  # Either 'tool' or 'prompt'
    prompt_name: Optional[str]
    prompt_args: Optional[Dict[str, Any]]

# Setup
llm = ChatOpenAI(
    model="gpt-4", 
    temperature=0.2,
    openai_api_key=settings.openai_api_key
)
mcp_url = "http://localhost:5001"

# Create langchain tools from our MCP tools
from langchain_core.tools import Tool as LangchainTool

langchain_tools = []
for tool in TOOLS:
    langchain_tools.append(
        LangchainTool(
            name=tool.name,
            description=tool.description,
            func=lambda **kwargs: f"Simulated response for {kwargs}",  # Placeholder implementation
        )
    )

# Create agent
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can analyze PDFs."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = {
    "input": lambda x: x["input"],
    "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"])
} | prompt | llm | OpenAIFunctionsAgentOutputParser()

agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True)

# Function to fetch prompt results via MCP API
def fetch_prompt(prompt_name: str, args: Dict[str, Any]) -> str:
    """Fetch prompt result from MCP API"""
    try:
        # Call MCP prompt endpoint
        response = requests.post(
            f"{mcp_url}/prompt/{prompt_name}",
            json=args
        )
        
        if response.status_code == 200:
            return response.json().get("response", "No response from prompt.")
        else:
            return f"Error from prompt endpoint: {response.status_code}"
    except Exception as e:
        return f"Error calling prompt: {str(e)}"

# No longer needed with the new agent setup above

# Decision node - determines whether to use tool or prompt
def decision_node(state: State) -> Dict:
    """Decides whether to use a tool or prompt based on the query."""
    query = state["query"]
    
    # Create a description of available prompts
    prompts_info = ""
    for name, prompt in PROMPTS.items():
        args = ", ".join([arg.name for arg in prompt.arguments if arg.required])
        optional_args = ", ".join([arg.name for arg in prompt.arguments if not arg.required])
        prompt_desc = f"- {name}: {prompt.description}\n  Required args: {args}"
        if optional_args:
            prompt_desc += f"\n  Optional args: {optional_args}"
        prompts_info += prompt_desc + "\n"
    
    # Simple system message that relies on built-in prompt/tool descriptions
    system_message = f"""You are a PDF assistant that can either use tools or pre-built prompts.
Based on the user's query, decide which approach would be more effective.

AVAILABLE PROMPTS:
{prompts_info}

Prompts are ideal for standard operations like PDF summarization, key point extraction,
document structure analysis, or podcast script generation.

Tools are better for custom retrieval, list operations, database status checks, or
when you need more flexibility.

Respond with JSON: {"branch": "tool"} or {"branch": "prompt", "prompt_name": "name", "prompt_args": {"arg1": "value1", ...}}
"""
    
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=query)
    ]
    
    # Get LLM decision
    response = llm.invoke(messages)
    
    # Extract decision from response
    branch = "tool"  # Default to tool
    prompt_name = None
    prompt_args = {}
    
    try:
        # Look for JSON in the response
        json_match = re.search(r'\{.*?"branch".*?\}', response.content, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group(0))
            branch = decision.get("branch", "tool")
            prompt_name = decision.get("prompt_name")
            prompt_args = decision.get("prompt_args", {})
    except Exception as e:
        logger.error(f"Error parsing decision: {str(e)}")
    
    # Add explanation message
    if branch == "prompt" and prompt_name:
        explanation = f"I'll use the {prompt_name} prompt to process your request."
    else:
        explanation = "I'll use specialized tools to process your request."
    
    return {
        "query": query,
        "messages": state["messages"] + [AIMessage(content=explanation)],
        "final_output": None,
        "branch": branch,
        "prompt_name": prompt_name,
        "prompt_args": prompt_args
    }

# Tool branch - handles tool selection and execution
def tool_branch(state: State) -> Dict:
    """Uses tools to process the query."""
    messages = state["messages"]
    
    # Use LangChain agent for tool calling
    try:
        result = agent_executor.invoke({"input": state["query"], "chat_history": messages})
    except Exception as e:
        # Log error and return a fallback response
        logger.error(f"Error in tool execution: {str(e)}")
        result = {"output": f"I encountered an error while processing your request: {str(e)}"}
    result_content = result.get("output", "No response generated.")
    
    return {
        "query": state["query"],
        "messages": state["messages"] + [AIMessage(content=result_content)],
        "final_output": result_content,
        "branch": state["branch"],
        "prompt_name": state["prompt_name"],
        "prompt_args": state["prompt_args"]
    }

# Prompt branch - calls MCP prompt
def prompt_branch(state: State) -> Dict:
    """Calls the appropriate MCP prompt with arguments."""
    prompt_name = state["prompt_name"]
    prompt_args = state["prompt_args"]
    
    if not prompt_name:
        return {
            "query": state["query"],
            "messages": state["messages"] + [AIMessage(content="Error: No prompt selected.")],
            "final_output": "Error: No prompt selected.",
            "branch": state["branch"],
            "prompt_name": None,
            "prompt_args": None
        }
    
    try:
        # Call MCP prompt endpoint
        response = requests.post(
            f"{mcp_url}/prompt/{prompt_name}",
            json=prompt_args
        )
        
        if response.status_code == 200:
            result = response.json().get("response", "No response from prompt.")
            return {
                "query": state["query"],
                "messages": state["messages"] + [AIMessage(content=result)],
                "final_output": result,
                "branch": state["branch"],
                "prompt_name": prompt_name,
                "prompt_args": prompt_args
            }
        else:
            error = f"Error from prompt endpoint: {response.status_code}"
            return {
                "query": state["query"],
                "messages": state["messages"] + [AIMessage(content=error)],
                "final_output": error,
                "branch": state["branch"],
                "prompt_name": prompt_name,
                "prompt_args": prompt_args
            }
    except Exception as e:
        error = f"Error calling prompt: {str(e)}"
        return {
            "query": state["query"],
            "messages": state["messages"] + [AIMessage(content=error)],
            "final_output": error,
            "branch": state["branch"],
            "prompt_name": prompt_name,
            "prompt_args": prompt_args
        }

# Response formatting node
def response_formatter(state: State) -> Dict:
    """Uses LLM to format the final output for presentation."""
    # Get raw output from previous steps
    final_output = state["final_output"]
    query = state["query"]
    branch = state["branch"]
    prompt_name = state["prompt_name"]
    
    # Create formatting instruction for LLM
    if branch == "prompt" and prompt_name:
        format_instruction = f"""You are a helpful assistant tasked with formatting the output from a PDF processing system.  
The following is the raw output from the '{prompt_name}' prompt in response to this query: "{query}".

Please format this content in a clear, well-structured way. Add appropriate headings, bullet points, or other formatting elements to improve readability. Ensure the content is organized logically and presented in a polished, professional manner.

Raw output to format:
{final_output}"""
    else:
        format_instruction = f"""You are a helpful assistant tasked with formatting the output from a PDF processing system.
The following is the raw output from tool-based processing in response to this query: "{query}".

Please format this content in a clear, well-structured way. Add appropriate headings, bullet points, or other formatting elements to improve readability. Ensure the content is organized logically and presented in a polished, professional manner.

Raw output to format:
{final_output}"""
    
    # Get formatted response from LLM
    format_messages = [HumanMessage(content=format_instruction)]
    formatted_response = llm.invoke(format_messages)
    
    return {
        "query": state["query"],
        "messages": state["messages"] + [formatted_response],
        "final_output": formatted_response.content,
        "branch": state["branch"],
        "prompt_name": state["prompt_name"],
        "prompt_args": state["prompt_args"]
    }

# Build the graph
def build_graph():
    """Builds and returns the compiled StateGraph."""
    builder = StateGraph(State)
    
    # Add nodes
    builder.add_node("decision", RunnableLambda(decision_node))
    builder.add_node("tool_branch", RunnableLambda(tool_branch))
    builder.add_node("prompt_branch", RunnableLambda(prompt_branch))
    builder.add_node("response_formatter", RunnableLambda(response_formatter))
    
    # Add edges
    builder.add_edge(START, "decision")
    
    # Conditional edge based on decision
    builder.add_conditional_edges(
        "decision",
        lambda state: "prompt_branch" if state["branch"] == "prompt" else "tool_branch"
    )
    
    # Branches lead to formatter
    builder.add_edge("tool_branch", "response_formatter")
    builder.add_edge("prompt_branch", "response_formatter")
    
    # End at formatter
    builder.add_edge("response_formatter", END)
    
    return builder.compile()
