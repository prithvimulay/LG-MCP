#!/usr/bin/env python3
"""
Manual MCP client to test PDF server functionality
"""

import asyncio
import json
import subprocess
import sys
from typing import Optional

class MCPTestClient:
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.request_id = 1
    
    async def start_server(self):
        """Start the MCP server"""
        cmd = [
            "uv", "run", 
            "--directory", "C:\\Dev\\Projects\\LG-MCP\\Level-TWO\\pdf_mcp_server",
            "python", "-m", "src.pdf_mcp.server"
        ]
        
        print("🚀 Starting MCP server...")
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Initialize the server
        await self.send_request({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        })
        self.request_id += 1
        
        # Send initialized notification
        await self.send_notification({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        })
        
        print("✅ Server initialized!")
    
    async def send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request"""
        if not self.process:
            raise Exception("Server not started")
            
        request_json = json.dumps(request) + "\n"
        print(f"📤 Sending: {request['method']}")
        
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response (simplified)
        try:
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                print(f"📥 Response: {response}")
                return response
        except Exception as e:
            print(f"⚠️ Response error: {e}")
        
        return {}
    
    async def send_notification(self, notification: dict):
        """Send a JSON-RPC notification"""
        if not self.process:
            raise Exception("Server not started")
            
        notification_json = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_json)
        self.process.stdin.flush()
    
    async def list_tools(self):
        """List available tools"""
        return await self.send_request({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/list",
            "params": {}
        })
    
    async def call_tool(self, tool_name: str, arguments: dict = None):
        """Call a specific tool"""
        self.request_id += 1
        return await self.send_request({
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {}
            }
        })
    
    async def test_pdf_workflow(self):
        """Test the complete PDF workflow"""
        print("\n🧪 Testing PDF Workflow")
        print("=" * 50)
        
        # 1. List available tools
        print("\n1️⃣ Listing available tools...")
        await self.list_tools()
        
        # 2. Upload PDFs
        print("\n2️⃣ Uploading PDFs...")
        await self.call_tool("upload_pdfs")
        
        # 3. List PDFs
        print("\n3️⃣ Listing PDFs...")
        await self.call_tool("list_pdfs")
        
        # 4. Select PDF
        print("\n4️⃣ Selecting PDF...")
        await self.call_tool("select_pdfs", {"pdf_identifiers": "1"})
        
        # 5. Query PDF
        print("\n5️⃣ Querying PDF...")
        await self.call_tool("query_pdfs", {"question": "What are the basic rules?"})
        
        print("\n✅ Workflow test complete!")
    
    def cleanup(self):
        """Clean up the server process"""
        if self.process:
            self.process.terminate()
            self.process.wait()

async def main():
    client = MCPTestClient()
    
    try:
        await client.start_server()
        await client.test_pdf_workflow()
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
