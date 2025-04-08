# Using the Jira Python MCP in a New Project

This guide explains how to integrate the Jira Python MCP server into a completely separate project, allowing you to interact with Jira through the Model Context Protocol.

## Table of Contents

- [Requirements](#requirements)
- [Installation Options](#installation-options)
- [MCP Integration](#mcp-integration)
- [Sample Usage](#sample-usage)
- [AI Assistant Integration](#ai-assistant-integration) 
- [LLM Prompt for Project Setup](#llm-prompt-for-project-setup)

## Requirements

Before integrating the Jira MCP server into your project, ensure you have:

- Python 3.12 or higher
- A Jira account with API token access
- Jira Cloud or Server instance URL

## Installation Options

There are several ways to integrate the Jira Python MCP server into your project:

### Option 1: Install from GitHub

1. Install the package directly from GitHub:
   ```bash
   pip install git+https://github.com/yourusername/jira_python_mcp.git
   ```

2. Create a `jira_mcp.env` file in your project directory with your Jira credentials:
   ```
   JIRA_SERVER=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

### Option 2: Clone and Install Locally

1. Clone the repository to a location of your choice:
   ```bash
   git clone https://github.com/yourusername/jira_python_mcp.git /path/to/jira_python_mcp
   cd /path/to/jira_python_mcp
   ```

2. Install it in development mode:
   ```bash
   pip install -e .
   ```

3. Configure your environment file as described in Option 1.

### Option 3: Using as a Submodule (for Git-based projects)

1. Add the repository as a Git submodule:
   ```bash
   git submodule add https://github.com/yourusername/jira_python_mcp.git external/jira_python_mcp
   ```

2. Install it in development mode:
   ```bash
   pip install -e external/jira_python_mcp
   ```

3. Configure your environment file as described in Option 1.

## MCP Integration

### Running the MCP Server

Once installed, you can run the MCP server in your project using:

```bash
# Set the path to your environment file (optional)
export JIRA_MCP_ENV_PATH=/path/to/your/jira_mcp.env

# Start the server
jira-mcp-server
```

### Background Execution (for Production)

For long-running applications, you may want to run the MCP server in the background:

```bash
# Using nohup
nohup jira-mcp-server > jira_mcp.log 2>&1 &

# Or using supervisor, systemd, etc. for production setups
```

## Sample Usage

### Using with an AI Assistant

The primary use case for the MCP server is to provide Jira functionality to AI assistants. After installing and running the server as described above, configure your AI assistant to connect to the MCP server (see the main README for instructions).

### Programmatic Usage

You can also use the underlying Jira clients directly in your Python code:

```python
from jira_python_mcp import JiraClient, AdvancedJiraClient

# Using the basic client
basic_client = JiraClient.from_env()
projects = basic_client.list_projects()
print(f"Found {len(projects)} projects")

# Using the advanced client
advanced_client = AdvancedJiraClient.from_env()
ticket_summary = advanced_client.get_ticket_summary("PROJECT-123")
print(f"Ticket: {ticket_summary['summary']}")
print(f"Status: {ticket_summary['current_status']['name']}")
print(f"Roles: {ticket_summary['roles']}")
```

## AI Assistant Integration

### Setting Up Claude Desktop

1. Edit the Claude Desktop configuration file:
   ```json
   "jira": {
     "command": "jira-mcp-server",
     "args": [],
     "env": {
       "JIRA_MCP_ENV_PATH": "/absolute/path/to/your/project/jira_mcp.env"
     },
     "disabled": false,
     "autoApprove": []
   }
   ```

2. Restart Claude Desktop

### Setting Up Claude VSCode Extension

1. Edit the Claude VSCode extension settings:
   ```json
   "jira": {
     "command": "jira-mcp-server",
     "args": [],
     "env": {
       "JIRA_MCP_ENV_PATH": "/absolute/path/to/your/project/jira_mcp.env"
     },
     "disabled": false,
     "autoApprove": []
   }
   ```

2. Restart VSCode or reload the Claude extension

## LLM Prompt for Project Setup

Below is a prompt you can use with an LLM (like Claude) to set up a best-practices Python project that uses the Jira Python MCP server to manage its own Jira tickets:

```
Please create a best-practices Python project that uses the Jira Python MCP server to manage its own Jira tickets. The project should:

1. Have a well-structured layout following modern Python best practices.
2. Include virtual environment setup and dependency management.
3. Provide a CLI interface for interacting with Jira tickets for this project.
4. Implement the following features:
   - List all tickets for the project
   - Show detailed information about a specific ticket
   - Create a new ticket for issues, feature requests, or bugs
   - Update ticket status
   - Add comments to tickets
5. Include proper error handling and logging.
6. Have a separate configuration file for project-specific settings.
7. Include unit tests and documentation.
8. Use the Jira Python MCP server as a dependency, configuring it to connect to a Jira instance.
9. Provide a sample workflow for using the tool to manage the project's own ticket lifecycle.

The Jira Python MCP server implementation is available at https://github.com/yourusername/jira_python_mcp and can be installed via pip. It provides both basic Jira functionality and advanced features like comprehensive ticket summaries.

Please explain your design decisions and provide complete implementation for all files required.
```

### Example Project Idea: Jira Development Assistant

One practical way to utilize this MCP server is to create a project that acts as a Jira development assistant. This tool could:

1. Help developers create tickets based on code TODOs
2. Monitor progress on tickets assigned to the team
3. Provide daily summaries of Jira activity
4. Integrate with Git commits to automatically update ticket status
5. Generate reports on sprint progress and team velocity

Such a project would demonstrate the full potential of the Jira MCP server while creating a useful tool for development teams.
