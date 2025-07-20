"""
Simple GitHub Helper for Deployment

A lightweight GitHub integration without complex MCP overhead.
Just the essential functions needed for deployment file uploads.
"""

import os
import requests
import base64
from typing import Dict, Optional


class SimpleGitHubHelper:
    """Simple GitHub helper for deployment tasks."""
    
    def __init__(self, token: str = None, owner: str = None, repo: str = None):
        """Initialize with GitHub credentials."""
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.owner = owner or os.getenv("GITHUB_OWNER") 
        self.repo = repo or os.getenv("GITHUB_REPO")
        
        if not all([self.token, self.owner, self.repo]):
            raise ValueError("GitHub token, owner, and repo are required")
        
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"
    
    def test_connection(self) -> Dict:
        """Test GitHub connection and get repo info."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return {
                "status": "success",
                "repo_info": response.json()
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e)
            }
    
    def upload_file(self, file_path: str, content: str, message: str = None) -> Dict:
        """Upload a single file to GitHub."""
        try:
            # Encode content
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # Check if file exists
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/contents/{file_path}"
            existing_response = requests.get(url, headers=self.headers)
            
            if existing_response.status_code == 200:
                # File exists, update it
                existing_data = existing_response.json()
                data = {
                    "message": message or f"Update {file_path}",
                    "content": encoded_content,
                    "sha": existing_data["sha"]
                }
            else:
                # File doesn't exist, create it
                data = {
                    "message": message or f"Add {file_path}",
                    "content": encoded_content
                }
            
            # Upload file
            response = requests.put(url, json=data, headers=self.headers)
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                return {
                    "status": "success",
                    "url": response_data['content']['html_url'],
                    "sha": response_data['commit']['sha']
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def upload_multiple_files(self, files_dict: Dict[str, str], base_message: str = "Deploy files") -> Dict:
        """Upload multiple files to GitHub."""
        results = {}
        successful = 0
        
        for file_path, content in files_dict.items():
            result = self.upload_file(file_path, content, f"{base_message}: {file_path}")
            results[file_path] = result
            if result["status"] == "success":
                successful += 1
        
        return {
            "status": "success" if successful > 0 else "error",
            "uploaded": successful,
            "total": len(files_dict),
            "results": results
        }
    
    def create_release(self, version: str, title: str = None, notes: str = "") -> Dict:
        """Create a GitHub release."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/releases"
            data = {
                "tag_name": f"v{version}",
                "name": title or f"Release v{version}",
                "body": notes,
                "draft": False,
                "prerelease": False
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "status": "success",
                    "release_url": response_data['html_url'],
                    "tag_name": response_data['tag_name']
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def trigger_workflow(self, workflow_name: str = "deploy.yml") -> Dict:
        """Trigger a GitHub Actions workflow."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_name}/dispatches"
            data = {
                "ref": "main"
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 204:
                return {
                    "status": "success",
                    "message": f"Workflow {workflow_name} triggered successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_workflow_runs(self, workflow_name: str = "deploy.yml", limit: int = 5) -> Dict:
        """Get recent workflow runs."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/actions/workflows/{workflow_name}/runs"
            params = {"per_page": limit}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "workflow_runs": response.json()["workflow_runs"]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_issue(self, title: str, body: str = "", labels: list = None, assignees: list = None) -> Dict:
        """Create a GitHub issue."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
            data = {
                "title": title,
                "body": body
            }
            
            if labels:
                data["labels"] = labels
            if assignees:
                data["assignees"] = assignees
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "status": "success",
                    "issue_number": response_data["number"],
                    "issue_url": response_data["html_url"]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_pull_request(self, title: str, head: str, base: str = "main", body: str = "", draft: bool = False) -> Dict:
        """Create a GitHub pull request."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/pulls"
            data = {
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "status": "success",
                    "pr_number": response_data["number"],
                    "pr_url": response_data["html_url"]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_branch(self, branch_name: str, from_branch: str = "main") -> Dict:
        """Create a new branch."""
        try:
            # Get the SHA of the source branch
            ref_url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/ref/heads/{from_branch}"
            ref_response = requests.get(ref_url, headers=self.headers)
            
            if ref_response.status_code != 200:
                return {
                    "status": "error",
                    "error": f"Could not get {from_branch} branch SHA"
                }
            
            sha = ref_response.json()["object"]["sha"]
            
            # Create new branch
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/git/refs"
            data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": sha
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                return {
                    "status": "success",
                    "branch_name": branch_name,
                    "sha": sha
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def add_comment_to_issue(self, issue_number: int, comment: str) -> Dict:
        """Add a comment to an issue."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments"
            data = {"body": comment}
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "status": "success",
                    "comment_id": response_data["id"],
                    "comment_url": response_data["html_url"]
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def close_issue(self, issue_number: int, comment: str = None) -> Dict:
        """Close an issue with optional comment."""
        try:
            # Add comment first if provided
            if comment:
                self.add_comment_to_issue(issue_number, comment)
            
            # Close the issue
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues/{issue_number}"
            data = {"state": "closed"}
            
            response = requests.patch(url, json=data, headers=self.headers)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": f"Issue #{issue_number} closed successfully"
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_repository_issues(self, state: str = "open", labels: str = None, limit: int = 30) -> Dict:
        """Get repository issues."""
        try:
            url = f"{self.base_url}/repos/{self.owner}/{self.repo}/issues"
            params = {
                "state": state,
                "per_page": limit
            }
            
            if labels:
                params["labels"] = labels
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "issues": response.json()
                }
            else:
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


def get_github_helper(token: str = None, owner: str = None, repo: str = None) -> Optional[SimpleGitHubHelper]:
    """Get a GitHub helper instance if credentials are available."""
    try:
        return SimpleGitHubHelper(token, owner, repo)
    except ValueError:
        return None


def check_github_environment() -> Dict:
    """Check if GitHub environment is properly configured."""
    required_vars = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        return {
            "available": False,
            "missing_vars": missing_vars
        }
    
    # Test connection
    helper = get_github_helper()
    if helper:
        result = helper.test_connection()
        return {
            "available": result["status"] == "success",
            "connection_test": result
        }
    
    return {"available": False, "error": "Could not create helper"}
