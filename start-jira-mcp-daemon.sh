#!/bin/bash
# start-jira-mcp-daemon.sh

# Build and start the daemon container
docker compose up -d jira-mcp-daemon

# Wait for container to be ready
sleep 2

# Verify container is running
if docker ps | grep -q jira-mcp-daemon; then
  echo "✅ Jira MCP daemon is running"
  # Copy config to the appropriate locations
  # Main Cline MCP settings
  CLINE_CONFIG_PATH="$HOME/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json"
  cp daemon_mcp_config.json "$CLINE_CONFIG_PATH"
  
  # Also update the fixed config in the repo for reference
  cp daemon_mcp_config.json fixed_cline_mcp_settings.json
  
  echo "✅ MCP configurations updated"
else
  echo "❌ Failed to start Jira MCP daemon"
  exit 1
fi
