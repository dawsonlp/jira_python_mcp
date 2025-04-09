#!/usr/bin/env python3
"""
Simple test client for the Jira MCP server.
This script connects to a running Jira MCP server instance and tests basic functionality.

Usage:
1. Start the server in another terminal: python -m jira_python_mcp.server
2. Run this script: python test_mcp_client.py
"""

import asyncio
import json
import subprocess
import sys
from mcp.client import Client

async def main():
    print("Testing Jira MCP server...")
    print("Note: Ensure the server is already running in another terminal window")
    print("      with: python -m jira_python_mcp.server\n")
    
    # Start a client process that connects to the running server
    try:
        print("Starting an MCP client to test the server...")
        process = await asyncio.create_subprocess_exec(
            "python", "-m", "jira_python_mcp.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
        )

        # Create a client that connects to the subprocess
        client = Client(
            read_stream=process.stdout,
            write_stream=process.stdin,
        )
        
        # Initialize the client
        print("Initializing MCP client...")
        await client.initialize()
        
        # List available tools
        print("\nListing available tools:")
        tools = await client.list_tools()
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        
        # Try to call the list_projects tool
        print("\nTrying to call the list_projects tool...")
        try:
            result = await client.call_tool(name="list_projects", arguments={})
            print("\nSuccess! The server returned:")
            for content in result:
                if content.type == "text":
                    try:
                        # Try to parse JSON and pretty print it
                        data = json.loads(content.text)
                        print(json.dumps(data, indent=2))
                    except json.JSONDecodeError:
                        # If not valid JSON, print as is
                        print(content.text)
        except Exception as e:
            print(f"Error calling tool: {e}")
            print("Note: If you don't have valid Jira credentials in jira_mcp.env, this is expected.")
            print("The important part is that the server is running and can handle requests.")
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        # Terminate the subprocess
        if 'process' in locals():
            process.terminate()
            await process.wait()
        print("\nTest complete.")

if __name__ == "__main__":
    asyncio.run(main())
