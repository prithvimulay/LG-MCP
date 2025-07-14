from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.agents import AgentFinish
from langchain_openai import ChatOpenAI 
from langchain_mcp_adapters.tool_agent import ToolCallingAgent
from langchain_mcp_adapters.tool_executor import MCPToolExecutor

class State(TypedDict):
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    agent_output: AnyMessage
    final_output: Optional[str]
    done: bool

llm = ChatOpenAI(model="gpt-4", temperature=0.2)  

# Set up MCP tool execution
mcp_url = "http://localhost:5001"  # Updated to correct port
tool_executor = MCPToolExecutor.from_url(mcp_url)

# Create agent with detailed instructions
system_prompt = """
You are a specialized assistant with access to PDF documents. Your task is to answer queries ONLY using information from these documents and not from your general knowledge.

For ALL queries, ALWAYS follow this exact process:

1. FIRST use select_relevant_pdf_tool to find the most relevant PDF for the query
2. THEN use retrieve_from_pdf_tool with the selected PDF name to get specific information
3. ONLY use the retrieved information to answer the query

IMPORTANT: Do NOT provide answers based on your general knowledge. If you cannot find relevant information in the PDFs, explain that you couldn't find information about the topic in the available documents.

Available tools:
- select_relevant_pdf_tool: Returns the most relevant PDF filename based on the query
- retrieve_from_pdf_tool: Gets information from a PDF (requires pdf_filename and query parameters)
- list_pdfs_tool: Lists all available PDFs
- db_status_tool: Shows the status of the PDF database

Your response should be well-structured and directly address the user's query based ONLY on the information retrieved from PDFs.
"""

agent = ToolCallingAgent.from_executor(
    tool_executor, 
    llm=llm,
    system_message=system_prompt
)

# Agent Tool Planning and Execution Node 
def agent_node(state: State):
    # Initialize messages if this is the first step
    if "messages" not in state or not state["messages"]:
        messages = [
            HumanMessage(content=state["query"])
        ]
    else:
        messages = state["messages"]
    
    # Invoke agent with messages
    result = agent.invoke({"messages": messages})
    
    # Check if the agent is finished
    is_done = isinstance(result, AgentFinish)
    
    # If agent is done, extract the final output
    final_output = None
    if is_done:
        final_output = result.content
    
    return {
        "messages": messages + [result],
        "agent_output": result,
        "final_output": final_output,
        "done": is_done
    }

# ───── Build Graph ─────
def build_graph():
    builder = StateGraph(State)
    
    # Add the agent node that handles tool calling
    builder.add_node("agent", RunnableLambda(agent_node))
    
    # Start with the agent node
    builder.add_edge(START, "agent")
    
    # Create a loop: if not done, go back to agent; if done, finish
    builder.add_conditional_edges(
        "agent",
        lambda state: END if state["done"] else "agent"
    )
    
    return builder.compile()
