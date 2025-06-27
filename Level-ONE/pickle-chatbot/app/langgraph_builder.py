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
from tools.youtube_tool import youtube_tool

tools = [wiki_tool, tavily_tool, pdf_tool, youtube_tool]

memory = ConversationBufferMemory(return_messages=True)

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def tool_calling_llm(state: State):
    user_message = state["messages"][-1]

    memory.chat_memory.add_user_message(user_message)

    conversation_history = memory.load_memory_variables({})["history"]

    llm_response = llm.invoke(conversation_history)
    
    memory.chat_memory.add_ai_message(llm_response)

    return {"messages": [llm_response]}

llm = ChatGroq(model="qwen2-72b-chat").bind_tools(tools=tools)

def build_graph():
    builder = StateGraph(State)
    builder.add_node("tool_calling_llm", tool_calling_llm)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "tool_calling_llm")
    builder.add_conditional_edges("tool_calling_llm", tools_condition)
    builder.add_edge("tools", "tool_calling_llm")
    return builder.compile()
