# Jira Python MCP Server

This project provides a [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/) server for exposing Jira functionality. It allows AI assistants to interact with Jira through a standardized interface.

The server is structured with separate modules for basic and advanced functionality:
- **Basic functionality**: Direct mappings to Jira API (list projects, get issue details, etc.)
- **Advanced functionality**: Higher-level abstractions that combine multiple API calls to provide more comprehensive data (e.g., complete ticket summaries with timeline and role information)

## Table of Contents

- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Available Tools](#available-tools)
- [MCP Integration](#mcp-integration)
- [Configuration](#configuration)
- [Extending the Server](#extending-the-server)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)

## Prerequisites

- Python 3.12 or higher
- A Jira account with API token access
- Jira Cloud or Server instance URL

## Setup and Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/dawsonlp/jira_python_mcp.git
   cd jira_python_mcp
   ```

2. Run the build script to set up the environment:
   ```bash
   ./build.sh
   ```
   This script will:
   - Check your Python version
   - Create a virtual environment
   - Install dependencies
   - Create a template environment file from the example

3. Configure your Jira credentials by editing the `jira_mcp.env` file created by the build script:
   ```bash
   nano jira_mcp.env
   ```
   Add your Jira server URL, email, and API token:
   ```
   JIRA_SERVER=https://your-domain.atlassian.net
   JIRA_EMAIL=your-email@example.com
   JIRA_API_TOKEN=your-api-token
   ```

4. Test the installation:
   ```bash
   source venv/bin/activate
   python -m jira_python_mcp.server
   ```
   You should see a message indicating the server has started.

## Usage

### Running the MCP Server

After installation, you can run the server using either of these methods:

```bash
# After installing the package:
jira-mcp-server

# OR directly from the source:
source venv/bin/activate
python -m jira_python_mcp.server
```

By default, the server logs information to:
- Console
- `jira_mcp.log` file in the current directory

### Available Tools

The server provides the following tools:

#### Basic Tools
- `list_projects`: Lists all projects in your Jira instance
- `get_issue`: Get basic information about a Jira issue
- `get_comments`: Get comments for a Jira issue

#### Advanced Tools
- `get_ticket_summary`: Get comprehensive ticket summary including:
  - Basic ticket details
  - Description
  - Comments
  - Timeline of events
  - Roles of different Jira accounts
  - Current status and type

## MCP Integration

### What is MCP?

The Model Context Protocol (MCP) is a standard that allows AI models to access external tools and resources. By implementing the MCP standard, this server enables AI assistants to interact with Jira data in a structured way.

### Integrating with AI Assistants

To use this MCP server with AI assistants like Claude, you need to:

1. Install the server as described above
2. Configure the AI assistant to connect to this MCP server
3. The AI can then use the provided tools to access Jira data

### Claude Desktop Integration

To add this MCP server to Claude Desktop:

1. Build and install the server using the instructions above
2. Edit the Claude Desktop configuration file:
   - Location: `~/.config/Claude/claude_desktop_config.json` (Linux/macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows)
   - Add the following to the `mcpServers` object:

```json
"jira": {
  "command": "jira-mcp-server",
  "args": [],
  "env": {
    "JIRA_MCP_ENV_PATH": "/absolute/path/to/your/jira_mcp.env"
  },
  "disabled": false,
  "autoApprove": []
}
```

3. Restart Claude Desktop

### VSCode Extension Integration

To add this MCP server to the Claude VSCode extension:

1. Build and install the server using the instructions above
2. Edit the Claude VSCode extension settings:
   - Location: `~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
   - Add the following to the `mcpServers` object:

```json
"jira": {
  "command": "jira-mcp-server",
  "args": [],
  "env": {
    "JIRA_MCP_ENV_PATH": "/absolute/path/to/your/jira_mcp.env"
  },
  "disabled": false,
  "autoApprove": []
}
```

3. Restart VSCode or reload the Claude extension

## Configuration

### Environment Variables

The server supports the following environment variables:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| JIRA_SERVER | Your Jira instance URL | Yes | None |
| JIRA_EMAIL | Email for basic authentication | No* | None |
| JIRA_API_TOKEN | API token for basic authentication | No* | None |
| JIRA_OAUTH_ACCESS_TOKEN | OAuth access token | No* | None |
| JIRA_OAUTH_ACCESS_TOKEN_SECRET | OAuth access token secret | No* | None |
| JIRA_CONSUMER_KEY | OAuth consumer key | No* | None |
| JIRA_KEY_CERT | Path to OAuth key certificate | No* | None |
| JIRA_TIMEOUT | Connection timeout in seconds | No | 60 |
| LOG_LEVEL | Logging level | No | INFO |
| JIRA_MCP_ENV_PATH | Path to environment file | No | jira_mcp.env |

*Either basic authentication (email + API token) or OAuth is required.

### Custom Environment File

You can specify a custom environment file path using:

```bash
JIRA_MCP_ENV_PATH=/path/to/your/custom.env jira-mcp-server
```

## Extending the Server

The server is designed to be easily extensible. You can add new functionality by modifying the existing modules or creating new ones.

### Project Structure

```
jira_python_mcp/
├── jira_python_mcp/              # Main package
│   ├── __init__.py               # Package initialization
│   ├── server.py                 # MCP server implementation
│   ├── base/                     # Basic Jira functionality
│   │   ├── __init__.py
│   │   └── client.py             # Basic Jira client (direct API calls)
│   └── advanced/                 # Advanced Jira functionality
│       ├── __init__.py
│       └── client.py             # Advanced client (higher-level abstractions)
├── build.sh                      # Build script
├── jira_mcp.env.example          # Example environment file
├── pyproject.toml                # Project configuration
└── readme.md                     # This file
```

### Adding Basic Functionality

To add new basic Jira functionality (direct API calls):

1. Add new methods to `JiraClient` in `jira_python_mcp/base/client.py`

```python
def new_method(self, param1, param2):
    """Documentation for your new method."""
    # Implement your method using self.client (JIRA instance)
    result = self.client.some_jira_api_call(param1, param2)
    return result
```

2. Add a new tool definition in `server.py`'s `_handle_list_tools` method:

```python
ToolDescription(
    name="your_new_tool_name",
    description="Description of what your tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of param1",
            },
            "param2": {
                "type": "integer",
                "description": "Description of param2",
            }
        },
        "required": ["param1"],  # List required parameters
        "additionalProperties": False,
    },
),
```

3. Implement the handler in the `_handle_call_tool` method:

```python
elif tool_name == "your_new_tool_name":
    return await self._your_new_tool_handler(params)
```

4. Add the implementation method:

```python
async def _your_new_tool_handler(self, params: Dict[str, Any]) -> Dict[str, List[ToolContentItem]]:
    """Handle your new tool.
    
    Args:
        params: The request parameters.
        
    Returns:
        Dict[str, List[ToolContentItem]]: The result.
    """
    try:
        param1 = params.get("arguments", {}).get("param1")
        param2 = params.get("arguments", {}).get("param2", default_value)
        
        if not param1:
            raise McpError(ErrorCode.InvalidParams, "Missing param1 parameter")
        
        result = self.base_client.new_method(param1, param2)
        return {
            "content": [
                ToolContentItem(
                    type="text",
                    text=json.dumps(result, indent=2),
                )
            ]
        }
    except Exception as e:
        logger.error(f"Error in your new tool: {e}")
        return {
            "content": [
                ToolContentItem(
                    type="text",
                    text=f"Error in your new tool: {e}",
                )
            ],
            "is_error": True,
        }
```

### Adding Advanced Functionality

To add new advanced functionality (higher-level abstractions):

1. Add new methods to `AdvancedJiraClient` in `jira_python_mcp/advanced/client.py`

```python
def new_advanced_method(self, param1):
    """Documentation for your new advanced method."""
    # Use basic client methods to build higher-level functionality
    basic_data1 = self.base_client.method1(param1)
    basic_data2 = self.base_client.method2(param1)
    
    # Process and combine the data
    processed_data = self._process_data(basic_data1, basic_data2)
    
    return processed_data

def _process_data(self, data1, data2):
    """Process and combine data from multiple sources."""
    # Implement your processing logic
    result = {
        "combined_data": {
            "from_source1": data1,
            "from_source2": data2,
            "processed_info": self._extract_insights(data1, data2)
        }
    }
    return result
```

2. Follow the same steps as for basic functionality to add the tool definition and handler to `server.py`

### Creating a New Module

If your functionality fits neither the base nor advanced modules, you can create a new module:

1. Create a new directory: `mkdir -p jira_python_mcp/your_module`
2. Create the module files:
   - `jira_python_mcp/your_module/__init__.py`
   - `jira_python_mcp/your_module/client.py`
3. Implement your client class and methods
4. Import and use your new module in `server.py`

## Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/dawsonlp/jira_python_mcp.git
cd jira_python_mcp

# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
