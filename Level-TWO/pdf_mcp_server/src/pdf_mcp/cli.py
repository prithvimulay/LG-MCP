import asyncio
import sys
import logging
from pdf_mcp.langgraph.graph_builder import process_pdf_query_mcp, cleanup_pdf_orchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pdf_mcp_cli")

class MCPWorkflowCLI:
    """CLI implementing the complete MCP workflow"""
    
    def __init__(self):
        self.session_active = False
    
    def print_banner(self):
        """Print CLI banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                   PDF MCP CLI - LangGraph Workflow                   ║
╠══════════════════════════════════════════════════════════════════════╣
║  Commands: 'help' | 'quit'/'exit' | 'clear' | 'status'               ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
    
    def show_help(self):
        """Show help information"""
        help_text = """
PDF MCP CLI - Complete Workflow Help

The MCP Workflow:
  User Query → CLI → Load Tools from MCP Server → LangGraph Tool Selection → 
  Call MCP Tool → Obtain Result → Format via LLM → Display in CLI

Available Commands:
  • help, h, ?          - Show this help
  • quit, exit, q       - Exit the session  
  • clear, cls          - Clear screen
  • status              - Check MCP server status

Natural Language Queries:
  Document Management:
    • "List all PDFs"
    • "Show available documents" 
    • "What PDFs do you have?"

  Content Search:
    • "Search for attention mechanisms in attention.pdf"
    • "Find information about AI agents"
    • "What does the roleAI.pdf say about agents?"

  Content Generation:
    • "Generate a podcast about transformers from attention.pdf"
    • "Create content about AI from agenticAI.pdf"

  Database Operations:
    • "Show database status"
    • "How many documents are indexed?"

Example Session:
  You: list all pdfs
  AI: [MCP workflow executes: loads tools → selects list_pdfs_tool → calls MCP server → formats result]

Available Documents: agenticAI.pdf, attention.pdf, roleAI.pdf
"""
        print(help_text)
    
    async def run_interactive_session(self):
        """Run interactive MCP workflow session"""
        self.session_active = True
        self.print_banner()
        
        try:
            print("Initializing MCP workflow system...")
            print("   • Connecting to MCP server...")
            print("   • Loading tools via MCP client...")
            print("   • Setting up LangGraph orchestration...")
            print("MCP workflow ready!\n")
            
            while self.session_active:
                try:
                    # Get user input
                    user_input = input("You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Handle system commands
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("\nGoodbye! MCP workflow session ended.")
                        break
                    
                    elif user_input.lower() in ['help', 'h', '?']:
                        self.show_help()
                        continue
                    
                    elif user_input.lower() in ['clear', 'cls']:
                        import os
                        os.system('cls' if os.name == 'nt' else 'clear')
                        self.print_banner()
                        continue
                    
                    elif user_input.lower() == 'status':
                        await self._show_mcp_status()
                        continue
                    
                    # Process query through MCP workflow
                    print(f"\nProcessing via MCP workflow...")
                    print("   → Loading MCP tools...")
                    print("   → LangGraph selecting tool...")
                    print("   → Calling MCP server...")
                    print("   → Formatting response...\n")
                    
                    response = await process_pdf_query_mcp(user_input)
                    
                    # Display response
                    print("AI Assistant (via MCP Workflow):")
                    print("─" * 70)
                    print(response)
                    print("─" * 70 + "\n")
                    
                except KeyboardInterrupt:
                    print("\nUse 'quit' to exit properly...")
                    continue
                except Exception as e:
                    print(f"\nMCP workflow error: {e}")
                    print("Try 'help' for available commands\n")
        
        finally:
            await self._cleanup()
    
    async def run_single_command(self, query: str):
        """Run single command through MCP workflow"""
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                 PDF MCP CLI - Single Command Mode                    ║") 
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(f"Query: {query}")
        print("─" * 70)
        
        try:
            print("Executing MCP workflow...")
            print("   → Connecting to MCP server...")
            print("   → Loading tools via MCP client...")
            print("   → LangGraph processing...")
            
            if query.strip().lower() == "list all pdfs":
                print("   → Using list_pdfs_tool directly...")
            else:
                print("   → Selecting appropriate tool for query...")
                
            print("   → Awaiting response...")
            print()
            
            response = await process_pdf_query_mcp(query)
            
            print("Result via MCP Workflow:")
            print("═" * 70)
            print(response)
            print("═" * 70)
            
        except Exception as e:
            print("MCP Workflow Error:")
            print("═" * 70)
            print(f"Error: {e}")
            print("Ensure MCP server is running: python -m pdf_mcp.mcp.server")
            print("═" * 70)
        finally:
            await self._cleanup()
    
    async def _show_mcp_status(self):
        """Show MCP system status"""
        try:
            status_response = await process_pdf_query_mcp("Show me the current system and database status")
            print("\nMCP System Status:")
            print("─" * 50)
            print(status_response)
            print("─" * 50 + "\n")
        except Exception as e:
            print(f"Failed to get MCP status: {e}\n")
    
    async def _cleanup(self):
        """Cleanup MCP workflow resources"""
        try:
            print("Cleaning up MCP workflow...")
            await cleanup_pdf_orchestrator()
            print("Cleanup completed")
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")

async def main():
    """Main CLI entry point for MCP workflow"""
    cli = MCPWorkflowCLI()
    
    try:
        if len(sys.argv) < 2:
            await cli.run_interactive_session()
        else:
            query = " ".join(sys.argv[1:])
            await cli.run_single_command(query)
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"CLI error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
