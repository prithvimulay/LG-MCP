from typing import TypedDict, Annotated, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
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

# Setup 
llm = ChatOpenAI(model="gpt-4", temperature=0.2)
mcp_url = "http://localhost:5001"
tool_executor = MCPToolExecutor.from_url(mcp_url)
agent = ToolCallingAgent.from_executor(tool_executor, llm=llm)

# Initial LLM Planning 
def llm_node(state: State):
    messages = [
        SystemMessage(content="""You are an advanced PDF assistant with specialized tools for document analysis and content generation.
        
        AVAILABLE TOOLS:
        - retrieve_from_pdf_tool: Use when you need to extract specific information from a PDF based on a query. Requires exact PDF filename and a clear search query.
        - generate_podcast_tool: Use when creating audio content or summaries based on PDF content. Requires PDF filename and podcast topic.
        - select_relevant_pdf_tool: Use when the user hasn't specified which PDF to use. This will find the most relevant PDF based on the query.
        - list_pdfs_tool: Use when you need to see all available PDFs in the system or when the user asks what documents are available.
        - db_status_tool: Use to check the vector database status, including which PDFs are indexed and their chunk counts.
        
        TOOL SELECTION GUIDELINES:
        1. Always check if PDFs exist first using list_pdfs_tool when a request mentions PDFs but doesn't specify a filename.
        2. Use select_relevant_pdf_tool when the user query relates to content but doesn't specify which PDF to use.
        3. For information extraction, use retrieve_from_pdf_tool with specific questions about PDF content.
        4. For content generation or summarization tasks, use generate_podcast_tool.
        5. Check database status with db_status_tool if you need to verify which PDFs are indexed.
        
        Carefully analyze the user's request to determine the most appropriate tool and required parameters."""),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(messages)
    return {
        "messages": messages + [response],
        "agent_output": response,
        "final_output": None,
        "done": False
    }

# Agent Tool Planner 
def tool_calling_llm(state: State):
    messages = state.get("messages") or [HumanMessage(content=state["query"])]
    result = agent.invoke({"messages": messages})
    is_done = isinstance(result, AgentFinish)
    return {
        "messages": messages + [result],
        "agent_output": result,
        "final_output": result.content if is_done else None,
        "done": is_done
    }

# Tool Executor 
def tool_call_node(state: State):
    if state["done"]:
        return state
    result = tool_executor.invoke_tool(state["agent_output"].tool_calls[0])
    return {
        "messages": state["messages"] + [result],
        "agent_output": result,
        "final_output": None,
        "done": False
    }

# Graph Builder 
def build_graph():
    builder = StateGraph(State)
    builder.add_node("llm_node", RunnableLambda(llm_node))
    builder.add_node("tool_calling_llm", RunnableLambda(tool_calling_llm))
    builder.add_node("tool_call", RunnableLambda(tool_call_node))

    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", "tool_calling_llm")
    builder.add_edge("tool_calling_llm", "tool_call")

    # Conditional looping based on completion
    builder.add_conditional_edges("tool_call", lambda state:
        "tool_calling_llm" if not state["done"] else "tool_calling_llm"
    )

    builder.set_finish_point("tool_calling_llm")
    return builder.compile()
