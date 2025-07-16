from typing import TypedDict, Annotated, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_core.tools import Tool as LCTool
from fastmcp import Client as MCPClient
import asyncio
import logging
import json
import re
from pdf_mcp.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class State(TypedDict):
    query: str
    messages: Annotated[list[AnyMessage], add_messages]
    final_output: Optional[str]
    branch: str  
    prompt_name: Optional[str]
    prompt_args: Optional[Dict[str, Any]]

llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.2,
    openai_api_key=settings.openai_api_key
)

MCP_URL = "http://localhost:5001"

async def load_mcp_tools_and_prompts():
    tools = []
    
    try:
        async with MCPClient(MCP_URL) as client:
            tool_defs = await client.list_tools()
            
            for tool_meta in tool_defs:
                def create_tool_func(name):
                    return lambda **kwargs: asyncio.run(
                        async_call_tool(name, kwargs)
                    )
                
                tools.append(Tool(
                    name=tool_meta.name,
                    func=create_tool_func(tool_meta.name),
                    description=tool_meta.description,
                ))
            
            prompt_defs = await client.list_prompts()
            
            for prompt_meta in prompt_defs:
                def create_prompt_func(name):
                    return lambda **kwargs: asyncio.run(
                        async_call_prompt(name, kwargs)
                    )
                
                tools.append(Tool(
                    name=f"prompt_{prompt_meta.name}",
                    func=create_prompt_func(prompt_meta.name),
                    description=f"[Prompt] {prompt_meta.description}",
                ))
    except Exception as e:
        logger.error(f"Error loading tools and prompts: {e}")
        return []
        
    return tools

async def async_call_tool(name, args):
    async with MCPClient(MCP_URL) as client:
        result = await client.call_tool(name, args)
        return result.data

async def async_call_prompt(name, args):
    async with MCPClient(MCP_URL) as client:
        result = await client.call_prompt(name, args)
        return result.data

def create_agent():
    try:
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful PDF assistant that can analyze and extract information from PDFs."),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        tools = asyncio.run(load_mcp_tools_and_prompts())
        if not tools:
            logger.warning("No tools loaded, using fallback empty tools list")
            tools = []
            
        agent_chain = create_openai_functions_agent(llm, tools, prompt)
        return AgentExecutor(agent=agent_chain, tools=tools, verbose=True)
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        from langchain_core.prompts import ChatPromptTemplate
        fallback_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful PDF assistant, but currently have limited functionality."),
            ("user", "{input}"),
        ])
        return AgentExecutor(
            agent=create_openai_functions_agent(llm, [], fallback_prompt),
            tools=[],
            verbose=True
        )

agent_executor = None

def get_agent_executor():
    global agent_executor
    if agent_executor is None:
        agent_executor = create_agent()
    return agent_executor

async def fetch_prompt(prompt_name: str, args: Dict[str, Any]) -> str:
    """Fetch prompt result using FastMCP client"""
    try:
        async with MCPClient(MCP_URL) as client:
            result = await client.call_prompt(prompt_name, args)
            return result.data
    except Exception as e:
        logger.error(f"Error calling prompt: {str(e)}")
        return f"Error calling prompt: {str(e)}"

def decision_node(state: State) -> Dict:
    """Decides whether to use a tool or prompt based on the query."""
    query = state["query"]
    
    try:
        prompts_info = ""
        prompt_definitions = asyncio.run(async_get_prompts_info())
        
        for prompt in prompt_definitions:
            name = prompt.get("name", "unknown")
            description = prompt.get("description", "No description available")
            parameters = prompt.get("parameters", {})
            required_params = parameters.get("required", [])
            properties = parameters.get("properties", {})
            
            req_args = ", ".join(required_params)
            opt_args = ", ".join([p for p in properties.keys() if p not in required_params])
            
            prompt_desc = f"- {name}: {description}\n  Required args: {req_args}"
            if opt_args:
                prompt_desc += f"\n  Optional args: {opt_args}"
            prompts_info += prompt_desc + "\n"
    except Exception as e:
        logger.error(f"Error getting prompts info: {str(e)}")
        prompts_info = "Error fetching available prompts."
    
    system_message = f"""You are a PDF assistant that can either use tools or pre-built prompts.
Based on the user's query, decide which approach would be more effective.

AVAILABLE PROMPTS:
{prompts_info}

Prompts are ideal for standard operations like PDF summarization, key point extraction,
document structure analysis, or podcast script generation.

Tools are better for custom retrieval, list operations, database status checks, or
when you need more flexibility.

Respond with JSON: {{"branch": "tool"}} or {{"branch": "prompt", "prompt_name": "name", "prompt_args": {{"arg1": "value1", ...}}}}
"""
    
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    
    branch = "tool"  # Default to tool
    prompt_name = None
    prompt_args = {}
    
    try:
        json_match = re.search(r'\{.*?"branch".*?\}', response.content, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group(0))
            branch = decision.get("branch", "tool")
            prompt_name = decision.get("prompt_name")
            prompt_args = decision.get("prompt_args", {})
    except Exception as e:
        logger.error(f"Error parsing decision: {str(e)}")
    
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

async def async_get_prompts_info():
    async with MCPClient(MCP_URL) as client:
        return await client.list_prompts()

def tool_branch(state: State) -> Dict:
    """Uses tools to process the query through the agent."""
    messages = state["messages"]
    
    try:
        result = get_agent_executor().invoke({
            "input": state["query"], 
            "chat_history": messages
        })
    except Exception as e:
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
        result = asyncio.run(fetch_prompt(prompt_name, prompt_args))
        
        return {
            "query": state["query"],
            "messages": state["messages"] + [AIMessage(content=result)],
            "final_output": result,
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

def response_formatter(state: State) -> Dict:
    """Uses LLM to format the final output for presentation."""
    final_output = state["final_output"]
    query = state["query"]
    branch = state["branch"]
    prompt_name = state["prompt_name"]
    
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

def build_graph():
    """Builds and returns the compiled StateGraph."""
    builder = StateGraph(State)
    
    builder.add_node("decision", RunnableLambda(decision_node))
    builder.add_node("tool_branch", RunnableLambda(tool_branch))
    builder.add_node("prompt_branch", RunnableLambda(prompt_branch))
    builder.add_node("response_formatter", RunnableLambda(response_formatter))
    
    builder.add_edge(START, "decision")
    
    builder.add_conditional_edges(
        "decision",
        lambda state: "prompt_branch" if state["branch"] == "prompt" else "tool_branch"
    )
    
    builder.add_edge("tool_branch", "response_formatter")
    builder.add_edge("prompt_branch", "response_formatter")
    
    builder.add_edge("response_formatter", END)
    
    return builder.compile()