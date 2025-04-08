"""Advanced Jira client with higher-level abstractions."""

from datetime import datetime
from typing import Dict, List, Any

from jira_python_mcp.base.client import JiraClient


class AdvancedJiraClient:
    """Advanced Jira client with higher-level abstractions."""

    def __init__(self, base_client: JiraClient):
        """Initialize Advanced Jira client.

        Args:
            base_client: Base Jira client.
        """
        self.base_client = base_client

    def get_ticket_summary(self, issue_key: str) -> Dict[str, Any]:
        """Get comprehensive ticket summary.

        This method provides a complete overview of a ticket including:
        - Basic ticket details
        - Description
        - Comments
        - Timeline of events
        - Roles of different Jira accounts
        - Current status and type

        Args:
            issue_key: The issue key (e.g., PROJ-123).

        Returns:
            Dict[str, Any]: Comprehensive ticket summary.
        """
        # Get basic issue details
        issue_details = self.base_client.get_issue(issue_key)
        
        # Get comments
        comments = self.base_client.get_comments(issue_key)
        
        # Get available transitions (for status context)
        transitions = self.base_client.get_transitions(issue_key)
        
        # Build timeline events
        timeline_events = self._build_timeline(issue_details, comments)
        
        # Identify roles
        roles = self._identify_roles(issue_details, comments)
        
        # Build comprehensive summary
        return {
            "ticket_key": issue_key,
            "summary": issue_details["summary"],
            "description": issue_details["description"],
            "current_status": {
                "name": issue_details["status"],
                "type": issue_details["issue_type"],
                "priority": issue_details["priority"],
                "possible_transitions": [t["name"] for t in transitions]
            },
            "timeline": timeline_events,
            "roles": roles,
            "comments": comments,
            "urls": {
                "web_ui": issue_details["url"]
            }
        }

    def _build_timeline(self, issue_details: Dict[str, Any], comments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build timeline of events for an issue.

        Args:
            issue_details: Issue details.
            comments: Issue comments.

        Returns:
            List[Dict[str, Any]]: Timeline events.
        """
        # Start with creation event
        timeline = [
            {
                "type": "created",
                "timestamp": issue_details["created"],
                "actor": issue_details["reporter"],
                "details": f"Ticket created by {issue_details['reporter']}"
            }
        ]
        
        # Add comment events
        for comment in comments:
            timeline.append({
                "type": "comment",
                "timestamp": comment["created"],
                "actor": comment["author"],
                "details": f"Comment added by {comment['author']}"
            })
            
            # If comment was updated, add that as an event too
            if comment["updated"] != comment["created"]:
                timeline.append({
                    "type": "comment_edited",
                    "timestamp": comment["updated"],
                    "actor": comment["author"],
                    "details": f"Comment edited by {comment['author']}"
                })
        
        # Add last update event if different from creation and not covered by comments
        if issue_details["updated"] != issue_details["created"] and not any(event["timestamp"] == issue_details["updated"] for event in timeline):
            timeline.append({
                "type": "updated",
                "timestamp": issue_details["updated"],
                "actor": "Unknown",  # We don't know who updated it from just the issue details
                "details": "Ticket updated"
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda event: datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00')))
        
        return timeline

    def _identify_roles(self, issue_details: Dict[str, Any], comments: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify roles played by different Jira accounts.

        Args:
            issue_details: Issue details.
            comments: Issue comments.

        Returns:
            Dict[str, List[str]]: Roles played by different accounts.
        """
        roles = {}
        
        # Add reporter
        reporter = issue_details["reporter"]
        roles[reporter] = ["Reporter"]
        
        # Add assignee if not unassigned
        assignee = issue_details["assignee"]
        if assignee != "Unassigned":
            if assignee in roles:
                roles[assignee].append("Assignee")
            else:
                roles[assignee] = ["Assignee"]
        
        # Add commenters
        for comment in comments:
            author = comment["author"]
            if author in roles:
                if "Commenter" not in roles[author]:
                    roles[author].append("Commenter")
            else:
                roles[author] = ["Commenter"]
        
        return roles

    @classmethod
    def from_base_client(cls, base_client: JiraClient) -> "AdvancedJiraClient":
        """Create Advanced Jira client from Base Jira client.

        Args:
            base_client: Base Jira client.

        Returns:
            AdvancedJiraClient: Advanced Jira client instance.
        """
        return cls(base_client)

    @classmethod
    def from_env(cls) -> "AdvancedJiraClient":
        """Create Advanced Jira client from environment variables.

        Returns:
            AdvancedJiraClient: Advanced Jira client instance.
        """
        base_client = JiraClient.from_env()
        return cls(base_client)
