# Jira MCP Server Fix Documentation

## Issue
The Jira MCP server was not functioning correctly when integrated with VS Code. When attempting to use MCP tools like `list_projects`, the server would return errors related to exception handling:

```
Error: catching classes that do not inherit from BaseException is not allowed
```

## Root Cause
The main issue was in the MCP configuration file (`cline_mcp_settings.json`). The server was being configured to run as a Python module rather than using the installed executable script.

### Original Configuration
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

## Solution
The fix involved updating the MCP configuration to use the installed `jira-mcp-server` executable directly instead of running the Python module.

### Fixed Configuration
```json
{
  "mcpServers": {
    "jira": {
      "command": "/home/dawsonlp/repos/jira_python_mcp/venv/bin/jira-mcp-server",
      "args": [],
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

## Additional Notes
- The error about catching classes that don't inherit from BaseException could be related to Python 3.12 compatibility. The server code was using custom exception handling that might not be compatible with newer Python versions.
- The Jira environment file (`jira_mcp.env`) was correctly set up with the server URL, email, and API token.
- After fixing the configuration, all server tools (`list_projects`, `get_issue`, `get_comments`, `get_ticket_summary`) became accessible and functional.

## Verification
After implementing the fix, we successfully tested the MCP server by:
1. Listing all available projects using the `list_projects` tool
2. Retrieving detailed information for ticket FORGE-3 using the `get_ticket_summary` tool

The MCP server is now correctly integrated with VS Code and can be used to interact with Jira without issues.
