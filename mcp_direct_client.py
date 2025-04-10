#!/usr/bin/env python3
"""
Direct MCP client that uses the MCP server implementation directly.
This approach bypasses the transport layer issues by directly accessing 
the server implementation methods.

Usage:
python mcp_direct_client.py
"""

import asyncio
import json
import sys
from mcp.types import Tool, TextContent

# Import the server implementation directly
from jira_python_mcp.server import JiraMcpServer

async def main():
    print("Testing Jira MCP functionality by directly calling server methods...")
    
    # Create our server instance (but don't run it)
    jira_server = JiraMcpServer()
    
    # List available tools
    print("\nAvailable tools in the Jira MCP server:")
    # Access the server's list_tools decorator
    for handler_name, handler in jira_server.server.request_handlers.items():
        if "list_tools" in str(handler_name):
            print(f"Found list_tools handler: {handler_name}")
    
    # Manually define the tools we know are available
    tools = [
        {"name": "list_projects", "description": "List all projects in Jira"},
        {"name": "get_issue", "description": "Get basic information about a Jira issue"},
        {"name": "get_comments", "description": "Get comments for a Jira issue"},
        {"name": "get_ticket_summary", "description": "Get comprehensive ticket summary"}
    ]
    
    # Print tools
    for tool in tools:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Call the list_projects tool directly by accessing the Jira client
    print("\nCalling list_projects directly via the Jira client...")
    
    try:
        # Use the base client directly instead of going through the server
        projects = jira_server.base_client.list_projects()
        
        print("\nSuccess! Projects found:")
        print(json.dumps(projects, indent=2))
    
    except Exception as e:
        print(f"Error getting projects: {e}")
    
    # Try getting a specific issue
    if projects:
        # Get the first project key
        project_key = projects[0]["key"]
        issue_key = f"{project_key}-1"  # Attempt to get the first issue
        
        print(f"\nGetting issue details for {issue_key} via the Jira client...")
        try:
            issue = jira_server.base_client.get_issue(issue_key)
            
            print("\nSuccess! Issue details:")
            print(json.dumps(issue, indent=2))
        except Exception as e:
            print(f"Error getting issue: {e}")

        # Try getting comments as well
        print(f"\nGetting comments for {issue_key} via the Jira client...")
        try:
            comments = jira_server.base_client.get_comments(issue_key)
            
            print("\nSuccess! Comments:")
            print(json.dumps(comments, indent=2))
        except Exception as e:
            print(f"Error getting comments: {e}")
            
        # Try advanced client functionality
        print(f"\nGetting ticket summary for {issue_key} via the Advanced Jira client...")
        try:
            summary = jira_server.advanced_client.get_ticket_summary(issue_key)
            
            print("\nSuccess! Ticket summary:")
            print(json.dumps(summary, indent=2))
        except Exception as e:
            print(f"Error getting ticket summary: {e}")

    print("\nTest complete.")

if __name__ == "__main__":
    asyncio.run(main())
