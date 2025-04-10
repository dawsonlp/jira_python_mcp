#!/usr/bin/env python3
"""
Direct test for the Jira MCP server functionality.
This script tests the core functionality without using the MCP protocol.

Usage:
python test_jira_mcp.py
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Import the core functionality that the MCP server uses
from jira_python_mcp.base.client import JiraClient
from jira_python_mcp.advanced.client import AdvancedJiraClient

async def main():
    # Set up logging
    print("Testing Jira MCP functionality directly...\n")
    
    # Load environment variables from .env file
    env_path = os.environ.get("JIRA_MCP_ENV_PATH", "jira_mcp.env")
    if Path(env_path).exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        print(f"Environment file {env_path} not found. Using system environment variables.")
    
    try:
        # Create a JiraClient instance
        print("\nCreating Jira client...")
        jira_client = JiraClient.from_env()
        print("✅ Successfully created Jira client")
        
        # Create an AdvancedJiraClient instance
        print("\nCreating Advanced Jira client...")
        advanced_client = AdvancedJiraClient(jira_client)
        print("✅ Successfully created Advanced Jira client")
        
        # Test the list_projects functionality
        print("\n1. Testing list_projects...")
        projects = jira_client.list_projects()
        if projects:
            print(f"✅ Found {len(projects)} projects:")
            print(json.dumps(projects, indent=2))
        else:
            print("✅ No projects found or accessible")
        
        # Test other functionality if projects exist
        if projects:
            project_key = projects[0]["key"]
            
            # Try to get transitions for a dummy issue
            print(f"\n2. Testing get_transitions for a dummy issue ({project_key}-1)...")
            try:
                transitions = jira_client.get_transitions(f"{project_key}-1")
                print("✅ Got transitions:")
                print(json.dumps(transitions, indent=2))
            except Exception as e:
                print(f"❌ Could not get transitions: {e}")
        
        print("\n==============================================")
        print("Test complete! Your Jira client is working.")
        print("This confirms the core functionality used by the MCP server.")
        print("==============================================")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nPossible issues:")
        print("1. Check that your jira_mcp.env file contains valid credentials")
        print("2. Make sure you can access the Jira instance from this machine")
        print("3. Verify your network connection")

if __name__ == "__main__":
    asyncio.run(main())
