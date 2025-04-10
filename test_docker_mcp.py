#!/usr/bin/env python3
"""
Test script for Jira MCP server running in Docker.

This script shows how to test the Docker-based MCP server.
It requires the Docker container to be running or properly configured
in your MCP settings file.

Usage:
    1. Build the Docker image: ./build-docker.sh
    2. Copy the Docker MCP config to your settings:
       cp docker_fixed_mcp_config.json ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
    3. Run this test script: python test_docker_mcp.py
"""

import json
import sys
import platform
import os
import subprocess
from pathlib import Path

# Colors for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_colored(message, color):
    """Print a colored message to the terminal."""
    print(f"{color}{message}{RESET}")

def print_section(title):
    """Print a section title."""
    print(f"\n{BOLD}{YELLOW}=== {title} ==={RESET}\n")

def run_command(command):
    """Run a command and return its output."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr

def verify_docker_image():
    """Verify that the Docker image exists."""
    print_section("Checking Docker Image")
    
    returncode, stdout, stderr = run_command("docker images | grep jira-mcp-server")
    
    if returncode == 0:
        print_colored("✓ Docker image 'jira-mcp-server' found", GREEN)
        return True
    else:
        print_colored("✗ Docker image 'jira-mcp-server' not found", RED)
        print_colored("Please build the image with: ./build-docker.sh", YELLOW)
        return False

def verify_mcp_config():
    """Verify that the MCP configuration exists."""
    print_section("Checking MCP Configuration")
    
    # Determine OS and config location
    if platform.system() == "Windows":
        config_path = os.path.join(os.environ.get("APPDATA", ""), "Code", "User", "globalStorage", "saoudrizwan.claude-dev", "settings", "cline_mcp_settings.json")
    else:
        config_path = os.path.expanduser("~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json")
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        print_colored(f"✗ MCP configuration not found at: {config_path}", RED)
        print_colored(f"Please copy the Docker configuration with:", YELLOW)
        print_colored(f"  cp docker_fixed_mcp_config.json {config_path}", YELLOW)
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config and 'jira' in config['mcpServers']:
            jira_config = config['mcpServers']['jira']
            if jira_config.get('command') == 'docker' and 'jira-mcp-server' in str(jira_config.get('args', [])):
                print_colored("✓ MCP configuration contains Docker setup for Jira", GREEN)
                return True
            else:
                print_colored("✗ MCP configuration does not contain Docker setup for Jira", RED)
                print_colored(f"Please copy the Docker configuration with:", YELLOW)
                print_colored(f"  cp docker_fixed_mcp_config.json {config_path}", YELLOW)
                return False
        else:
            print_colored("✗ MCP configuration does not contain Jira server settings", RED)
            print_colored(f"Please copy the Docker configuration with:", YELLOW)
            print_colored(f"  cp docker_fixed_mcp_config.json {config_path}", YELLOW)
            return False
    except Exception as e:
        print_colored(f"✗ Error reading MCP configuration: {e}", RED)
        return False

def verify_env_file():
    """Verify that the environment file exists."""
    print_section("Checking Environment File")
    
    env_path = Path("jira_mcp.env")
    
    if not env_path.exists():
        print_colored("✗ Environment file not found: jira_mcp.env", RED)
        print_colored("Please create the environment file from the example:", YELLOW)
        print_colored("  cp jira_mcp.env.example jira_mcp.env", YELLOW)
        print_colored("  edit jira_mcp.env and add your Jira credentials", YELLOW)
        return False
    
    required_vars = ["JIRA_SERVER"]
    auth_vars = [
        ["JIRA_EMAIL", "JIRA_API_TOKEN"],
        ["JIRA_OAUTH_ACCESS_TOKEN", "JIRA_OAUTH_ACCESS_TOKEN_SECRET", "JIRA_CONSUMER_KEY", "JIRA_KEY_CERT"]
    ]
    
    env_content = open(env_path, 'r').read()
    
    # Check required variables
    missing_required = [var for var in required_vars if f"{var}=" not in env_content]
    if missing_required:
        print_colored(f"✗ Missing required environment variables: {', '.join(missing_required)}", RED)
        return False
    
    # Check auth variables
    has_auth = False
    for auth_group in auth_vars:
        if all(f"{var}=" in env_content for var in auth_group):
            has_auth = True
            break
    
    if not has_auth:
        print_colored("✗ Missing authentication variables. You need either:", RED)
        print_colored("  - JIRA_EMAIL and JIRA_API_TOKEN", YELLOW)
        print_colored("  - or OAuth credentials (JIRA_OAUTH_*)", YELLOW)
        return False
    
    print_colored("✓ Environment file exists and contains required variables", GREEN)
    return True

def test_docker_run():
    """Test running the Docker container directly."""
    print_section("Testing Docker Container")
    
    # Use a non-interactive command that will exit immediately
    command = "docker run --rm -v $(pwd)/jira_mcp.env:/app/jira_mcp.env:ro jira-mcp-server python -c \"print('Container test successful')\""
    returncode, stdout, stderr = run_command(command)
    
    if returncode == 0 and "Container test successful" in stdout:
        print_colored("✓ Docker container runs successfully", GREEN)
        print_colored(f"Output: {stdout.strip()}", GREEN)
        return True
    else:
        print_colored("✗ Error running Docker container", RED)
        if stdout:
            print_colored(f"Output: {stdout}", YELLOW)
        if stderr:
            print_colored(f"Error: {stderr}", RED)
        return False

def main():
    """Main test function."""
    print_colored(f"\n{BOLD}Jira MCP Docker Test Script{RESET}\n", YELLOW)
    
    tests = [
        verify_docker_image,
        verify_env_file,
        test_docker_run,
        verify_mcp_config
    ]
    
    success = True
    for test in tests:
        if not test():
            success = False
    
    print_section("Summary")
    if success:
        print_colored("✓ All checks passed! The Docker MCP server should be ready to use.", GREEN)
        print_colored("You can now use the Jira MCP server with AI assistants through Docker.", GREEN)
    else:
        print_colored("✗ Some checks failed. Please address the issues above.", RED)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
