#!/usr/bin/env python3
"""Jira MCP server for exposing Jira functionality through the Model Context Protocol."""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from modelcontextprotocol.server import McpServer, McpServerCapabilities, McpServerInfo
from modelcontextprotocol.server.transport import McpStdioTransport
from modelcontextprotocol.types import (
    CallToolRequestSchema,
    ErrorCode,
    ListToolsRequestSchema,
    McpError,
    ToolContentItem,
    ToolDescription,
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
        self.server = McpServer(
            info=McpServerInfo(
                name="jira-python-mcp",
                version="0.1.0",
            ),
            capabilities=McpServerCapabilities(
                tools=True,
                resources=False,  # Not implementing resources for now
            ),
        )

        # Load clients on demand
        self._base_client = None
        self._advanced_client = None

        # Register handlers
        self.server.set_request_handler(ListToolsRequestSchema, self._handle_list_tools)
        self.server.set_request_handler(CallToolRequestSchema, self._handle_call_tool)

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
                raise McpError(
                    ErrorCode.InternalError, f"Failed to create base Jira client: {e}"
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
                raise McpError(
                    ErrorCode.InternalError, f"Failed to create advanced Jira client: {e}"
                )
        return self._advanced_client

    def _handle_error(self, error: Exception) -> None:
        """Handle errors in the MCP server.

        Args:
            error: The error that occurred.
        """
        logger.error(f"MCP Error: {error}")

    async def _handle_list_tools(self, _: Dict[str, Any]) -> Dict[str, List[ToolDescription]]:
        """Handle the list_tools request.

        Args:
            _: The request parameters (unused).

        Returns:
            Dict[str, List[ToolDescription]]: The list of tools provided by this server.
        """
        logger.info("Handling list_tools request")
        return {
            "tools": [
                # Basic tools
                ToolDescription(
                    name="list_projects",
                    description="List all projects in Jira",
                    input_schema={
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                ),
                ToolDescription(
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
                ToolDescription(
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
                ToolDescription(
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
        }

    async def _handle_call_tool(
        self, params: Dict[str, Any]
    ) -> Dict[str, List[ToolContentItem]]:
        """Handle the call_tool request.

        Args:
            params: The request parameters.

        Returns:
            Dict[str, List[ToolContentItem]]: The result of the tool call.

        Raises:
            McpError: If the tool is not found or an error occurs.
        """
        tool_name = params.get("name")
        logger.info(f"Handling call_tool request for tool: {tool_name}")

        # Basic tools
        if tool_name == "list_projects":
            return await self._list_projects()
        elif tool_name == "get_issue":
            return await self._get_issue(params)
        elif tool_name == "get_comments":
            return await self._get_comments(params)
        
        # Advanced tools
        elif tool_name == "get_ticket_summary":
            return await self._get_ticket_summary(params)
        
        raise McpError(ErrorCode.MethodNotFound, f"Unknown tool: {tool_name}")

    # Basic tool implementations
    
    async def _list_projects(self) -> Dict[str, List[ToolContentItem]]:
        """List all projects in Jira.

        Returns:
            Dict[str, List[ToolContentItem]]: The list of projects.
        """
        try:
            projects = self.base_client.list_projects()
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=json.dumps(projects, indent=2),
                    )
                ]
            }
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=f"Error listing projects: {e}",
                    )
                ],
                "is_error": True,
            }
    
    async def _get_issue(self, params: Dict[str, Any]) -> Dict[str, List[ToolContentItem]]:
        """Get information about a Jira issue.

        Args:
            params: The request parameters.

        Returns:
            Dict[str, List[ToolContentItem]]: The issue information.
        """
        try:
            issue_key = params.get("arguments", {}).get("issue_key")
            if not issue_key:
                raise McpError(ErrorCode.InvalidParams, "Missing issue_key parameter")
            
            issue = self.base_client.get_issue(issue_key)
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=json.dumps(issue, indent=2),
                    )
                ]
            }
        except Exception as e:
            logger.error(f"Error getting issue: {e}")
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=f"Error getting issue: {e}",
                    )
                ],
                "is_error": True,
            }
    
    async def _get_comments(self, params: Dict[str, Any]) -> Dict[str, List[ToolContentItem]]:
        """Get comments for a Jira issue.

        Args:
            params: The request parameters.

        Returns:
            Dict[str, List[ToolContentItem]]: The issue comments.
        """
        try:
            issue_key = params.get("arguments", {}).get("issue_key")
            if not issue_key:
                raise McpError(ErrorCode.InvalidParams, "Missing issue_key parameter")
            
            comments = self.base_client.get_comments(issue_key)
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=json.dumps(comments, indent=2),
                    )
                ]
            }
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=f"Error getting comments: {e}",
                    )
                ],
                "is_error": True,
            }
    
    # Advanced tool implementations
    
    async def _get_ticket_summary(self, params: Dict[str, Any]) -> Dict[str, List[ToolContentItem]]:
        """Get comprehensive ticket summary.

        Args:
            params: The request parameters.

        Returns:
            Dict[str, List[ToolContentItem]]: The ticket summary.
        """
        try:
            issue_key = params.get("arguments", {}).get("issue_key")
            if not issue_key:
                raise McpError(ErrorCode.InvalidParams, "Missing issue_key parameter")
            
            summary = self.advanced_client.get_ticket_summary(issue_key)
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=json.dumps(summary, indent=2),
                    )
                ]
            }
        except Exception as e:
            logger.error(f"Error getting ticket summary: {e}")
            return {
                "content": [
                    ToolContentItem(
                        type="text",
                        text=f"Error getting ticket summary: {e}",
                    )
                ],
                "is_error": True,
            }

    async def run(self) -> None:
        """Run the Jira MCP server."""
        transport = McpStdioTransport()
        await self.server.connect(transport)
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
