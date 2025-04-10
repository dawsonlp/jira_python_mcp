# Jira MCP Daemon Approach

This document explains the long-running container approach for the Jira MCP server. This approach provides better resource utilization and performance for shared environments.

## How It Works

Instead of creating a new container for each MCP session (which is inefficient), this approach:

1. Maintains a single long-running container (`jira-mcp-daemon`)
2. Uses `docker exec` to run MCP server instances within that container
3. Shares resources across all instances

## Advantages

- **Resource Efficiency**: Single container instance for multiple MCP sessions
- **Startup Speed**: No container creation overhead for each session
- **Simpler Configuration**: Environment variables can be set once at container start
- **Better for Shared Hosting**: Works well in multi-user environments

## Files

- `docker-compose.yml` - Defines the long-running daemon container
- `daemon_mcp_config.json` - MCP configuration that uses `docker exec` 
- `start-jira-mcp-daemon.sh` - Script to start the daemon and update MCP config
- `stop-jira-mcp-daemon.sh` - Script to stop the daemon

## Usage

### Starting the Daemon

```bash
./start-jira-mcp-daemon.sh
```

This will:
1. Build and start the daemon container
2. Update the MCP configuration to use `docker exec`
3. Confirm successful startup

### Stopping the Daemon

```bash
./stop-jira-mcp-daemon.sh
```

This will shut down the container.

## Technical Details

The key difference in this approach is in how the MCP server is invoked:

**Traditional Approach:**
```json
"command": "docker",
"args": ["run", "--rm", "-i", "-v", "...", "jira-mcp-server"],
```

**Daemon Approach:**
```json
"command": "docker",
"args": ["exec", "-i", "jira-mcp-daemon", "python", "-m", "jira_python_mcp.server"],
```

The traditional approach creates a new container for each MCP session, while the daemon approach executes new processes within an existing container.

## Troubleshooting

If the daemon fails to start:
1. Check Docker is running
2. Verify the jira_mcp.env file exists
3. Check docker logs: `docker logs jira-mcp-daemon`

If an MCP tool fails:
1. Ensure the daemon is running: `docker ps | grep jira-mcp-daemon`
2. Check the configuration was properly updated
3. Restart the daemon if needed
