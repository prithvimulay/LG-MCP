from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_groq import ChatGroq
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages

from langchain.memory import ConversationBufferMemory

from tools.wiki_tool import wiki_tool
from tools.tavily_tool import tavily_tool
from tools.pdf_tool import pdf_tool
from tools.youtube_tool import pickleball_youtube

tools = [wiki_tool, tavily_tool, pdf_tool, pickleball_youtube]

memory = ConversationBufferMemory(return_messages=True)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

llm = ChatGroq(model="qwen-qwq-32b").bind_tools(tools=tools)

def tool_calling_llm(state: State):
    user_message = state["messages"][-1]
    print(f"\n[User Message]: {user_message.content}")
    memory.chat_memory.add_user_message(user_message)

    conversation_history = memory.load_memory_variables({})["history"]
    llm_response = llm.invoke(conversation_history)
    memory.chat_memory.add_ai_message(llm_response)

    print(f"[LLM Response]: {llm_response.content}")
    return {"messages": [llm_response]}

def summarizer_llm(state: State):
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
    return {"messages": [summary.content]}

def build_graph():
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    builder.add_node("summarizer_llm", summarizer_llm)
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "summarizer_llm")
    builder.add_edge("summarizer_llm", "tool_calling_llm")
    return builder.compile()
