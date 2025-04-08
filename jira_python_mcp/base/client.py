"""Basic Jira client for interacting with Jira API."""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional

from jira import JIRA
from jira.resources import Project


@dataclass
class JiraConfig:
    """Configuration for Jira client."""

    server: str
    email: Optional[str] = None
    api_token: Optional[str] = None
    oauth_access_token: Optional[str] = None
    oauth_access_token_secret: Optional[str] = None
    consumer_key: Optional[str] = None
    key_cert_path: Optional[str] = None
    timeout: int = 60


class JiraClient:
    """Client for interacting with Jira API."""

    def __init__(self, config: JiraConfig):
        """Initialize Jira client.

        Args:
            config: Jira configuration.
        """
        self.config = config
        self.client = self._create_client()

    def _create_client(self) -> JIRA:
        """Create Jira client.

        Returns:
            JIRA: Jira client instance.
        """
        # Basic authentication
        if self.config.email and self.config.api_token:
            return JIRA(
                server=self.config.server,
                basic_auth=(self.config.email, self.config.api_token),
                timeout=self.config.timeout,
            )
        
        # OAuth authentication
        if (
            self.config.oauth_access_token
            and self.config.oauth_access_token_secret
            and self.config.consumer_key
            and self.config.key_cert_path
        ):
            return JIRA(
                server=self.config.server,
                oauth={
                    "access_token": self.config.oauth_access_token,
                    "access_token_secret": self.config.oauth_access_token_secret,
                    "consumer_key": self.config.consumer_key,
                    "key_cert": self.config.key_cert_path,
                },
                timeout=self.config.timeout,
            )
        
        raise ValueError("Invalid Jira configuration. Either basic auth or OAuth must be provided.")

    def list_projects(self) -> List[Dict[str, str]]:
        """List all projects.

        Returns:
            List[Dict[str, str]]: List of projects with their details.
        """
        projects = self.client.projects()
        return [
            {
                "id": project.id,
                "key": project.key,
                "name": project.name,
                "lead": getattr(project, "lead", {}).get("displayName", "Unknown") if hasattr(project, "lead") else "Unknown",
                "url": f"{self.config.server}/browse/{project.key}",
            }
            for project in projects
        ]
    
    def get_issue(self, issue_key: str) -> Dict[str, any]:
        """Get issue details.

        Args:
            issue_key: The issue key (e.g., PROJ-123).

        Returns:
            Dict[str, any]: Issue details.
        """
        issue = self.client.issue(issue_key)
        return {
            "id": issue.id,
            "key": issue.key,
            "summary": issue.fields.summary,
            "description": issue.fields.description or "",
            "status": issue.fields.status.name,
            "issue_type": issue.fields.issuetype.name,
            "project": issue.fields.project.key,
            "created": issue.fields.created,
            "updated": issue.fields.updated,
            "reporter": getattr(issue.fields.reporter, "displayName", "Unknown") if hasattr(issue.fields, "reporter") else "Unknown",
            "assignee": getattr(issue.fields.assignee, "displayName", "Unassigned") if hasattr(issue.fields, "assignee") and issue.fields.assignee else "Unassigned",
            "priority": getattr(issue.fields.priority, "name", "None") if hasattr(issue.fields, "priority") and issue.fields.priority else "None",
            "url": f"{self.config.server}/browse/{issue.key}",
        }
    
    def get_comments(self, issue_key: str) -> List[Dict[str, any]]:
        """Get comments for an issue.

        Args:
            issue_key: The issue key (e.g., PROJ-123).

        Returns:
            List[Dict[str, any]]: List of comments.
        """
        comments = self.client.comments(issue_key)
        return [
            {
                "id": comment.id,
                "author": comment.author.displayName if hasattr(comment, "author") else "Unknown",
                "body": comment.body,
                "created": comment.created,
                "updated": comment.updated,
            }
            for comment in comments
        ]
    
    def get_transitions(self, issue_key: str) -> List[Dict[str, str]]:
        """Get available transitions for an issue.

        Args:
            issue_key: The issue key (e.g., PROJ-123).

        Returns:
            List[Dict[str, str]]: List of available transitions.
        """
        transitions = self.client.transitions(issue_key)
        return [
            {
                "id": transition["id"],
                "name": transition["name"],
                "to_status": transition["to"]["name"],
            }
            for transition in transitions
        ]

    @classmethod
    def from_env(cls) -> "JiraClient":
        """Create Jira client from environment variables.

        Returns:
            JiraClient: Jira client instance.
        """
        server = os.environ.get("JIRA_SERVER")
        if not server:
            raise ValueError("JIRA_SERVER environment variable is required")

        config = JiraConfig(
            server=server,
            email=os.environ.get("JIRA_EMAIL"),
            api_token=os.environ.get("JIRA_API_TOKEN"),
            oauth_access_token=os.environ.get("JIRA_OAUTH_ACCESS_TOKEN"),
            oauth_access_token_secret=os.environ.get("JIRA_OAUTH_ACCESS_TOKEN_SECRET"),
            consumer_key=os.environ.get("JIRA_CONSUMER_KEY"),
            key_cert_path=os.environ.get("JIRA_KEY_CERT"),
            timeout=int(os.environ.get("JIRA_TIMEOUT", "60")),
        )

        return cls(config)
