"""
Test suite for GitHub MCP Integration

This module contains tests for the GitHub MCP integration functionality.
"""

import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import tempfile
import json

# Add the project root to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.project.tools.github_mcp import GitHubMCPTool, GitHubMCPClient, GitHubConfig
    from src.project.tools.deployment_orchestrator import DeploymentOrchestrator
    from src.project.tools.mcp_config import create_mcp_config
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: GitHub MCP not available for testing: {e}")
    MCP_AVAILABLE = False


class TestGitHubMCPConfig(unittest.TestCase):
    """Test GitHub MCP configuration functionality."""
    
    def test_github_config_creation(self):
        """Test GitHubConfig creation."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        config = GitHubConfig(
            token="test_token",
            owner="test_owner", 
            repo="test_repo"
        )
        
        self.assertEqual(config.token, "test_token")
        self.assertEqual(config.owner, "test_owner")
        self.assertEqual(config.repo, "test_repo")
        self.assertEqual(config.base_url, "https://api.github.com")

    def test_mcp_config_creation(self):
        """Test MCP configuration creation."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_OWNER': 'test_owner',
            'GITHUB_REPO': 'test_repo'
        }):
            config = create_mcp_config()
            
            self.assertEqual(config.github['token'], 'test_token')
            self.assertEqual(config.github['owner'], 'test_owner') 
            self.assertEqual(config.github['repo'], 'test_repo')


class TestGitHubMCPClient(unittest.TestCase):
    """Test GitHub MCP client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if MCP_AVAILABLE:
            self.config = GitHubConfig(
                token="test_token",
                owner="test_owner",
                repo="test_repo"
            )
            self.client = GitHubMCPClient(self.config)
    
    @patch('requests.get')
    def test_sync_request_get(self, mock_get):
        """Test synchronous GET request."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        mock_response = Mock()
        mock_response.json.return_value = {"test": "data"}
        mock_response.content = b'{"test": "data"}'
        mock_get.return_value = mock_response
        
        result = self.client._sync_request("GET", "test/endpoint")
        
        self.assertEqual(result, {"test": "data"})
        mock_get.assert_called_once()

    @patch('requests.post')
    def test_sync_request_post(self, mock_post):
        """Test synchronous POST request."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        mock_response = Mock()
        mock_response.json.return_value = {"created": True}
        mock_response.content = b'{"created": True}'
        mock_post.return_value = mock_response
        
        test_data = {"name": "test_repo"}
        result = self.client._sync_request("POST", "user/repos", test_data)
        
        self.assertEqual(result, {"created": True})
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_create_repository(self, mock_post):
        """Test repository creation."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        mock_response = Mock()
        mock_response.json.return_value = {
            "name": "test_repo",
            "full_name": "test_owner/test_repo",
            "html_url": "https://github.com/test_owner/test_repo"
        }
        mock_response.content = b'{"name": "test_repo"}'
        mock_post.return_value = mock_response
        
        result = self.client.create_repository("test_repo", "Test repository")
        
        self.assertEqual(result["name"], "test_repo")
        mock_post.assert_called_once()


