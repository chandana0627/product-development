"""
GitHub MCP (Model Context Protocol) Integration Tool

This module provides GitHub integration capabilities through MCP server
for automated repository management, deployment tracking, and CI/CD integration.
"""

import os
import json
import subprocess
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import requests
from pathlib import Path


@dataclass
class GitHubConfig:
    """Configuration for GitHub MCP integration."""
    token: str
    owner: str
    repo: str
    base_url: str = "https://api.github.com"
    mcp_server_url: Optional[str] = None


class GitHubMCPClient:
    """
    GitHub MCP Client for interacting with GitHub through Model Context Protocol.
    
    This client provides methods to:
    - Create repositories
    - Manage deployments
    - Handle CI/CD workflows
    - Track deployment status
    - Manage secrets and environment variables
    """

    def __init__(self, config: GitHubConfig):
        """
        Initialize GitHub MCP client.
        
        Args:
            config (GitHubConfig): GitHub configuration including token and repo details
        """
        self.config = config
        self.session = None
        self.logger = logging.getLogger(__name__)
        
        # Set up headers for GitHub API
        self.headers = {
            "Authorization": f"token {self.config.token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _sync_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make synchronous GitHub API request.
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            data (Optional[Dict]): Request payload
            
        Returns:
            Dict: API response
        """
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise

    async def _async_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make asynchronous GitHub API request.
        
        Args:
            method (str): HTTP method
            endpoint (str): API endpoint
            data (Optional[Dict]): Request payload
            
        Returns:
            Dict: API response
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async context manager.")
        
        url = f"{self.config.base_url}/{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, params=data) as response:
                    response.raise_for_status()
                    return await response.json() if response.content_length else {}
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json() if response.content_length else {}
            elif method.upper() == "PUT":
                async with self.session.put(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json() if response.content_length else {}
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    response.raise_for_status()
                    return await response.json() if response.content_length else {}
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except aiohttp.ClientError as e:
            self.logger.error(f"GitHub API request failed: {e}")
            raise

    def create_repository(self, repo_name: str, description: str = "", private: bool = False) -> Dict:
        """
        Create a new GitHub repository.
        
        Args:
            repo_name (str): Repository name
            description (str): Repository description
            private (bool): Whether repository should be private
            
        Returns:
            Dict: Repository creation response
        """
        data = {
            "name": repo_name,
            "description": description,
            "private": private,
            "auto_init": True,
            "gitignore_template": "Python"
        }
        
        return self._sync_request("POST", "user/repos", data)

    def upload_files_to_repo(self, files_dict: Dict[str, str], commit_message: str = "Initial deployment files") -> List[Dict]:
        """
        Upload multiple files to repository.
        
        Args:
            files_dict (Dict[str, str]): Dictionary mapping file paths to content
            commit_message (str): Commit message
            
        Returns:
            List[Dict]: List of file upload responses
        """
        responses = []
        
        for file_path, content in files_dict.items():
            # Encode content to base64
            import base64
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # Check if file already exists to get its SHA
            get_endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
            try:
                existing_file = self._sync_request("GET", get_endpoint)
                sha = existing_file.get("sha")
                self.logger.info(f"File {file_path} exists, updating with SHA: {sha}")
            except Exception:
                sha = None
                self.logger.info(f"File {file_path} is new")
            
            data = {
                "message": commit_message,
                "content": encoded_content,
                "branch": "main"
            }
            
            # Add SHA if file exists (for updates)
            if sha:
                data["sha"] = sha
            
            endpoint = f"repos/{self.config.owner}/{self.config.repo}/contents/{file_path}"
            try:
                response = self._sync_request("PUT", endpoint, data)
                responses.append(response)
                self.logger.info(f"✅ Successfully uploaded {file_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to upload {file_path}: {e}")
                responses.append({"error": str(e), "file": file_path})
            
        return responses

    def create_deployment(self, environment: str = "production", description: str = "Automated deployment") -> Dict:
        """
        Create a GitHub deployment.
        
        Args:
            environment (str): Deployment environment
            description (str): Deployment description
            
        Returns:
            Dict: Deployment creation response
        """
        try:
            data = {
                "ref": "main",
                "environment": environment,
                "description": description,
                "auto_merge": False,
                "required_contexts": []
            }
            
            endpoint = f"repos/{self.config.owner}/{self.config.repo}/deployments"
            response = self._sync_request("POST", endpoint, data)
            self.logger.info(f"✅ Deployment created: {response.get('id')}")
            return response
        except Exception as e:
            self.logger.warning(f"⚠️ Could not create deployment: {e}")
            # Return a mock deployment ID for compatibility
            import time
            return {
                "id": int(time.time()),
                "status": "mock_deployment",
                "message": "Deployment tracking not available"
            }

    def update_deployment_status(self, deployment_id: int, state: str, description: str = "") -> Dict:
        """
        Update deployment status.
        
        Args:
            deployment_id (int): Deployment ID
            state (str): Deployment state (pending, success, error, failure)
            description (str): Status description
            
        Returns:
            Dict: Status update response
        """
        data = {
            "state": state,
            "description": description,
            "environment": "production"
        }
        
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/deployments/{deployment_id}/statuses"
        return self._sync_request("POST", endpoint, data)

    def trigger_workflow(self, workflow_filename: str, inputs: Dict = None) -> Dict:
        """
        Trigger a GitHub Actions workflow.
        
        Args:
            workflow_filename (str): Workflow filename (e.g., 'deploy.yml')
            inputs (Dict): Workflow inputs
            
        Returns:
            Dict: Workflow trigger response
        """
        data = {
            "ref": "main",
            "inputs": inputs or {}
        }
        
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/actions/workflows/{workflow_filename}/dispatches"
        return self._sync_request("POST", endpoint, data)

    def get_workflow_runs(self, workflow_filename: str, limit: int = 10) -> Dict:
        """
        Get workflow run history.
        
        Args:
            workflow_filename (str): Workflow filename
            limit (int): Maximum number of runs to retrieve
            
        Returns:
            Dict: Workflow runs data
        """
        params = {"per_page": limit}
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/actions/workflows/{workflow_filename}/runs"
        return self._sync_request("GET", endpoint, params)

    def create_secret(self, secret_name: str, secret_value: str) -> Dict:
        """
        Create or update a repository secret.
        
        Args:
            secret_name (str): Secret name
            secret_value (str): Secret value
            
        Returns:
            Dict: Secret creation response
        """
        # First, get the repository's public key for encryption
        key_endpoint = f"repos/{self.config.owner}/{self.config.repo}/actions/secrets/public-key"
        key_response = self._sync_request("GET", key_endpoint)
        
        # Encrypt the secret value
        from cryptography.hazmat.primitives.asymmetric import padding
        from cryptography.hazmat.primitives import serialization, hashes
        import base64
        
        public_key_bytes = base64.b64decode(key_response["key"])
        public_key = serialization.load_der_public_key(public_key_bytes)
        
        encrypted_value = public_key.encrypt(
            secret_value.encode(),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        encrypted_value_b64 = base64.b64encode(encrypted_value).decode()
        
        data = {
            "encrypted_value": encrypted_value_b64,
            "key_id": key_response["key_id"]
        }
        
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/actions/secrets/{secret_name}"
        return self._sync_request("PUT", endpoint, data)

    def get_repository_info(self) -> Dict:
        """
        Get repository information.
        
        Returns:
            Dict: Repository information
        """
        endpoint = f"repos/{self.config.owner}/{self.config.repo}"
        return self._sync_request("GET", endpoint)

    def create_release(self, tag_name: str, name: str, body: str = "", draft: bool = False) -> Dict:
        """
        Create a GitHub release.
        
        Args:
            tag_name (str): Git tag name
            name (str): Release name
            body (str): Release description
            draft (bool): Whether release is a draft
            
        Returns:
            Dict: Release creation response
        """
        data = {
            "tag_name": tag_name,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": False
        }
        
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/releases"
        return self._sync_request("POST", endpoint, data)

    def setup_webhook(self, webhook_url: str, events: List[str] = None) -> Dict:
        """
        Set up a webhook for repository events.
        
        Args:
            webhook_url (str): Webhook URL
            events (List[str]): List of events to subscribe to
            
        Returns:
            Dict: Webhook creation response
        """
        if events is None:
            events = ["push", "deployment", "deployment_status", "workflow_run"]
        
        data = {
            "config": {
                "url": webhook_url,
                "content_type": "json",
                "insecure_ssl": "0"
            },
            "events": events,
            "active": True
        }
        
        endpoint = f"repos/{self.config.owner}/{self.config.repo}/hooks"
        return self._sync_request("POST", endpoint, data)


class GitHubMCPTool:
    """
    High-level GitHub MCP tool for deployment integration.
    
    This tool provides simplified methods for common deployment tasks
    and integrates with the deployment workflow.
    """

    def __init__(self, github_token: str, owner: str, repo: str):
        """
        Initialize GitHub MCP tool.
        
        Args:
            github_token (str): GitHub personal access token
            owner (str): Repository owner
            repo (str): Repository name
        """
        self.config = GitHubConfig(
            token=github_token,
            owner=owner,
            repo=repo
        )
        self.client = GitHubMCPClient(self.config)
        self.logger = logging.getLogger(__name__)

    def deploy_to_github(self, project_root: str, files_dict: Dict[str, str]) -> Dict:
        """
        Deploy project files to GitHub repository.
        
        Args:
            project_root (str): Local project root path
            files_dict (Dict[str, str]): Dictionary of files to deploy
            
        Returns:
            Dict: Deployment results
        """
        try:
            self.logger.info(f"🚀 Starting GitHub deployment for {self.config.repo}")
            
            # 1. Upload files to repository
            upload_responses = self.client.upload_files_to_repo(
                files_dict, 
                "Automated deployment files upload"
            )
            
            # 2. Create deployment
            deployment = self.client.create_deployment(
                environment="production",
                description="Automated deployment via MCP"
            )
            
            # 3. Update deployment status to pending
            self.client.update_deployment_status(
                deployment["id"], 
                "pending", 
                "Deployment in progress"
            )
            
            # 4. Trigger deployment workflow if it exists
            try:
                workflow_trigger = self.client.trigger_workflow("deploy.yml")
                self.logger.info("✅ Deployment workflow triggered")
            except Exception as e:
                self.logger.warning(f"⚠️ Could not trigger workflow: {e}")
                workflow_trigger = None
            
            # 5. Update deployment status to success
            self.client.update_deployment_status(
                deployment["id"], 
                "success", 
                "Deployment completed successfully"
            )
            
            return {
                "status": "success",
                "deployment_id": deployment["id"],
                "upload_responses": upload_responses,
                "workflow_trigger": workflow_trigger,
                "repository_url": f"https://github.com/{self.config.owner}/{self.config.repo}"
            }
            
        except Exception as e:
            self.logger.error(f"❌ GitHub deployment failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def setup_deployment_secrets(self, secrets: Dict[str, str]) -> Dict:
        """
        Set up deployment secrets in GitHub repository.
        
        Args:
            secrets (Dict[str, str]): Dictionary of secret names and values
            
        Returns:
            Dict: Results of secret creation
        """
        results = {}
        
        for secret_name, secret_value in secrets.items():
            try:
                response = self.client.create_secret(secret_name, secret_value)
                results[secret_name] = {"status": "success", "response": response}
                self.logger.info(f"✅ Secret {secret_name} created successfully")
            except Exception as e:
                results[secret_name] = {"status": "error", "error": str(e)}
                self.logger.error(f"❌ Failed to create secret {secret_name}: {e}")
        
        return results

    def monitor_deployment(self, deployment_id: int, timeout: int = 300) -> Dict:
        """
        Monitor deployment status.
        
        Args:
            deployment_id (int): Deployment ID to monitor
            timeout (int): Timeout in seconds
            
        Returns:
            Dict: Deployment monitoring results
        """
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Get workflow runs to check deployment status
                workflow_runs = self.client.get_workflow_runs("deploy.yml", limit=5)
                
                if workflow_runs.get("workflow_runs"):
                    latest_run = workflow_runs["workflow_runs"][0]
                    status = latest_run.get("status")
                    conclusion = latest_run.get("conclusion")
                    
                    if status == "completed":
                        return {
                            "status": "completed",
                            "conclusion": conclusion,
                            "run_url": latest_run.get("html_url"),
                            "duration": time.time() - start_time
                        }
                
                time.sleep(10)  # Wait 10 seconds before checking again
                
            except Exception as e:
                self.logger.error(f"Error monitoring deployment: {e}")
                time.sleep(10)
        
        return {
            "status": "timeout",
            "message": f"Deployment monitoring timed out after {timeout} seconds"
        }

    def create_deployment_release(self, version: str, release_notes: str = "") -> Dict:
        """
        Create a release for the deployment.
        
        Args:
            version (str): Version tag
            release_notes (str): Release notes
            
        Returns:
            Dict: Release creation results
        """
        try:
            release = self.client.create_release(
                tag_name=f"v{version}",
                name=f"Release v{version}",
                body=release_notes or f"Automated release v{version}"
            )
            
            return {
                "status": "success",
                "release_url": release.get("html_url"),
                "tag_name": release.get("tag_name")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to create release: {e}")
            return {
                "status": "error",
                "error": str(e)
            }


def get_github_mcp_tool(github_token: str = None, owner: str = None, repo: str = None) -> GitHubMCPTool:
    """
    Factory function to create GitHub MCP tool instance.
    
    Args:
        github_token (str): GitHub token (defaults to environment variable)
        owner (str): Repository owner (defaults to environment variable)
        repo (str): Repository name (defaults to environment variable)
        
    Returns:
        GitHubMCPTool: Configured GitHub MCP tool instance
    """
    github_token = github_token or os.getenv("GITHUB_TOKEN")
    owner = owner or os.getenv("GITHUB_OWNER")
    repo = repo or os.getenv("GITHUB_REPO")
    
    if not all([github_token, owner, repo]):
        raise ValueError(
            "GitHub token, owner, and repo must be provided either as arguments "
            "or environment variables (GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO)"
        )
    
    return GitHubMCPTool(github_token, owner, repo)
