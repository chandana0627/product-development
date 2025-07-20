"""
MCP Server Configuration for GitHub integration

This module provides configuration and setup for Model Context Protocol server
that interfaces with GitHub APIs for deployment automation.
"""

import json
import os
from typing import Dict, Any, List
from dataclasses import dataclass, asdict


@dataclass
class MCPServerConfig:
    """Configuration for MCP Server."""
    name: str = "github-deployment-mcp"
    version: str = "1.0.0"
    description: str = "GitHub MCP server for deployment automation"
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = [
                "repository_management",
                "deployment_tracking", 
                "workflow_automation",
                "secret_management",
                "release_management"
            ]


@dataclass
class GitHubMCPServerConfig:
    """GitHub-specific MCP server configuration."""
    server: MCPServerConfig
    github: Dict[str, Any]
    
    def __post_init__(self):
        if not self.github:
            self.github = {
                "api_base_url": "https://api.github.com",
                "timeout": 30,
                "max_retries": 3,
                "rate_limit_per_hour": 5000
            }


def create_mcp_config(
    github_token: str = None,
    github_owner: str = None, 
    github_repo: str = None,
    config_path: str = None
) -> GitHubMCPServerConfig:
    """
    Create MCP server configuration.
    
    Args:
        github_token (str): GitHub personal access token
        github_owner (str): GitHub repository owner
        github_repo (str): GitHub repository name
        config_path (str): Path to save configuration file
        
    Returns:
        GitHubMCPServerConfig: Complete MCP server configuration
    """
    
    # Get values from environment if not provided
    github_token = github_token or os.getenv("GITHUB_TOKEN")
    github_owner = github_owner or os.getenv("GITHUB_OWNER") 
    github_repo = github_repo or os.getenv("GITHUB_REPO")
    
    server_config = MCPServerConfig()
    
    github_config = {
        "api_base_url": "https://api.github.com",
        "token": github_token,
        "owner": github_owner,
        "repo": github_repo,
        "timeout": 30,
        "max_retries": 3,
        "rate_limit_per_hour": 5000,
        "webhook_secret": os.getenv("GITHUB_WEBHOOK_SECRET"),
        "deployment_environments": ["development", "staging", "production"],
        "auto_merge_enabled": False,
        "required_status_checks": ["ci", "security-scan"],
        "protected_branches": ["main", "production"]
    }
    
    config = GitHubMCPServerConfig(
        server=server_config,
        github=github_config
    )
    
    # Save configuration to file if path provided
    if config_path:
        save_mcp_config(config, config_path)
    
    return config


def save_mcp_config(config: GitHubMCPServerConfig, config_path: str):
    """
    Save MCP configuration to JSON file.
    
    Args:
        config (GitHubMCPServerConfig): Configuration to save
        config_path (str): Path to save configuration
    """
    config_dict = {
        "server": asdict(config.server),
        "github": config.github
    }
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, 'w') as f:
        json.dump(config_dict, f, indent=2)


def load_mcp_config(config_path: str) -> GitHubMCPServerConfig:
    """
    Load MCP configuration from JSON file.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        GitHubMCPServerConfig: Loaded configuration
    """
    with open(config_path, 'r') as f:
        config_dict = json.load(f)
    
    server_config = MCPServerConfig(**config_dict["server"])
    
    return GitHubMCPServerConfig(
        server=server_config,
        github=config_dict["github"]
    )


def get_default_mcp_tools() -> Dict[str, Dict[str, Any]]:
    """
    Get default MCP tools configuration for GitHub integration.
    
    Returns:
        Dict[str, Dict[str, Any]]: Default tools configuration
    """
    return {
        "repository_tools": {
            "create_repository": {
                "description": "Create a new GitHub repository",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False},
                    "private": {"type": "boolean", "required": False, "default": False}
                }
            },
            "upload_files": {
                "description": "Upload files to repository", 
                "parameters": {
                    "files": {"type": "object", "required": True},
                    "commit_message": {"type": "string", "required": False}
                }
            }
        },
        "deployment_tools": {
            "create_deployment": {
                "description": "Create a GitHub deployment",
                "parameters": {
                    "environment": {"type": "string", "required": False, "default": "production"},
                    "description": {"type": "string", "required": False}
                }
            },
            "update_deployment_status": {
                "description": "Update deployment status",
                "parameters": {
                    "deployment_id": {"type": "integer", "required": True},
                    "state": {"type": "string", "required": True},
                    "description": {"type": "string", "required": False}
                }
            }
        },
        "workflow_tools": {
            "trigger_workflow": {
                "description": "Trigger GitHub Actions workflow",
                "parameters": {
                    "workflow_file": {"type": "string", "required": True},
                    "inputs": {"type": "object", "required": False}
                }
            },
            "get_workflow_status": {
                "description": "Get workflow run status",
                "parameters": {
                    "workflow_file": {"type": "string", "required": True},
                    "limit": {"type": "integer", "required": False, "default": 10}
                }
            }
        },
        "secret_tools": {
            "create_secret": {
                "description": "Create or update repository secret",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "value": {"type": "string", "required": True}
                }
            }
        },
        "release_tools": {
            "create_release": {
                "description": "Create a GitHub release",
                "parameters": {
                    "tag_name": {"type": "string", "required": True},
                    "name": {"type": "string", "required": True},
                    "body": {"type": "string", "required": False},
                    "draft": {"type": "boolean", "required": False, "default": False}
                }
            }
        }
    }


# Default configuration template
DEFAULT_MCP_CONFIG_TEMPLATE = {
    "server": {
        "name": "github-deployment-mcp",
        "version": "1.0.0", 
        "description": "GitHub MCP server for deployment automation",
        "capabilities": [
            "repository_management",
            "deployment_tracking",
            "workflow_automation", 
            "secret_management",
            "release_management"
        ]
    },
    "github": {
        "api_base_url": "https://api.github.com",
        "token": "${GITHUB_TOKEN}",
        "owner": "${GITHUB_OWNER}",
        "repo": "${GITHUB_REPO}",
        "timeout": 30,
        "max_retries": 3,
        "rate_limit_per_hour": 5000,
        "webhook_secret": "${GITHUB_WEBHOOK_SECRET}",
        "deployment_environments": ["development", "staging", "production"],
        "auto_merge_enabled": False,
        "required_status_checks": ["ci", "security-scan"],
        "protected_branches": ["main", "production"]
    }
}
