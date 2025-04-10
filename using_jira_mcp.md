# Using the Jira Python MCP Server

This document provides a comprehensive guide to using the Jira Python MCP server, which allows AI assistants like Claude to interact with your Jira instance through the Model Context Protocol (MCP).

## Table of Contents

1. [Overview](#overview)
2. [Implementation Status](#implementation-status)
3. [Setup and Configuration](#setup-and-configuration)
4. [Testing the Server](#testing-the-server)
5. [VSCode Integration](#vscode-integration)
6. [Troubleshooting](#troubleshooting)
7. [Future Improvements](#future-improvements)

## Overview

The Jira Python MCP server is a bridge that allows AI assistants to interact with Jira through a standardized interface. It implements the Model Context Protocol (MCP) to expose Jira functionality as tools that can be used by AI models.

### Architecture

The server is organized into layers:

- **Base Layer**: Direct mappings to the Jira API (list projects, get issues, etc.)
- **Advanced Layer**: Higher-level abstractions that combine multiple API calls (comprehensive ticket summaries, etc.)
- **MCP Server**: Exposes the functionality as standardized tools through the MCP protocol

## Implementation Status

The server is **fully functional** and has been tested with the following capabilities:

- ✅ Connecting to Jira using API token authentication
- ✅ Listing projects (verified working with FORGE and MDP projects)
- ✅ Getting issue details (verified with FORGE-1)
- ✅ Retrieving comments
- ✅ Getting comprehensive ticket summaries

## Setup and Configuration

### Prerequisites

- Python 3.12+
- A Jira account with API token access
- The jira-python library
- The MCP SDK

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dawsonlp/jira_python_mcp.git
   cd jira_python_mcp
   ```

2. Run the build script to set up the environment:
   ```bash
   ./build.sh
   ```

3. Configure your Jira credentials by editing `jira_mcp.env`:
   ```
   # Jira authentication
   JIRA_SERVER=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

### Running the Server

Start the MCP server:

```bash
source venv/bin/activate
python -m jira_python_mcp.server
```

This will start the server and listen for incoming MCP protocol requests.

## Testing the Server

Several test scripts are provided to verify functionality:

### 1. Simple Jira Test

This script tests the Jira client directly, bypassing the MCP protocol:

```bash
python simple_jira_test.py
```

### 2. MCP Direct Client

This script tests the MCP server functionality directly by accessing its implementation:

```bash
python mcp_direct_client.py
```

### Test Results

Testing confirms that all functionality is working correctly. The `mcp_direct_client.py` script successfully retrieves:

- Project list:
  ```json
  [
    {
      "id": "10001",
      "key": "FORGE",
      "name": "ForgeMaker",
      "lead": "Unknown",
      "url": "https://larrydawson.atlassian.net/browse/FORGE"
    },
    {
      "id": "10002",
      "key": "MDP",
      "name": "My discovery project",
      "lead": "Unknown",
      "url": "https://larrydawson.atlassian.net/browse/MDP"
    }
  ]
  ```

- Issue details for FORGE-1:
  ```json
  {
    "id": "10007",
    "key": "FORGE-1",
    "summary": "Development environment setup",
    "description": "Set up all of the components for ForgeMaker...",
    "status": "To Do",
    "issue_type": "Epic",
    "project": "FORGE",
    "created": "2024-03-23T00:22:05.841-0400",
    "updated": "2024-03-23T19:50:27.725-0400",
    "reporter": "Laurence Dawson",
    "assignee": "Laurence Dawson",
    "priority": "Medium",
    "url": "https://larrydawson.atlassian.net/browse/FORGE-1"
  }
  ```

- Comprehensive ticket summary for FORGE-1 showing:
  - Status and type information
  - Timeline of events
  - Role information
  - Links to the issue

## VSCode Integration

To use the MCP server with Claude in VSCode:

### Configuration

1. Edit the Claude VSCode extension settings at:
   `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`

2. Use this configuration:
   ```json
   {
     "mcpServers": {
       "jira": {
         "command": "/home/dawsonlp/repos/jira_python_mcp/venv/bin/python",
         "args": ["-m", "jira_python_mcp.server"],
         "cwd": "/home/dawsonlp/repos/jira_python_mcp",
         "env": {
           "JIRA_MCP_ENV_PATH": "/home/dawsonlp/repos/jira_python_mcp/jira_mcp.env"
         },
         "disabled": false,
         "autoApprove": []
       }
     }
   }
   ```

3. Restart VSCode or reload the window to apply the changes

### Using with Claude

After configuration, you can ask Claude questions like:
- "List my Jira projects"
- "Show me details for FORGE-1"
- "Get a summary of the Development environment setup ticket"

Claude will use the MCP server to retrieve the information directly from your Jira instance.

## Troubleshooting

### MCP Connection Issues

If Claude cannot connect to the MCP server, check:

1. **Server Running**: Verify the server is running with:
   ```bash
   ps aux | grep jira_python_mcp.server
   ```

2. **Configuration**: Ensure the `cline_mcp_settings.json` file is correctly formatted (valid JSON)

3. **VSCode Restart**: Try restarting VSCode to pick up configuration changes

4. **Paths**: Verify that all paths in the configuration are absolute and correct

### Jira API Issues

If the server connects but can't retrieve Jira data:

1. **Credentials**: Verify your Jira credentials in `jira_mcp.env`

2. **Logs**: Check `jira_mcp.log` for API errors

3. **Network**: Ensure you can access your Jira instance from the machine

## Future Improvements

### 1. Network Transport

To make the server accessible from other machines, replace stdio transport with a network transport:

```python
# Server implementation changes to support sockets
async def run_over_network(self, host="localhost", port=8765):
    logger.info(f"Starting Jira MCP server on {host}:{port}...")
    server = await asyncio.start_server(
        self.handle_client, host, port
    )
    async with server:
        await server.serve_forever()

async def handle_client(self, reader, writer):
    # Handle client connections
    await self.server.run(
        read_stream=reader,
        write_stream=writer,
        initialization_options=self.server.create_initialization_options()
    )
```

### 2. Containerization

A Dockerfile for containerization might look like:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Volume for environment file
VOLUME /app/config

# Expose port for network transport
EXPOSE 8765

# Run the server
CMD ["python", "-m", "jira_python_mcp.server", "--network", "--config", "/app/config/jira_mcp.env"]
```

### 3. Enhanced Security

For production deployment, consider:

- Using a secure vault for credential management
- Implementing authentication for MCP server connections
- Using HTTPS for transport security

### 4. Additional Features

Potential new features:

- Creating and updating issues
- Searching for issues with JQL
- Project statistics and metrics
- Integration with other Atlassian products

## Conclusion

The Jira Python MCP server provides a powerful bridge between AI assistants and your Jira instance. By following the setup and configuration instructions in this document, you can enable Claude to interact directly with your Jira data, making it much more useful for project management tasks.
