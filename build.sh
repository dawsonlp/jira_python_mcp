#!/bin/bash
set -e

echo "Building Jira Python MCP Server..."

# Check for Python 3.12+
PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ( [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ] ); then
    echo "Error: Python 3.12+ is required. Found Python $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade pip, wheel, setuptools
echo "Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

# Install dependencies
echo "Installing dependencies..."
pip install -e ".[dev]"

# Create example environment file if it doesn't exist
if [ ! -f "jira_mcp.env" ] && [ -f "jira_mcp.env.example" ]; then
    echo "Creating jira_mcp.env from jira_mcp.env.example..."
    cp jira_mcp.env.example jira_mcp.env
    echo "Please edit jira_mcp.env to add your Jira credentials."
fi

# Update file permissions
echo "Setting executable permissions..."
chmod +x jira_python_mcp/server.py

echo "Build complete!"
echo ""
echo "To run the server directly (for testing):"
echo "  source venv/bin/activate"
echo "  python -m jira_python_mcp.server"
echo ""
echo "To install in editable mode (for development):"
echo "  pip install -e ."
echo ""
echo "To build and install system-wide:"
echo "  python -m build"
echo "  pip install dist/*.whl"
echo ""
echo "After installation, you can run the server using:"
echo "  jira-mcp-server"
