#!/usr/bin/env python3
"""Jira MCP server for exposing Jira functionality through the Model Context Protocol."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    JSONRPCError,
    TextContent,
    Tool,
)

from jira_python_mcp.base.client import JiraClient
from jira_python_mcp.advanced.client import AdvancedJiraClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("jira_mcp.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("jira_mcp")


class JiraMcpServer:
    """Jira MCP server for exposing Jira functionality through the Model Context Protocol."""

    def __init__(self):
        """Initialize the Jira MCP server."""
        # Load environment variables from .env file
        env_path = os.environ.get("JIRA_MCP_ENV_PATH", "jira_mcp.env")
        if Path(env_path).exists():
            load_dotenv(env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        else:
            logger.warning(
                f"Environment file {env_path} not found. Using system environment variables."
            )

        # Set up the MCP server
        self.server = Server(
            name="jira-python-mcp",
            version="0.1.0",
        )

        # Load clients on demand
        self._base_client = None
        self._advanced_client = None

        # Register handlers using decorators
        @self.server.list_tools()
        async def list_tools():
            logger.info("Handling list_tools request")
            return [
                # Basic tools
                Tool(
                    name="list_projects",
                    description="List all projects in Jira",
                    input_schema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_issue",
                    description="Get basic information about a Jira issue",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., PROJ-123)",
                            }
                        },
                        "required": ["issue_key"],
                        "additionalProperties": False,
                    },
                ),
                Tool(
                    name="get_comments",
                    description="Get comments for a Jira issue",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., PROJ-123)",
                            }
                        },
                        "required": ["issue_key"],
                        "additionalProperties": False,
                    },
                ),
                # Advanced tools
                Tool(
                    name="get_ticket_summary",
                    description="Get comprehensive ticket summary including description, comments, timeline, roles, and status",
                    input_schema={
                        "type": "object",
                        "properties": {
                            "issue_key": {
                                "type": "string",
                                "description": "The issue key (e.g., PROJ-123)",
                            }
                        },
                        "required": ["issue_key"],
                        "additionalProperties": False,
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]):
            logger.info(f"Handling call_tool request for tool: {name}")

            try:
                # Basic tools
                if name == "list_projects":
                    return await self._list_projects()
                elif name == "get_issue":
                    return await self._get_issue(arguments)
                elif name == "get_comments":
                    return await self._get_comments(arguments)
                # Advanced tools
                elif name == "get_ticket_summary":
                    return await self._get_ticket_summary(arguments)
                
                raise JSONRPCError(
                    code=-32601,  # Method not found
                    message=f"Unknown tool: {name}",
                )
            except JSONRPCError:
                # Re-raise JSONRPCError
                raise
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                raise JSONRPCError(
                    code=-32603,  # Internal error
                    message=f"Error executing tool {name}: {e}",
                )

        # Set up error handler
        self.server.onerror = self._handle_error

    @property
    def base_client(self) -> JiraClient:
        """Get the base Jira client, creating it if necessary.

        Returns:
            JiraClient: A client for interacting with Jira.
        """
        if self._base_client is None:
            try:
                self._base_client = JiraClient.from_env()
            except Exception as e:
                logger.error(f"Failed to create base Jira client: {e}")
                raise JSONRPCError(
                    code=-32603,  # Internal error
                    message=f"Failed to create base Jira client: {e}",
                )
        return self._base_client
    
    @property
    def advanced_client(self) -> AdvancedJiraClient:
        """Get the advanced Jira client, creating it if necessary.

        Returns:
            AdvancedJiraClient: An advanced client for interacting with Jira.
        """
        if self._advanced_client is None:
            try:
                self._advanced_client = AdvancedJiraClient(self.base_client)
            except Exception as e:
                logger.error(f"Failed to create advanced Jira client: {e}")
                raise JSONRPCError(
                    code=-32603,  # Internal error
                    message=f"Failed to create advanced Jira client: {e}",
                )
        return self._advanced_client

    def _handle_error(self, error: Exception) -> None:
        """Handle errors in the MCP server.

        Args:
            error: The error that occurred.
        """
        logger.error(f"MCP Error: {error}")

    # Basic tool implementations
    
    async def _list_projects(self) -> List[TextContent]:
        """List all projects in Jira.

        Returns:
            List[TextContent]: The list of projects.
        """
        try:
            projects = self.base_client.list_projects()
            return [
                TextContent(
                    text=json.dumps(projects, indent=2),
                )
            ]
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return [
                TextContent(
                    text=f"Error listing projects: {e}",
                )
            ]
    
    async def _get_issue(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get information about a Jira issue.

        Args:
            arguments: The tool arguments.

        Returns:
            List[TextContent]: The issue information.
        """
        try:
            issue_key = arguments.get("issue_key")
            if not issue_key:
                raise JSONRPCError(
                    code=-32602,  # Invalid params
                    message="Missing issue_key parameter",
                )
            
            issue = self.base_client.get_issue(issue_key)
            return [
                TextContent(
                    text=json.dumps(issue, indent=2),
                )
            ]
        except JSONRPCError:
            # Re-raise JSONRPCError
            raise
        except Exception as e:
            logger.error(f"Error getting issue: {e}")
            return [
                TextContent(
                    text=f"Error getting issue: {e}",
                )
            ]
    
    async def _get_comments(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get comments for a Jira issue.

        Args:
            arguments: The tool arguments.

        Returns:
            List[TextContent]: The issue comments.
        """
        try:
            issue_key = arguments.get("issue_key")
            if not issue_key:
                raise JSONRPCError(
                    code=-32602,  # Invalid params
                    message="Missing issue_key parameter",
                )
            
            comments = self.base_client.get_comments(issue_key)
            return [
                TextContent(
                    text=json.dumps(comments, indent=2),
                )
            ]
        except JSONRPCError:
            # Re-raise JSONRPCError
            raise
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            return [
                TextContent(
                    text=f"Error getting comments: {e}",
                )
            ]
    
    # Advanced tool implementations
    
    async def _get_ticket_summary(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Get comprehensive ticket summary.

        Args:
            arguments: The tool arguments.

        Returns:
            List[TextContent]: The ticket summary.
        """
        try:
            issue_key = arguments.get("issue_key")
            if not issue_key:
                raise JSONRPCError(
                    code=-32602,  # Invalid params
                    message="Missing issue_key parameter",
                )
            
            summary = self.advanced_client.get_ticket_summary(issue_key)
            return [
                TextContent(
                    text=json.dumps(summary, indent=2),
                )
            ]
        except JSONRPCError:
            # Re-raise JSONRPCError
            raise
        except Exception as e:
            logger.error(f"Error getting ticket summary: {e}")
            return [
                TextContent(
                    text=f"Error getting ticket summary: {e}",
                )
            ]

    async def run(self) -> None:
        """Run the Jira MCP server."""
        logger.info("Starting Jira MCP server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream=read_stream,
                write_stream=write_stream,
                initialization_options=self.server.create_initialization_options()
            )
            logger.info("Jira MCP server started")


def main() -> None:
    """Run the Jira MCP server."""
    # Set log level from environment
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logger.setLevel(logging.getLevelName(log_level))
    
    server = JiraMcpServer()
    try:
        import asyncio
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Jira MCP server stopped")
    except Exception as e:
        logger.error(f"Error running Jira MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
