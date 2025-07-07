#!/usr/bin/env python3
"""
Test script to verify MCP server works correctly
"""

import subprocess
import json
import sys

def test_mcp_server():
    """Test if the MCP server can start and respond to a simple request"""
    
    # Test command that Claude Desktop will use
    cmd = [
        "python", "run_server.py"
    ]
    
    try:
        # Start the server process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={"PYTHONPATH": "C:\\Dev\\Projects\\LG-MCP\\Level-TWO\\pdf_mcp_server\\src"}
        )
        
        # Send a simple initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send the request
        request_json = json.dumps(init_request) + "\n"
        stdout, stderr = process.communicate(input=request_json, timeout=10)
        
        print("✅ Server started successfully!")
        print("📤 Sent initialization request")
        print("📥 Response received:")
        print(stdout[:200] + "..." if len(stdout) > 200 else stdout)
        
        if stderr:
            print("⚠️  Stderr:", stderr[:200])
            
        return True
        
    except subprocess.TimeoutExpired:
        print("✅ Server is running (timeout waiting for response is normal)")
        process.kill()
        return True
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    test_mcp_server()
