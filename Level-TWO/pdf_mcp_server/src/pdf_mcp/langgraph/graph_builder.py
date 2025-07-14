from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START
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
    done: bool

llm = ChatOpenAI(model="gpt-4", temperature=0.2)  

# Set up MCP tool execution
mcp_url = "http://localhost:8000"
tool_executor = MCPToolExecutor.from_url(mcp_url)
agent = ToolCallingAgent.from_executor(tool_executor, llm=llm)

# LLM Orchestration Node
def llm_node(state: State):
    messages = [
        SystemMessage(content="You are a smart assistant. Plan the best action or tool."),
        HumanMessage(content=state["query"])
    ]
    response = llm.invoke(messages)
    return {
        "messages": messages + [response],
        "agent_output": response,
        "done": False
    }

# Agent Tool Planner 
def tool_calling_llm(state: State):
    messages = state.get("messages") or [HumanMessage(content=state["query"])]
    result = agent.invoke({"messages": messages})
    return {
        "messages": messages + [result],
        "agent_output": result,
        "done": isinstance(result, AgentFinish)
    }

# Tool Execution Node 
def tool_call_node(state: State):
    if state["done"]:
        return state
    result = tool_executor.invoke_tool(state["agent_output"].tool_calls[0])
    return {
        "messages": state["messages"] + [result],
        "agent_output": result,
        "done": False
    }

# ───── Build Graph ─────
def build_graph():
    builder = StateGraph(State)
    builder.add_node("llm_node", RunnableLambda(llm_node))
    builder.add_node("tool_calling_llm", RunnableLambda(tool_calling_llm))
    builder.add_node("tool_call", RunnableLambda(tool_call_node))

    builder.add_edge(START, "llm_node")
    builder.add_edge("llm_node", "tool_calling_llm")
    builder.add_edge("tool_calling_llm", "tool_call")
    builder.add_conditional_edges("tool_call", lambda state:
        "tool_calling_llm" if not state["done"] else "tool_calling_llm"
    )

    builder.set_finish_point("tool_calling_llm")
    return builder.compile()
