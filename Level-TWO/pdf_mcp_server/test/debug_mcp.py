#!/usr/bin/env python3
"""
Debug script to test MCP server with Claude Desktop protocol
"""

import subprocess
import json
import sys
import time

def test_mcp_initialization():
    """Test MCP server initialization like Claude Desktop would"""
    
    cmd = [
        "uv", "run", 
        "--directory", "C:\\Dev\\Projects\\LG-MCP\\Level-TWO\\pdf_mcp_server",
        "python", "-m", "src.pdf_mcp.server"
    ]
    
    print("🚀 Starting MCP server...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "claude-desktop",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 Sending initialization request...")
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Wait for response
        print("⏱️ Waiting for response...")
        try:
            stdout, stderr = process.communicate(timeout=5)
            print("📥 Response received!")
            print("STDOUT:", stdout[:500])
            if stderr:
                print("STDERR:", stderr[:500])
                
        except subprocess.TimeoutExpired:
            print("⏰ Timeout - server is running but waiting for more input")
            process.kill()
            print("✅ This is normal behavior for MCP servers!")
            
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_claude_config():
    """Check Claude Desktop configuration"""
    import os
    config_path = os.path.join(os.environ['APPDATA'], 'Claude', 'claude_desktop_config.json')
    
    print(f"📁 Config path: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            print("✅ Config file exists and is valid JSON")
            print("📋 Config contents:")
            print(json.dumps(config, indent=2))
            return True
    except FileNotFoundError:
        print("❌ Config file not found!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config: {e}")
        return False

if __name__ == "__main__":
    print("🔍 MCP Server Debug Tool")
    print("=" * 50)
    
    print("\n1️⃣ Checking Claude Desktop configuration...")
    check_claude_config()
    
    print("\n2️⃣ Testing MCP server initialization...")
    test_mcp_initialization()
    
    print("\n3️⃣ Next steps:")
    print("- Restart Claude Desktop completely")
    print("- Look for MCP servers in Claude Desktop settings")
    print("- Try asking Claude: 'What tools do you have available?'")
    print("- Or directly call: upload_pdfs()")
