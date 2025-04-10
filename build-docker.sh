#!/bin/bash
set -e

echo "Building Jira MCP Docker image..."
# Use --load to ensure the image is loaded into the Docker daemon
docker build --load -t jira-mcp-server .

echo "Docker image built successfully!"
echo ""
echo "To run the server using Docker:"
echo "  docker run --rm -i -v $(pwd)/jira_mcp.env:/app/jira_mcp.env:ro jira-mcp-server"
echo ""
echo "To run with Docker Compose:"
echo "  docker-compose up"
echo ""
echo "For VSCode integration, update your MCP settings file to use:"
echo "  \"command\": \"docker\","
echo "  \"args\": [\"run\", \"--rm\", \"-i\", \"jira-mcp-server\"],"
echo ""
