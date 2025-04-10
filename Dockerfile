FROM python:3.12-slim

WORKDIR /app

# Copy only requirements first to leverage Docker caching
COPY pyproject.toml readme.md ./

# Copy application code first (needed before we can install in editable mode)
COPY jira_python_mcp/ /app/jira_python_mcp/
COPY jira_mcp.env.example /app/

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir git+https://github.com/modelcontextprotocol/python-sdk.git

# Set permissions
RUN chmod +x /app/jira_python_mcp/server.py

# Set environment variable for env file location (can be overridden)
ENV JIRA_MCP_ENV_PATH=/app/jira_mcp.env

# Command to run the server
ENTRYPOINT ["python", "-m", "jira_python_mcp.server"]
