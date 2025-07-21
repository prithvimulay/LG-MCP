from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq  # Changed from OpenAI
import json
import re
from pdf_mcp.mcp.mcp_client import get_mcp_client
from pdf_mcp.config.settings import settings

class State(TypedDict):
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    final_output: Optional[str]
    tool_name: Optional[str]
    tool_args: Optional[Dict[str, Any]]

llm = ChatGroq(
    model="llama3-70b-8192",
    temperature=0.2,
    groq_api_key=settings.groq_api_key
)

async def decision_node(state: State) -> Dict:
    """Select the best tool for the query"""
    query = state["query"]
    
    try:
        client = await get_mcp_client()
        tools = await client.get_tools()
        
        tools_info = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in tools
        ])
        
        system_message = f"""You are a PDF assistant. Select the best tool for this query.

AVAILABLE TOOLS:
{tools_info}

Respond with JSON: {{"tool_name": "exact_tool_name", "tool_args": {{"query": "query"}}}}

Query: {query}"""

        response = llm.invoke([
            SystemMessage(content=system_message), 
            HumanMessage(content=query)
        ])
        
        # Parse tool selection
        tool_name = "list_pdfs"  # Default
        tool_args = {"query": query}
        
        try:
            json_match = re.search(r'\{.*?"tool_name".*?\}', response.content, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group(0))
                tool_name = decision.get("tool_name", "list_pdfs")
                tool_args = decision.get("tool_args", {"query": query})
        except:
            pass
            
        return {
            "query": query,
            "messages": state["messages"] + [AIMessage(content=f"Using {tool_name}")],
            "final_output": None,
            "tool_name": tool_name,
            "tool_args": tool_args
        }
    except Exception as e:
        return {
            "query": query,
            "messages": state["messages"] + [AIMessage(content=f"Error: {e}")],
            "final_output": f"Error: {e}",
            "tool_name": None,
            "tool_args": {}
        }

async def tool_branch(state: State) -> Dict:
    """Execute the selected tool"""
    tool_name = state["tool_name"]
    tool_args = state["tool_args"]
    
    if not tool_name:
        output = "Error: No tool selected"
    else:
        try:
            client = await get_mcp_client()
            output = await client.call_tool(tool_name, tool_args)
        except Exception as e:
            output = f"Tool error: {e}"
    
    return {
        "query": state["query"],
        "messages": state["messages"] + [AIMessage(content=output)],
        "final_output": output,
        "tool_name": tool_name,
        "tool_args": tool_args
    }

def build_graph():
    """Build tools-only graph"""
    builder = StateGraph(State)
    
    builder.add_node("decision", RunnableLambda(decision_node))
    builder.add_node("tool_branch", RunnableLambda(tool_branch))
    
    builder.add_edge(START, "decision")
    builder.add_edge("decision", "tool_branch")
    builder.add_edge("tool_branch", END)
    
    return builder.compile()
