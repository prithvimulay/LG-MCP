from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from pdf_mcp.config.settings import settings
from pdf_mcp.mcp.mcp_client import get_mcp_client
import logging
import asyncio

logger = logging.getLogger(__name__)

class LangGraphPDFOrchestrator:
    """LangGraph orchestrator with robust MCP tool integration and strict tool usage."""

    def __init__(self):
        self.graph = None
        self.mcp_client = None
        self.tools_map = {}   
        self.tools_list = []  
        self.llm = None
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        try:
            logger.info("Initializing LangGraph PDF Orchestrator...")
            self.mcp_client = await get_mcp_client()
            raw_tools = await self.mcp_client.get_tools()
            if isinstance(raw_tools, dict):
                self.tools_map = raw_tools
                self.tools_list = list(raw_tools.values())
            elif isinstance(raw_tools, list):
                self.tools_map = {t.name: t for t in raw_tools}
                self.tools_list = raw_tools
            else:
                raise ValueError(f"Unexpected tools type: {type(raw_tools)}")
            logger.info(f"Loaded {len(self.tools_list)} MCP tools: {list(self.tools_map.keys())}")
            self.llm = ChatGroq(
                model=settings.llm_model,
                temperature=0.0,
                max_tokens=1000,
                groq_api_key=settings.groq_api_key
            )
            self.graph = self._build_langgraph()
            self._initialized = True
            logger.info("LangGraph PDF Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"LangGraph orchestrator initialization failed: {e}")
            raise

    def _build_langgraph(self):
        llm_with_tools = self.llm.bind_tools(self.tools_list)

        async def agent_node(state: MessagesState):
            messages = state["messages"]
            system_msg = SystemMessage(content=(
                "You are a PDF processing assistant that helps users interact with PDF documents. \n\n"
                "IMPORTANT INSTRUCTIONS:\n"
                "1. For a query like 'List all PDFs', use ONLY list_pdfs_tool\n"
                "2. For database or indexing status, use ONLY db_status_tool\n"
                "3. For content search in a specific PDF, use ONLY retrieve_from_pdf_tool\n"
                "4. For podcast generation, use ONLY generate_podcast_tool\n"
                "5. For finding a relevant PDF by topic, use ONLY select_relevant_pdf_tool\n\n"
                "For each user query, select EXACTLY ONE tool that best fits their request.\n"
                "DO NOT call multiple tools or attempt to chain them together.\n"
                "If a query like 'List all PDFs' comes in, just call list_pdfs_tool with no arguments.\n"
            ))
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [system_msg] + messages
            response = await llm_with_tools.ainvoke(messages)
            logger.info(
                f"Agent response has {len(response.tool_calls) if hasattr(response, 'tool_calls') and response.tool_calls else 0} tool calls"
            )
            return {"messages": [response]}

        async def mcp_tool_node(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]
            logger.info("MCP tool node activated")
            if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
                logger.info("No tool calls found")
                return {"messages": []}
            tool_messages = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args") or {}
                logger.info(f"Executing MCP tool: {tool_name} with args: {tool_args}")
                try:
                    proxy = self.tools_map.get(tool_name)
                    if not proxy:
                        available_tools = list(self.tools_map.keys())
                        result = f"Tool '{tool_name}' not found. Available: {available_tools}"
                        logger.error(result)
                    else:
                        raw_result = await asyncio.wait_for(
                            proxy.ainvoke(tool_args), timeout=120.0
                        )
                        if isinstance(raw_result, dict) and "result" in raw_result:
                            result = raw_result["result"]
                        else:
                            result = str(raw_result)
                        logger.info(f"Tool '{tool_name}' succeeded, result preview: {result[:100]}...")
                    tool_messages.append(
                        ToolMessage(content=result, tool_call_id=tool_call["id"])
                    )
                except asyncio.TimeoutError:
                    error_msg = f"Tool {tool_name} timed out after 120 seconds"
                    logger.error(error_msg)
                    tool_messages.append(
                        ToolMessage(content=error_msg, tool_call_id=tool_call["id"])
                    )
                except Exception as e:
                    error_msg = f"Tool {tool_name} execution failed: {e}"
                    logger.error(error_msg)
                    tool_messages.append(
                        ToolMessage(content=error_msg, tool_call_id=tool_call["id"])
                    )
            logger.info(f"MCP tool node completed with {len(tool_messages)} tool messages")
            return {"messages": tool_messages}

        def strict_routing(state: MessagesState):
            messages = state["messages"]
            last_message = messages[-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                logger.info("Routing to MCP tools")
                return "tools"
            logger.info("No tool calls found - workflow complete")
            return END

        builder = StateGraph(MessagesState)
        builder.add_node("agent", agent_node)
        builder.add_node("tools", mcp_tool_node)
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", strict_routing)
        builder.add_edge("tools", "agent")
        return builder.compile()

    async def process_query(self, query: str) -> str:
        try:
            if not self._initialized:
                await self.initialize()
            logger.info(f"Processing query with fixed MCP integration: {query[:100]}...")
            initial_state = {"messages": [HumanMessage(content=query)]}
            result = await asyncio.wait_for(
                self.graph.ainvoke(initial_state), timeout=240.0  
            )
            final_message = result["messages"][-1]
            logger.info("MCP workflow completed successfully")
            return final_message.content
        except asyncio.TimeoutError:
            return "Workflow timed out. This may indicate a tool execution issue."
        except Exception as e:
            logger.error(f"MCP workflow error: {e}")
            return f"Workflow failed: {str(e)}"

    async def cleanup(self):
        try:
            if self.mcp_client:
                await self.mcp_client.cleanup()
            self._initialized = False
            logger.info("LangGraph orchestrator cleaned up")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

_pdf_orchestrator = LangGraphPDFOrchestrator()

async def process_pdf_query_mcp(query: str) -> str:
    return await _pdf_orchestrator.process_query(query)

async def cleanup_pdf_orchestrator():
    await _pdf_orchestrator.cleanup()
