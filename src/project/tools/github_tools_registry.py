"""
GitHub Tools Registry for LLM Integration

This module provides a comprehensive registry of all GitHub tools that the LLM can call directly.
The LLM can access these tools through the deployment system or directly.
"""

import os
from typing import Dict, List, Optional, Any
from src.project.tools.github_helper import get_github_helper


class GitHubToolsRegistry:
    """
    Registry of all GitHub tools available for LLM to call.
    
    This class provides a unified interface for the LLM to access
    all GitHub capabilities including issues, PRs, branches, workflows, etc.
    """
    
    def __init__(self):
        """Initialize the GitHub tools registry."""
        self.helper = get_github_helper()
        self.available = self.helper is not None
        
    def get_available_tools(self) -> Dict[str, str]:
        """
        Get list of all available GitHub tools that LLM can call.
        
        Returns:
            Dict[str, str]: Dictionary of tool names and descriptions
        """
        if not self.available:
            return {"error": "GitHub tools not available - check environment variables"}
        
        return {
            # File Management Tools
            "upload_file": "Upload a single file to GitHub repository",
            "upload_multiple_files": "Upload multiple files to GitHub repository",
            
            # Issue Management Tools  
            "create_issue": "Create a new GitHub issue with title, body, labels, assignees",
            "add_comment_to_issue": "Add a comment to an existing issue",
            "close_issue": "Close an issue with optional closing comment",
            "get_repository_issues": "List repository issues (open/closed) with filtering",
            
            # Pull Request Tools
            "create_pull_request": "Create a new pull request between branches",
            "create_branch": "Create a new branch from existing branch",
            
            # Workflow & CI/CD Tools
            "trigger_workflow": "Trigger a GitHub Actions workflow",
            "get_workflow_runs": "Get recent workflow run history",
            
            # Release Management Tools
            "create_release": "Create a new GitHub release with notes",
            
            # Repository Tools
            "test_connection": "Test GitHub API connection and get repo info"
        }
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a specific GitHub tool with parameters.
        
        Args:
            tool_name (str): Name of the tool to call
            **kwargs: Tool-specific parameters
            
        Returns:
            Dict[str, Any]: Tool execution result
        """
        if not self.available:
            return {
                "status": "error",
                "error": "GitHub tools not available. Check GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO environment variables."
            }
        
        # Map tool names to helper methods
        tool_mapping = {
            "upload_file": self.helper.upload_file,
            "upload_multiple_files": self.helper.upload_multiple_files,
            "create_issue": self.helper.create_issue,
            "add_comment_to_issue": self.helper.add_comment_to_issue,
            "close_issue": self.helper.close_issue,
            "get_repository_issues": self.helper.get_repository_issues,
            "create_pull_request": self.helper.create_pull_request,
            "create_branch": self.helper.create_branch,
            "trigger_workflow": self.helper.trigger_workflow,
            "get_workflow_runs": self.helper.get_workflow_runs,
            "create_release": self.helper.create_release,
            "test_connection": self.helper.test_connection
        }
        
        if tool_name not in tool_mapping:
            return {
                "status": "error",
                "error": f"Unknown tool: {tool_name}. Available tools: {list(tool_mapping.keys())}"
            }
        
        try:
            method = tool_mapping[tool_name]
            result = method(**kwargs)
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": f"Error calling {tool_name}: {str(e)}"
            }
    
    def get_tool_documentation(self, tool_name: str = None) -> Dict[str, Any]:
        """
        Get detailed documentation for GitHub tools.
        
        Args:
            tool_name (str, optional): Specific tool name, or None for all tools
            
        Returns:
            Dict[str, Any]: Tool documentation
        """
        docs = {
            "upload_file": {
                "description": "Upload a single file to GitHub repository",
                "parameters": {
                    "file_path": "str - Path where file should be stored in repo",
                    "content": "str - File content to upload",
                    "message": "str, optional - Commit message"
                },
                "example": {
                    "file_path": "README.md",
                    "content": "# My Project\\nThis is a test file",
                    "message": "Add README file"
                }
            },
            
            "create_issue": {
                "description": "Create a new GitHub issue",
                "parameters": {
                    "title": "str - Issue title",
                    "body": "str, optional - Issue description",
                    "labels": "list, optional - List of label names",
                    "assignees": "list, optional - List of usernames to assign"
                },
                "example": {
                    "title": "Bug: Application crashes on startup",
                    "body": "Detailed description of the bug...",
                    "labels": ["bug", "critical"],
                    "assignees": ["username"]
                }
            },
            
            "create_pull_request": {
                "description": "Create a new pull request",
                "parameters": {
                    "title": "str - PR title",
                    "head": "str - Source branch name",
                    "base": "str - Target branch (default: main)",
                    "body": "str, optional - PR description",
                    "draft": "bool, optional - Create as draft PR"
                },
                "example": {
                    "title": "Add new feature",
                    "head": "feature/new-feature",
                    "base": "main",
                    "body": "This PR adds a new feature..."
                }
            },
            
            "create_branch": {
                "description": "Create a new branch from existing branch",
                "parameters": {
                    "branch_name": "str - Name of new branch",
                    "from_branch": "str, optional - Source branch (default: main)"
                },
                "example": {
                    "branch_name": "feature/awesome-feature",
                    "from_branch": "main"
                }
            },
            
            "trigger_workflow": {
                "description": "Trigger a GitHub Actions workflow",
                "parameters": {
                    "workflow_name": "str - Workflow filename (default: deploy.yml)"
                },
                "example": {
                    "workflow_name": "deploy.yml"
                }
            },
            
            "create_release": {
                "description": "Create a new GitHub release",
                "parameters": {
                    "version": "str - Version number",
                    "title": "str, optional - Release title",
                    "notes": "str, optional - Release notes"
                },
                "example": {
                    "version": "1.0.0",
                    "title": "First Release",
                    "notes": "Initial release with basic features"
                }
            },
            
            "add_comment_to_issue": {
                "description": "Add a comment to an existing issue",
                "parameters": {
                    "issue_number": "int - Issue number",
                    "comment": "str - Comment text"
                },
                "example": {
                    "issue_number": 1,
                    "comment": "This issue has been investigated..."
                }
            }
        }
        
        if tool_name:
            return docs.get(tool_name, {"error": f"No documentation for tool: {tool_name}"})
        
        return docs


# Create global registry instance
github_tools = GitHubToolsRegistry()


def llm_call_github_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Simplified function for LLM to call GitHub tools.
    
    Args:
        tool_name (str): Name of the GitHub tool to call
        **kwargs: Tool-specific parameters
        
    Returns:
        Dict[str, Any]: Tool execution result
    """
    return github_tools.call_tool(tool_name, **kwargs)


def llm_get_github_tools() -> Dict[str, str]:
    """
    Get list of available GitHub tools for LLM.
    
    Returns:
        Dict[str, str]: Available tools and descriptions
    """
    return github_tools.get_available_tools()


def llm_github_tool_help(tool_name: str = None) -> Dict[str, Any]:
    """
    Get help documentation for GitHub tools.
    
    Args:
        tool_name (str, optional): Specific tool name for detailed help
        
    Returns:
        Dict[str, Any]: Tool documentation
    """
    return github_tools.get_tool_documentation(tool_name)


# Example usage for LLM
if __name__ == "__main__":
    # Show available tools
    print("🔧 Available GitHub Tools for LLM:")
    tools = llm_get_github_tools()
    for tool, description in tools.items():
        print(f"  • {tool}: {description}")
    
    print("\\n📖 Example tool usage:")
    print("  result = llm_call_github_tool('create_issue', title='Bug Report', body='Description...')")
    print("  result = llm_call_github_tool('create_branch', branch_name='feature/new-feature')")
    print("  result = llm_call_github_tool('upload_file', file_path='test.txt', content='Hello World')")
