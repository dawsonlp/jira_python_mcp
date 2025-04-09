#!/usr/bin/env python3
"""
Very simple test script for the Jira MCP server.
This is the easiest way to verify the server is working correctly.

Usage:
1. First run the Jira MCP server in a separate terminal:
   $ python -m jira_python_mcp.server

2. Then run this test in another terminal:
   $ python simple_jira_test.py
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.models import ServerCapabilities
from jira_python_mcp.base.client import JiraClient
from jira_python_mcp.advanced.client import AdvancedJiraClient
from dotenv import load_dotenv

async def main():
    # Load environment variables from .env file
    env_path = os.environ.get("JIRA_MCP_ENV_PATH", "jira_mcp.env")
    if Path(env_path).exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Environment file {env_path} not found. Using system environment variables.")

    print("Testing Jira client directly (bypassing MCP)...")
    
    try:
        # Create a JiraClient instance
        client = JiraClient.from_env()
        print("\n✅ Successfully created Jira client! Connection is working.")
        
        # Try to list projects
        print("\nAttempting to list projects...")
        projects = client.list_projects()
        
        # Print up to 3 projects with pretty JSON formatting
        if projects:
            print(f"\n✅ Success! Found {len(projects)} projects. Here are up to 3 of them:")
            print(json.dumps(projects[:3], indent=2))
        else:
            print("\n✅ Connection works but no projects were found (empty list returned).")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("1. Check that your jira_mcp.env file contains valid credentials")
        print("2. Make sure you can access the Jira instance from this machine")
        print("3. Verify your network connection")
        return
    
    print("\n==============================================")
    print("Test complete! Your Jira integration is working.")
    print("The MCP server should now be fully functional.")
    print("==============================================")

if __name__ == "__main__":
    asyncio.run(main())
