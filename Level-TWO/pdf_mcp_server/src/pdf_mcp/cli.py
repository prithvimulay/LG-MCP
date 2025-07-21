import asyncio
import sys
import logging
from pdf_mcp.langgraph.graph_builder import build_graph
from pdf_mcp.mcp.mcp_client import get_mcp_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf_mcp_cli")

class PDFAssistantCLI:
    def __init__(self):
        self.graph = None
        self.mcp_client = None

    async def initialize(self) -> bool:
        """Initialize CLI components"""
        try:
            # Initialize MCP client
            self.mcp_client = await get_mcp_client()
            health = await self.mcp_client.health_check()
            
            if not health:
                logger.error("MCP server health check failed")
                return False
            
            logger.info("MCP client connected")
            
            # Build graph
            self.graph = build_graph()
            logger.info("LangGraph initialized")
            
            return True

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            return False

    async def process_query(self, query: str) -> str:
        """Process query through LangGraph"""
        if not self.graph:
            if not await self.initialize():
                return " System initialization failed"

        try:
            initial_state = {
                "query": query,
                "messages": [],
                "final_output": None,
                "branch": "",
                "tool_name": None,
                "tool_args": None
            }

            result = await self.graph.ainvoke(initial_state)
            return result.get("final_output", "No response generated")

        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def run_interactive(self):
        """Run interactive mode"""
        print("🚀 PDF Assistant CLI (MCP + LangGraph)")
        
        if not await self.initialize():
            print("❌ Failed to initialize system")
            return

        print("Type your queries or 'quit' to exit\n")

        while True:
            try:
                query = input(">>> ").strip()
                
                if not query:
                    continue
                    
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break

                print("🔄 Processing...")
                result = await self.process_query(query)
                print(f"\n📝 Response:\n{result}\n")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}\n")

    async def run_single_query(self, query: str) -> str:
        """Run single query"""
        if not await self.initialize():
            return "❌ System initialization failed"
        return await self.process_query(query)

    async def cleanup(self):
        """Clean up resources"""
        if self.mcp_client:
            await self.mcp_client.close()

async def main():
    """Main entry point"""
    cli = PDFAssistantCLI()
    
    try:
        if len(sys.argv) > 1:
            # Single query mode
            query = " ".join(sys.argv[1:])
            result = await cli.run_single_query(query)
            print(result)
        else:
            # Interactive mode
            await cli.run_interactive()
    finally:
        await cli.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
