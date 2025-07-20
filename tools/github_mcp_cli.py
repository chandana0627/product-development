#!/usr/bin/env python3
"""
GitHub MCP CLI Tool

A command-line interface for testing and interacting with GitHub MCP integration.
"""

import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.project.tools.github_mcp import get_github_mcp_tool
    from src.project.tools.deployment_orchestrator import create_deployment_orchestrator
    from src.project.tools.mcp_config import create_mcp_config
    from src.project.nodes.deployment import DeployApplication
    from src.project.LLMS.model import GroqLLM
    MCP_AVAILABLE = True
except ImportError as e:
    print(f"❌ GitHub MCP not available: {e}")
    MCP_AVAILABLE = False


class GitHubMCPCLI:
    """Command-line interface for GitHub MCP operations."""
    
    def __init__(self):
        """Initialize CLI."""
        self.github_tool = None
        self.orchestrator = None
        
        if MCP_AVAILABLE:
            try:
                self.github_tool = get_github_mcp_tool()
                self.orchestrator = create_deployment_orchestrator()
                print("✅ GitHub MCP initialized successfully")
            except Exception as e:
                print(f"⚠️ GitHub MCP initialization failed: {e}")
                print("Make sure environment variables are set correctly.")

    def check_environment(self):
        """Check if environment is properly configured."""
        print("\n🔍 Checking GitHub MCP Environment...")
        
        required_vars = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
        missing_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: {'*' * len(value)}")
            else:
                print(f"❌ {var}: Not set")
                missing_vars.append(var)
        
        if missing_vars:
            print(f"\n❌ Missing required variables: {missing_vars}")
            print("Please set these environment variables and try again.")
            return False
        else:
            print("\n✅ All required environment variables are set")
            return True

    def test_connection(self):
        """Test GitHub API connection."""
        if not self.github_tool:
            print("❌ GitHub MCP tool not available")
            return False
        
        print("\n🔗 Testing GitHub API connection...")
        
        try:
            repo_info = self.github_tool.client.get_repository_info()
            print(f"✅ Connected to repository: {repo_info['full_name']}")
            print(f"   Description: {repo_info.get('description', 'No description')}")
            print(f"   Private: {repo_info['private']}")
            print(f"   Default branch: {repo_info['default_branch']}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to GitHub: {e}")
            return False

    def create_test_deployment(self):
        """Create a test deployment."""
        if not self.github_tool:
            print("❌ GitHub MCP tool not available")
            return
        
        print("\n🚀 Creating test deployment...")
        
        # Sample deployment files
        test_files = {
            "Dockerfile": """FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8000
CMD ["python", "app.py"]""",
            
            "docker-compose.yml": """version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENV=production""",
            
            "requirements.txt": """flask==2.3.2
gunicorn==21.2.0""",
            
            "README.md": f"""# Test Deployment

This is a test deployment created by GitHub MCP CLI tool.

Created: {datetime.now().isoformat()}
"""
        }
        
        try:
            result = self.github_tool.deploy_to_github("/tmp/test_project", test_files)
            
            if result["status"] == "success":
                print(f"✅ Test deployment created successfully")
                print(f"   Deployment ID: {result['deployment_id']}")
                print(f"   Repository URL: {result['repository_url']}")
                return result["deployment_id"]
            else:
                print(f"❌ Test deployment failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Test deployment failed: {e}")
            return None

    def monitor_deployment(self, deployment_id):
        """Monitor a deployment."""
        if not self.github_tool:
            print("❌ GitHub MCP tool not available")
            return
        
        print(f"\n👀 Monitoring deployment {deployment_id}...")
        
        try:
            result = self.github_tool.monitor_deployment(deployment_id, timeout=60)
            
            print(f"Status: {result['status']}")
            if result.get('conclusion'):
                print(f"Conclusion: {result['conclusion']}")
            if result.get('run_url'):
                print(f"Workflow URL: {result['run_url']}")
            if result.get('duration'):
                print(f"Duration: {result['duration']:.2f} seconds")
                
        except Exception as e:
            print(f"❌ Failed to monitor deployment: {e}")

    def setup_secrets(self):
        """Setup test deployment secrets."""
        if not self.github_tool:
            print("❌ GitHub MCP tool not available")
            return
        
        print("\n🔐 Setting up test deployment secrets...")
        
        test_secrets = {
            "TEST_SECRET": "test_value_123",
            "DATABASE_URL": "postgresql://localhost:5432/testdb",
            "SECRET_KEY": "test-secret-key-for-demo"
        }
        
        try:
            result = self.github_tool.setup_deployment_secrets(test_secrets)
            
            for secret_name, secret_result in result.items():
                if secret_result["status"] == "success":
                    print(f"✅ Secret {secret_name} created successfully")
                else:
                    print(f"❌ Failed to create secret {secret_name}: {secret_result['error']}")
                    
        except Exception as e:
            print(f"❌ Failed to setup secrets: {e}")

    def create_release(self):
        """Create a test release."""
        if not self.github_tool:
            print("❌ GitHub MCP tool not available")
            return
        
        print("\n🏷️ Creating test release...")
        
        version = f"test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        release_notes = f"""
