#!/usr/bin/env python3
"""
GitHub MCP Setup Script

This script helps you set up GitHub MCP integration for automated deployment.
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create a .env file with required GitHub configurations."""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ .env file already exists")
        response = input("Do you want to update it? (y/N): ")
        if response.lower() != 'y':
            return
    
    print("\n🔧 Setting up GitHub MCP configuration...")
    print("Please provide the following information:")
    
    github_token = input("GitHub Personal Access Token: ").strip()
    github_owner = input("GitHub Username/Organization: ").strip()
    github_repo = input("Repository Name: ").strip()
    
    env_content = f"""# GitHub MCP Configuration
GITHUB_TOKEN={github_token}
GITHUB_OWNER={github_owner}
GITHUB_REPO={github_repo}

# Enable GitHub features
ENABLE_GITHUB_PUSH=true
ENABLE_GITHUB_DEPLOY=true
CREATE_GITHUB_RELEASE=false

# Optional: Docker Hub configuration
DOCKER_HUB_USERNAME=
DOCKER_HUB_TOKEN=

# Optional: Application secrets
DATABASE_URL=
SECRET_KEY=
API_KEY=
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"✅ Created .env file at {env_path.absolute()}")
    print("\n⚠️ Important:")
    print("1. Never commit your .env file to version control")
    print("2. Add .env to your .gitignore file")
    print("3. Update the optional values as needed")

def create_gitignore():
    """Create or update .gitignore file."""
    gitignore_path = Path(".gitignore")
    
    gitignore_entries = [
        "# Environment variables",
        ".env",
        ".env.local",
        ".env.*.local",
        "",
        "# Python cache",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "",
        "# Virtual environments",
        "venv/",
        "env/",
        ".venv/",
        "",
        "# IDE files",
        ".vscode/",
        ".idea/",
        "*.swp",
        "*.swo",
        "",
        "# Logs",
        "*.log",
        "logs/",
        "",
        "# Generated projects (optional)",
        "generated_projects/*/",
        "!generated_projects/.gitkeep"
    ]
    
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            existing_content = f.read()
        
        if ".env" in existing_content:
            print("✅ .gitignore already contains .env")
            return
    
    with open(gitignore_path, 'a') as f:
        f.write("\n".join(gitignore_entries) + "\n")
    
    print(f"✅ Updated .gitignore file")

def test_github_connection():
    """Test GitHub API connection."""
    print("\n🔗 Testing GitHub connection...")
    
    try:
        # Import and test GitHub MCP
        sys.path.append('.')
        from src.project.tools.github_mcp import get_github_mcp_tool
        
        github_tool = get_github_mcp_tool()
        repo_info = github_tool.client.get_repository_info()
        
        print(f"✅ Successfully connected to: {repo_info['full_name']}")
        print(f"   Description: {repo_info.get('description', 'No description')}")
        print(f"   Private: {repo_info['private']}")
        print(f"   Default branch: {repo_info['default_branch']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to connect to GitHub: {e}")
        print("\nPlease check:")
        print("1. Your GitHub token is valid and has correct permissions")
        print("2. The repository owner and name are correct")
        print("3. You have access to the repository")
        return False

def install_dependencies():
    """Install required dependencies."""
    print("\n📦 Installing GitHub MCP dependencies...")
    
    dependencies = [
        "aiohttp>=3.8.0",
        "PyGithub>=2.0.0",
        "cryptography>=40.0.0",
        "requests>=2.28.0"
    ]
    
    try:
        import subprocess
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
        
        print("✅ All dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 GitHub MCP Integration Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("src/project/nodes/deployment.py").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Create/update .gitignore
    create_gitignore()
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv not installed, skipping .env loading")
    
    # Test connection
    if test_github_connection():
        print("\n✅ GitHub MCP setup completed successfully!")
        print("\nNext steps:")
        print("1. Review your .env file and update any optional values")
        print("2. Test the integration by running your deployment script")
        print("3. Check the generated_projects folder for your deployments")
    else:
        print("\n⚠️ Setup completed but GitHub connection failed")
        print("Please check your configuration and try again")

if __name__ == "__main__":
    main()
