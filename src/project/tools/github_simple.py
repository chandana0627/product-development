"""
Simple GitHub API helper for deployment
"""

import os
import requests
import base64
from typing import Dict, Optional


class SimpleGitHubAPI:
    """Simple GitHub API wrapper for deployment needs."""
    
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
    
    def upload_file(self, file_path: str, content: str, message: str = None) -> Dict:
        """Upload a single file to GitHub repository."""
        try:
            # Encode content
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # GitHub API URL
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{file_path}"
            
            # Check if file exists
            existing_response = requests.get(url, headers=self.headers)
            
            if existing_response.status_code == 200:
                # File exists, update it
                existing_data = existing_response.json()
                sha = existing_data["sha"]
                data = {
                    "message": message or f"Update {file_path}",
                    "content": encoded_content,
                    "sha": sha
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
    
    def upload_files(self, files: Dict[str, str], base_message: str = "Deploy files") -> Dict:
        """Upload multiple files."""
        results = {}
        successful = 0
        
        for file_path, content in files.items():
            message = f"{base_message}: {file_path}"
            result = self.upload_file(file_path, content, message)
            results[file_path] = result
            
            if result.get("status") == "success":
                successful += 1
        
        return {
            "total_files": len(files),
            "successful": successful,
            "results": results
        }
    
    def create_release(self, tag: str, name: str, body: str = "") -> Dict:
        """Create a GitHub release."""
        try:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases"
            
            data = {
                "tag_name": tag,
                "name": name,
                "body": body,
                "draft": False,
                "prerelease": False
            }
            
            response = requests.post(url, json=data, headers=self.headers)
            
            if response.status_code == 201:
                response_data = response.json()
                return {
                    "status": "success",
                    "url": response_data['html_url'],
                    "tag": response_data['tag_name']
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
    
    def get_repo_info(self) -> Dict:
        """Get basic repository information."""
        try:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "success",
                    "name": data['full_name'],
                    "default_branch": data['default_branch'],
                    "private": data['private'],
                    "url": data['html_url']
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


def get_github_api() -> Optional[SimpleGitHubAPI]:
    """Get GitHub API instance if credentials are available."""
    try:
        return SimpleGitHubAPI()
    except ValueError:
        return None