# Test Release {version}

This is a test release created by the GitHub MCP CLI tool.

## Features
- Automated deployment configuration
- Docker containerization
- GitHub Actions integration

Created: {datetime.now().isoformat()}
        """.strip()
        
        try:
            result = self.github_tool.create_deployment_release(version, release_notes)
            
            if result["status"] == "success":
                print(f"✅ Release created successfully")
                print(f"   Tag: {result['tag_name']}")
                print(f"   URL: {result['release_url']}")
            else:
                print(f"❌ Failed to create release: {result['error']}")
                
        except Exception as e:
            print(f"❌ Failed to create release: {e}")

    def show_status(self):
        """Show deployment status and history."""
        if not self.orchestrator:
            print("❌ Deployment orchestrator not available")
            return
        
        print("\n📊 Deployment Status and History...")
        
        # Show current status
        status = self.orchestrator.get_deployment_status()
        print(f"Active deployments: {len(status['active_deployments'])}")
        print(f"Total deployments: {status['total_deployments']}")
        print(f"MCP enabled: {status['mcp_enabled']}")
        
        # Show recent history
        history = self.orchestrator.get_deployment_history(5)
        if history:
            print("\n📈 Recent Deployment History:")
            for i, deployment in enumerate(history, 1):
                print(f"  {i}. {deployment['project_name']} - {deployment['status']} ({deployment['timestamp']})")
        else:
            print("\n📈 No deployment history available")

    def run_full_test(self):
        """Run a complete test of the GitHub MCP integration."""
        print("\n🧪 Running Full GitHub MCP Test Suite...")
        
        # 1. Check environment
        if not self.check_environment():
            return False
        
        # 2. Test connection
        if not self.test_connection():
            return False
        
        # 3. Create test deployment
        deployment_id = self.create_test_deployment()
        if not deployment_id:
            return False
        
        # 4. Setup secrets
        self.setup_secrets()
        
        # 5. Monitor deployment
        self.monitor_deployment(deployment_id)
        
        # 6. Create release
        self.create_release()
        
        # 7. Show status
        self.show_status()
        
        print("\n✅ Full test suite completed successfully!")
        return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub MCP CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_mcp_cli.py check-env
  python github_mcp_cli.py test-connection
  python github_mcp_cli.py create-deployment
  python github_mcp_cli.py full-test
        """
    )
    
    parser.add_argument(
        "command",
        choices=[
            "check-env", "test-connection", "create-deployment", 
            "setup-secrets", "create-release", "status", "full-test"
        ],
        help="Command to execute"
    )
    
    parser.add_argument(
        "--deployment-id",
        type=int,
        help="Deployment ID for monitoring"
    )
    
    args = parser.parse_args()
    
    if not MCP_AVAILABLE:
        print("❌ GitHub MCP integration is not available.")
        print("Please install required dependencies and check your configuration.")
        sys.exit(1)
    
    cli = GitHubMCPCLI()
    
    if args.command == "check-env":
        cli.check_environment()
    elif args.command == "test-connection":
        cli.test_connection()
    elif args.command == "create-deployment":
        deployment_id = cli.create_test_deployment()
        if deployment_id and args.deployment_id is None:
            cli.monitor_deployment(deployment_id)
    elif args.command == "setup-secrets":
        cli.setup_secrets()
    elif args.command == "create-release":
        cli.create_release()
    elif args.command == "status":
        cli.show_status()
    elif args.command == "full-test":
        cli.run_full_test()
    
    if args.deployment_id:
        cli.monitor_deployment(args.deployment_id)


if __name__ == "__main__":
    main()
