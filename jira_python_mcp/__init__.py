"""Jira MCP server for exposing Jira functionality through the Model Context Protocol."""

__version__ = "0.1.0"

# Re-export important classes
from jira_python_mcp.base.client import JiraClient, JiraConfig
from jira_python_mcp.advanced.client import AdvancedJiraClient
