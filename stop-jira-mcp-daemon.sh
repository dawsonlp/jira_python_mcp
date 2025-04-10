#!/bin/bash
# stop-jira-mcp-daemon.sh

# Stop the daemon container
docker compose down

echo "✅ Jira MCP daemon stopped"
