from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq

from tools.wiki_tool import wiki_tool
from tools.tavily_tool import tavily_tool
from tools.pdf_tool import pdf_tool
from tools.youtube_tool import pickleball_youtube

# Tools list
tools = [wiki_tool, tavily_tool, pdf_tool, pickleball_youtube]

# State schema inheriting from MessagesState (includes messages field with add_messages reducer)
class State(MessagesState):
    pass  # Inherits messages field with add_messages reducer automatically

# Initialize LLM with bound tools
llm = ChatGroq(model="qwen-qwq-32b").bind_tools(tools=tools)

def tool_calling_llm(state: State):
    """
    LLM node that processes user messages and decides whether to call tools.
    Uses state["messages"] directly - no manual memory management needed.
    """
    user_message = state["messages"][-1]
    print(f"\n[User Message]: {user_message.content}")

    # Pass the full conversation history from state to LLM
    # State automatically manages conversation continuity
    llm_response = llm.invoke(state["messages"])
    print(f"[LLM Response]: {llm_response.content}")

    return {"messages": [llm_response]}

def summarizer_llm(state: State):
    """
    Summarizes tool output and provides user-friendly responses.
    State management handles message persistence automatically.
    """
    tool_output = state["messages"][-1]
    print(f"\n[Tool Output Received]: {tool_output}")

    if hasattr(tool_output, "tool_call"):
        tool_name = tool_output.tool_call.get("name", "unknown_tool")
        tool_args = tool_output.tool_call.get("arguments", {})
        
        summary_prompt = (
            f"A tool was invoked with:\n"
            f"Tool: {tool_name}\nArguments: {tool_args}\n"
            f"Summarize for the user."
        )
        summary = llm.invoke(summary_prompt)
    else:
        safe_text = getattr(tool_output, "content", "")
        if not safe_text or not isinstance(safe_text, str):
            safe_text = "No readable content."
        summary = llm.invoke(safe_text)

    print(f"[Summarized Output for User]: {summary.content}")
    return {"messages": [summary]}

def build_graph():
    """
    Builds the LangGraph workflow with proper state management and persistence.
    """
    # Create StateGraph with MessagesState-based schema
    builder = StateGraph(State)

    # Add nodes to the graph
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("summarizer_llm", summarizer_llm)

    # Define graph edges and control flow
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "summarizer_llm")
    builder.add_edge("summarizer_llm", "tool_calling_llm")

    # Initialize InMemorySaver for state persistence and conversation continuity
    my_saver = InMemorySaver()

    # Compile graph with checkpointer for durable execution
    return builder.compile(checkpointer=my_saver)