class TestGitHubMCPTool(unittest.TestCase):
    """Test GitHub MCP tool functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if MCP_AVAILABLE:
            with patch.dict(os.environ, {
                'GITHUB_TOKEN': 'test_token',
                'GITHUB_OWNER': 'test_owner',
                'GITHUB_REPO': 'test_repo'
            }):
                self.tool = GitHubMCPTool("test_token", "test_owner", "test_repo")

    @patch('src.project.tools.github_mcp.GitHubMCPClient.upload_files_to_repo')
    @patch('src.project.tools.github_mcp.GitHubMCPClient.create_deployment')
    @patch('src.project.tools.github_mcp.GitHubMCPClient.update_deployment_status')
    def test_deploy_to_github(self, mock_update_status, mock_create_deployment, mock_upload_files):
        """Test GitHub deployment functionality."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        # Mock responses
        mock_upload_files.return_value = [{"status": "success"}]
        mock_create_deployment.return_value = {"id": 123, "status": "pending"}
        mock_update_status.return_value = {"status": "success"}
        
        files_dict = {
            "Dockerfile": "FROM python:3.9",
            "docker-compose.yml": "version: '3.8'"
        }
        
        result = self.tool.deploy_to_github("/test/project", files_dict)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["deployment_id"], 123)
        mock_upload_files.assert_called_once()
        mock_create_deployment.assert_called_once()

    @patch('src.project.tools.github_mcp.GitHubMCPClient.create_secret')
    def test_setup_deployment_secrets(self, mock_create_secret):
        """Test deployment secrets setup."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        mock_create_secret.return_value = {"status": "success"}
        
        secrets = {
            "DATABASE_URL": "postgresql://localhost:5432/test",
            "SECRET_KEY": "test_secret"
        }
        
        result = self.tool.setup_deployment_secrets(secrets)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(mock_create_secret.call_count, 2)


class TestDeploymentOrchestrator(unittest.TestCase):
    """Test deployment orchestrator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        if MCP_AVAILABLE:
            with patch.dict(os.environ, {
                'GITHUB_TOKEN': 'test_token',
                'GITHUB_OWNER': 'test_owner',
                'GITHUB_REPO': 'test_repo'
            }):
                self.orchestrator = DeploymentOrchestrator("test_token", "test_owner", "test_repo")

    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        self.assertIsNotNone(self.orchestrator)
        self.assertTrue(self.orchestrator.mcp_enabled)

    @patch('src.project.tools.deployment_orchestrator.DeploymentOrchestrator._deploy_to_github')
    @patch('src.project.tools.deployment_orchestrator.DeploymentOrchestrator._prepare_local_deployment')
    def test_orchestrate_deployment(self, mock_prepare_local, mock_deploy_github):
        """Test deployment orchestration."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        # Mock responses
        mock_prepare_local.return_value = {"status": "success", "files_generated": 3}
        mock_deploy_github.return_value = {"status": "success", "deployment_id": 123}
        
        state = {
            "project_folder": "/test/project",
            "project_name": "test_project",
            "generated_deployment_files": {
                "Dockerfile": "FROM python:3.9",
                "docker-compose.yml": "version: '3.8'",
                "requirements.txt": "flask==2.0.1"
            }
        }
        
        result_state = self.orchestrator.orchestrate_deployment(state, enable_github_deploy=True)
        
        self.assertEqual(result_state["deployment_status"], "success")
        self.assertIn("deployment_results", result_state)
        mock_prepare_local.assert_called_once()
        mock_deploy_github.assert_called_once()

    def test_deployment_tracking(self):
        """Test deployment tracking functionality."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        # Test initial state
        status = self.orchestrator.get_deployment_status()
        self.assertEqual(len(status["active_deployments"]), 0)
        
        # Test deployment history
        history = self.orchestrator.get_deployment_history()
        self.assertEqual(len(history), 0)


class TestIntegrationWithDeploymentNode(unittest.TestCase):
    """Test integration with existing deployment node."""
    
    @patch.dict(os.environ, {
        'GITHUB_TOKEN': 'test_token',
        'GITHUB_OWNER': 'test_owner',
        'GITHUB_REPO': 'test_repo',
        'ENABLE_GITHUB_DEPLOY': 'true'
    })
    def test_deployment_node_integration(self):
        """Test integration with DeployApplication node."""
        if not MCP_AVAILABLE:
            self.skipTest("GitHub MCP not available")
        
        # This test would require the actual DeployApplication class
        # and proper mocking of the LLM model
        pass


class TestEnvironmentConfiguration(unittest.TestCase):
    """Test environment configuration and validation."""
    
    def test_required_environment_variables(self):
        """Test validation of required environment variables."""
        required_vars = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
        
        # Test with missing variables
        with patch.dict(os.environ, {}, clear=True):
            if MCP_AVAILABLE:
                with self.assertRaises(ValueError):
                    from src.project.tools.github_mcp import get_github_mcp_tool
                    get_github_mcp_tool()
        
        # Test with all variables present
        with patch.dict(os.environ, {
            'GITHUB_TOKEN': 'test_token',
            'GITHUB_OWNER': 'test_owner',
            'GITHUB_REPO': 'test_repo'
        }):
            if MCP_AVAILABLE:
                from src.project.tools.github_mcp import get_github_mcp_tool
                tool = get_github_mcp_tool()
                self.assertIsNotNone(tool)


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
