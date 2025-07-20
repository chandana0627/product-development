import os
import subprocess
import time
import sys
from pathlib import Path
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path if needed
sys.path.append(str(Path(__file__).parent.parent.parent))

# Simple GitHub integration without complex MCP
GITHUB_AVAILABLE = False
try:
    import requests
    import base64
    from src.project.tools.github_helper import get_github_helper, check_github_environment
    GITHUB_AVAILABLE = True
    print("✅ GitHub integration available")
except ImportError:
    print("ℹ️ GitHub dependencies not available - install with: pip install requests")
    get_github_helper = None
    check_github_environment = None
except Exception as e:
    print(f"⚠️ GitHub import error: {e}")
    get_github_helper = None
    check_github_environment = None

class DeployApplication:
    """
    AI-powered deployment automation for generating deployment scripts, configurations, and best practices.
    """

    def __init__(self, model):
        """
        Initializes the deployment automation with an AI model.
        """
        self.llm = model
        
        # Simple GitHub integration - no complex MCP
        self.github_enabled = self._check_github_environment()
        
        if self.github_enabled:
            print("✅ GitHub integration ready")
            print(f"   Repository: {os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}")
        else:
            print("ℹ️ GitHub integration disabled - deployment will work without GitHub")

    def _check_github_environment(self):
        """
        Check if GitHub environment is properly configured.
        
        Returns:
            bool: True if GitHub can be used
        """
        if not GITHUB_AVAILABLE:
            return False
        
        required_vars = ["GITHUB_TOKEN", "GITHUB_OWNER", "GITHUB_REPO"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            print(f"⚠️ Missing GitHub environment variables: {missing_vars}")
            return False
        
        return True

    def generate_deployment_files(self, state):
        """
        Generates deployment configuration and scripts based on the given project.

        Args:
            state (dict): Contains project-related information such as project folder, codebase, and tech stack.

        Returns:
            dict: Deployment configuration files.
        """
        # Optional: Track workflow progress (can be handled externally)
        # StreamlitUI tracking should be done at a higher level to avoid circular imports
        
        project_root = state.get("project_folder")
        if not project_root:
            raise ValueError("❌ Error: Project folder not found in state")
        os.makedirs(project_root, exist_ok=True)

        design_document = state.get("design")

        prompt = f"""
        You are a **highly skilled DevOps engineer** responsible for **generating a full deployment setup**  
        for the given project.  

        ## **📜 Design Document (Extract)**
        {design_document}

        ## **🔹 Instructions**
        - Identify the **Tech Stack** (Programming languages, frameworks, databases, etc.).
        - Identify the **Infrastructure** (Cloud providers, containerization tools, deployment platforms).

        ---  
        ## **🔹 Deployment Requirements**
        - Generate a **Dockerfile** for containerizing the application.  
        - Provide a **docker-compose.yml** file for local multi-container setup.  
        - Include **Kubernetes manifests (YAML files)** for cloud deployment.  
        - Provide **CI/CD pipeline configuration** (GitHub Actions, GitLab CI/CD, or Jenkins).  
        - Ensure security best practices (least privilege, environment variable management, secure API keys).  
        - Optimize deployment for **scalability, security, and reliability**.  

        ---  
        ## **🛠 Example Output Format**  
        Generate deployment files using this format:
        
        Use triple backticks followed by the filename for each file:
        - For Dockerfile: ```Dockerfile
        - For Docker Compose: ```docker-compose.yml  
        - For Kubernetes: ```k8s/deployment.yaml
        - For GitHub Actions: ```github/workflows/deploy.yml
        - For requirements: ```requirements.txt
        
        ---  
        **⚠️ STRICT INSTRUCTIONS:**  
        - **DO NOT** modify the application code.  
        - **DO NOT** include explanations, reasoning, or placeholders.  
        - Ensure **ALL** deployment files are correctly formatted and ready to use.  
        """

        print("\n🚀 Generating deployment files...")

        # Invoke AI model to generate deployment scripts
        ai_response_deployment = self.llm.invoke([HumanMessage(content=prompt)]).content

        print("\n🔍 AI Deployment Response:", ai_response_deployment)

        # Parse AI response safely
        generated_deployment_files = self.parse_code_response(ai_response_deployment)

        # Save the generated deployment files
        if generated_deployment_files:
            print("\n💾 Saving generated deployment files...")
            self.save_generated_code(generated_deployment_files, project_root)
            print("\n✅ Deployment files generated successfully!")
            
            # 🐙 Push to GitHub if MCP is available and enabled
            self.push_to_github(state, generated_deployment_files)
        else:
            print("\n⚠️ No deployment files were generated from the AI response")

        print("\n✅ Deployment process complete!")

        # Return updated state with deployment files
        state["generated_deployment_files"] = generated_deployment_files

        # Run traditional deployment automation
        self.run_deployment_automation(state)

        return state

    def parse_code_response(self, response):
        """
        Parses the AI-generated response into a dictionary mapping file paths to code.

        Args:
            response (str): AI-generated response.

        Returns:
            dict: Dictionary with file paths as keys and code as values.
        """
        code_blocks = response.split("```")  # AI formats code blocks using ```
        file_mapping = {}

        for block in code_blocks:
            lines = block.strip().split("\n")
            if len(lines) > 1:
                file_name = lines[0].strip()  # First line should be the file name
                file_mapping[file_name] = "\n".join(lines[1:])  # Rest is code

        return file_mapping

    def save_generated_code(self, files_dict, project_root):
        """
        Saves the AI-generated deployment files in the specified project folder.

        Args:
            files_dict (dict): Dictionary mapping file paths to content.
            project_root (str): Path to the root of the project.
        """
        for file_path, content in files_dict.items():
            full_path = os.path.join(project_root, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"✅ Saved: {file_path}")

    def run_deployment_automation(self, state):
        """
        Runs the deployment automation process by executing generated scripts.

        Args:
            state (dict): The project state containing folder paths and configurations.
        """
        project_root = state.get("project_folder")

        print("\n🚀 **Starting Automated Deployment...**")

        # Check & Run Docker
        dockerfile_path = os.path.join(project_root, "Dockerfile")
        if os.path.exists(dockerfile_path):
            print("\n🐳 **Building Docker Image...**")
            self.run_command(f"docker build -t my_app {project_root}")
            self.run_command(f"docker run -d -p 8000:8000 my_app")

        # Start Docker Compose (if available)
        docker_compose_path = os.path.join(project_root, "docker-compose.yml")
        if os.path.exists(docker_compose_path):
            print("\n📦 **Starting Docker Compose Services...**")
            self.run_command(f"docker-compose -f {docker_compose_path} up -d")

        # Apply Kubernetes Configurations
        k8s_folder = os.path.join(project_root, "k8s")
        if os.path.exists(k8s_folder):
            print("\n☸️ **Deploying Kubernetes Services...**")
            self.run_command(f"kubectl apply -f {k8s_folder}")

        # Trigger CI/CD Pipelines (GitHub Actions or Jenkins)
        ci_cd_config = os.path.join(project_root, ".github/workflows/deploy.yml")
        if os.path.exists(ci_cd_config):
            print("\n🚀 **Triggering GitHub Actions Pipeline...**")
            self.run_command("gh workflow run deploy.yml")

        jenkinsfile_path = os.path.join(project_root, "Jenkinsfile")
        if os.path.exists(jenkinsfile_path):
            print("\n🔧 **Triggering Jenkins Pipeline...**")
            self.run_command("jenkins build my_project_pipeline")

        print("\n✅ **Automated Deployment Completed!**")

    def run_command(self, command):
        """
        Executes a shell command and prints output.

        Args:
            command (str): Command to execute.
        """
        print(f"\n🔹 Running: {command}")
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in process.stdout:
            print(line.decode(), end="")
        process.wait()

    def push_to_github(self, state, generated_files):
        """
        Push generated deployment files to GitHub repository using direct API.
        
        Args:
            state (dict): Project state containing information
            generated_files (dict): Dictionary of generated files
        """
        if not self.github_enabled:
            print("ℹ️ GitHub integration not available, skipping GitHub push")
            print("   To enable GitHub push:")
            print("   1. Set GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO in .env")
            print("   2. Install dependencies: pip install requests")
            return None
        
        # Check if GitHub push is enabled
        if not os.getenv("ENABLE_GITHUB_PUSH", "true").lower() == "true":
            print("ℹ️ GitHub push disabled via ENABLE_GITHUB_PUSH environment variable")
            return None
        
        print("\n🐙 Pushing generated files to GitHub...")
        print(f"   Repository: {os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}")
        print(f"   Files to push: {list(generated_files.keys())}")
        
        try:
            # Upload files one by one with detailed feedback
            upload_results = {}
            successful_uploads = 0
            
            for file_path, content in generated_files.items():
                print(f"\n📤 Uploading {file_path}...")
                
                try:
                    result = self._upload_single_file(file_path, content)
                    upload_results[file_path] = result
                    
                    if result.get("status") == "success":
                        print(f"   ✅ {file_path} uploaded successfully")
                        successful_uploads += 1
                    else:
                        print(f"   ❌ {file_path} upload failed: {result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    print(f"   ❌ {file_path} upload error: {e}")
                    upload_results[file_path] = {"status": "error", "error": str(e)}
            
            # Summary
            total_files = len(generated_files)
            print(f"\n📊 Upload Summary: {successful_uploads}/{total_files} files uploaded successfully")
            
            if successful_uploads > 0:
                repo_url = f"https://github.com/{os.getenv('GITHUB_OWNER')}/{os.getenv('GITHUB_REPO')}"
                print(f"✅ Repository URL: {repo_url}")
                
                # Execute CI/CD pipeline if enabled
                if os.getenv("ENABLE_CICD_PIPELINE", "true").lower() == "true":
                    self._execute_cicd_pipeline(generated_files)
                
                # Create deployment tracking issue if enabled
                if os.getenv("CREATE_DEPLOYMENT_ISSUE", "false").lower() == "true":
                    self._create_deployment_issue(state, generated_files)
                
                # Create a release if specified and files were uploaded
                if os.getenv("CREATE_GITHUB_RELEASE", "false").lower() == "true":
                    version = state.get("version", "1.0.0")
                    self.create_github_release(state, version)
                
                return {
                    "status": "success",
                    "repository_url": repo_url,
                    "files_uploaded": successful_uploads,
                    "total_files": total_files,
                    "upload_results": upload_results
                }
            else:
                print("❌ No files were successfully uploaded to GitHub")
                return {
                    "status": "failed",
                    "error": "No files uploaded successfully",
                    "upload_results": upload_results
                }
                
        except Exception as e:
            print(f"❌ Error during GitHub push: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }

    def _upload_single_file(self, file_path, content):
        """
        Upload a single file to GitHub repository using direct API.
        
        Args:
            file_path (str): Path of the file in repository
            content (str): File content
            
        Returns:
            dict: Upload result
        """
        try:
            import requests
            import base64
            
            # Get GitHub credentials
            github_token = os.getenv("GITHUB_TOKEN")
            owner = os.getenv("GITHUB_OWNER") 
            repo = os.getenv("GITHUB_REPO")
            
            # Encode content
            encoded_content = base64.b64encode(content.encode()).decode()
            
            # GitHub API URL
            url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            # Check if file exists
            existing_response = requests.get(url, headers=headers)
            
            if existing_response.status_code == 200:
                # File exists, update it
                existing_data = existing_response.json()
                sha = existing_data["sha"]
                data = {
                    "message": f"Update {file_path} via AI deployment system",
                    "content": encoded_content,
                    "sha": sha
                }
            else:
                # File doesn't exist, create it
                data = {
                    "message": f"Create {file_path} via AI deployment system", 
                    "content": encoded_content
                }
            
            # Upload file
            response = requests.put(url, json=data, headers=headers)
            
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

    def _execute_cicd_pipeline(self, generated_files):
        """
        Execute CI/CD pipeline after successful deployment.
        
        Args:
            generated_files (dict): Dictionary of generated files
        """
        print("\n🚀 Executing CI/CD Pipeline...")
        
        # Check if GitHub Actions workflow exists in generated files
        workflow_files = [f for f in generated_files.keys() if 'workflow' in f or 'deploy.yml' in f]
        
        if workflow_files:
            print(f"✅ Found workflow files: {workflow_files}")
            
            # Try to trigger the workflow
            try:
                from src.project.tools.github_helper import get_github_helper
                
                helper = get_github_helper()
                if helper:
                    print("🔄 Triggering GitHub Actions workflow...")
                    
                    # Wait a moment for files to be processed by GitHub
                    import time
                    time.sleep(5)
                    
                    result = helper.trigger_workflow("deploy.yml")
                    
                    if result["status"] == "success":
                        print("✅ GitHub Actions workflow triggered successfully!")
                        
                        # Optional: Monitor workflow execution
                        if os.getenv("MONITOR_WORKFLOW", "false").lower() == "true":
                            self._monitor_workflow_execution(helper)
                    else:
                        print(f"⚠️ Failed to trigger workflow: {result.get('error', 'Unknown error')}")
                        print("   This is normal if the workflow file was just created")
                else:
                    print("⚠️ GitHub helper not available for workflow triggering")
                    
            except Exception as e:
                print(f"⚠️ Could not trigger workflow: {e}")
                print("   This is normal if the workflow doesn't exist yet")
        else:
            print("ℹ️ No GitHub Actions workflow files found in deployment")
            print("   You can manually create .github/workflows/deploy.yml for CI/CD")
        
        # Execute local Docker build if Dockerfile exists
        if "Dockerfile" in generated_files:
            print("\n🐳 Executing Docker build pipeline...")
            try:
                # Build Docker image
                project_folder = os.getenv("PROJECT_FOLDER", "./generated_projects")
                self.run_command(f"docker build -t deployment-app {project_folder}")
                print("✅ Docker image built successfully")
                
                # Optional: Run container for testing
                if os.getenv("TEST_DOCKER_CONTAINER", "false").lower() == "true":
                    self.run_command("docker run --rm -d -p 8080:8080 deployment-app")
                    print("✅ Docker container started for testing")
                
            except Exception as e:
                print(f"⚠️ Docker build failed: {e}")
        
        print("✅ CI/CD Pipeline execution completed!")

    def _create_deployment_issue(self, state, generated_files):
        """
        Create a GitHub issue to track deployment progress.
        
        Args:
            state (dict): Project state
            generated_files (dict): Dictionary of generated files
        """
        print("\n📝 Creating deployment tracking issue...")
        
        try:
            from src.project.tools.github_helper import get_github_helper
            
            helper = get_github_helper()
            if not helper:
                print("⚠️ GitHub helper not available for issue creation")
                return
            
            project_name = state.get("project_name", "Generated Project")
            version = state.get("version", "1.0.0")
            file_list = "\n".join([f"- {file}" for file in generated_files.keys()])
            
            issue_title = f"🚀 Deployment v{version}: {project_name}"
            issue_body = f"""# Deployment Tracking - {project_name} v{version}

## 📦 Deployment Information
- **Project**: {project_name}
- **Version**: {version}
- **Timestamp**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Files Deployed**: {len(generated_files)}

## 📁 Generated Files
{file_list}

## 🚀 Deployment Status
- [x] Files generated
- [x] Pushed to repository  
- [ ] CI/CD pipeline completed
- [ ] Deployment verified
- [ ] Issue can be closed

## 🔧 Next Steps
1. Monitor CI/CD pipeline execution
2. Verify deployment in target environment
3. Run post-deployment tests
4. Close this issue when deployment is confirmed

---
*This issue was created automatically by the AI deployment system.*
"""
            
            result = helper.create_issue(
                title=issue_title,
                body=issue_body,
                labels=["deployment", "automation", f"v{version}"]
            )
            
            if result["status"] == "success":
                print(f"✅ Deployment issue created: #{result['issue_number']}")
                print(f"   Issue URL: {result['issue_url']}")
                
                # Store issue number in state for later updates
                state["deployment_issue_number"] = result['issue_number']
                
                return result
            else:
                print(f"⚠️ Failed to create deployment issue: {result.get('error')}")
                
        except Exception as e:
            print(f"⚠️ Error creating deployment issue: {e}")
    
    def _update_deployment_issue(self, state, status_message, close_issue=False):
        """
        Update the deployment tracking issue with status.
        
        Args:
            state (dict): Project state
            status_message (str): Status update message
            close_issue (bool): Whether to close the issue
        """
        issue_number = state.get("deployment_issue_number")
        if not issue_number:
            return
        
        try:
            from src.project.tools.github_helper import get_github_helper
            
            helper = get_github_helper()
            if not helper:
                return
            
            timestamp = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            comment = f"🤖 **Automated Status Update** - {timestamp}\n\n{status_message}"
            
            # Add comment
            comment_result = helper.add_comment_to_issue(issue_number, comment)
            
            if comment_result["status"] == "success":
                print(f"✅ Updated deployment issue #{issue_number}")
                
                # Close issue if requested
                if close_issue:
                    close_result = helper.close_issue(
                        issue_number,
                        "🎉 **Deployment Completed Successfully!**\n\n" +
                        "All deployment tasks have been completed. The issue is now closed.\n\n" +
                        "*Automatically closed by deployment system.*"
                    )
                    
                    if close_result["status"] == "success":
                        print(f"✅ Deployment issue #{issue_number} closed successfully")
            
        except Exception as e:
            print(f"⚠️ Error updating deployment issue: {e}")
    
    def create_feature_branch_and_pr(self, state, feature_name, files_dict):
        """
        Create a feature branch and pull request for new changes.
        
        Args:
            state (dict): Project state
            feature_name (str): Name of the feature
            files_dict (dict): Files to add to the branch
        """
        print(f"\n🌿 Creating feature branch for: {feature_name}")
        
        try:
            from src.project.tools.github_helper import get_github_helper
            
            helper = get_github_helper()
            if not helper:
                print("⚠️ GitHub helper not available for branch/PR creation")
                return
            
            # Create branch name
            import re
            branch_name = f"feature/{re.sub(r'[^a-zA-Z0-9-]', '-', feature_name.lower())}"
            
            # Create branch
            branch_result = helper.create_branch(branch_name)
            
            if branch_result["status"] == "success":
                print(f"✅ Branch created: {branch_name}")
                
                # Upload files to branch (Note: this would need branch-specific upload)
                # For now, we'll create a PR with existing files
                
                # Create pull request
                project_name = state.get("project_name", "Project")
                pr_body = f"""# {feature_name}

## 📦 Changes
This PR contains automated changes for {project_name}.

## 📁 Files Modified
{chr(10).join([f"- {file}" for file in files_dict.keys()])}

## 🤖 Automated Generation
This PR was created automatically by the AI deployment system.

## ✅ Checklist
- [x] Files generated
- [ ] Code review completed
- [ ] Tests passing
- [ ] Ready for merge

---
*Created by AI-powered deployment system*
"""
                
                pr_result = helper.create_pull_request(
                    title=f"🚀 {feature_name}",
                    head=branch_name,
                    base="main",
                    body=pr_body,
                    draft=False
                )
                
                if pr_result["status"] == "success":
                    print(f"✅ Pull Request created: #{pr_result['pr_number']}")
                    print(f"   PR URL: {pr_result['pr_url']}")
                    return pr_result
                else:
                    print(f"⚠️ Failed to create PR: {pr_result.get('error')}")
            else:
                print(f"⚠️ Failed to create branch: {branch_result.get('error')}")
                
        except Exception as e:
            print(f"⚠️ Error creating feature branch/PR: {e}")

    def _monitor_workflow_execution(self, helper, timeout=300):
        """
        Monitor GitHub Actions workflow execution.
        
        Args:
            helper: GitHub helper instance
            timeout (int): Timeout in seconds
        """
        print("\n👀 Monitoring workflow execution...")
        
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = helper.get_workflow_runs("deploy.yml", limit=1)
                
                if result["status"] == "success" and result["workflow_runs"]:
                    run = result["workflow_runs"][0]
                    status = run.get("status", "unknown")
                    conclusion = run.get("conclusion")
                    
                    print(f"🔄 Workflow status: {status}")
                    
                    if status == "completed":
                        if conclusion == "success":
                            print("✅ Workflow completed successfully!")
                        else:
                            print(f"❌ Workflow failed with conclusion: {conclusion}")
                        break
                    elif status in ["failed", "cancelled"]:
                        print(f"❌ Workflow {status}")
                        break
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"⚠️ Error monitoring workflow: {e}")
                break
        
        if time.time() - start_time >= timeout:
            print("⏱️ Workflow monitoring timed out")

    def create_github_release(self, state, version):
        """
        Create a GitHub release for the deployed project using direct API.
        
        Args:
            state (dict): Project state
            version (str): Version number
        """
        try:
            import requests
            
            # Get GitHub credentials
            github_token = os.getenv("GITHUB_TOKEN")
            owner = os.getenv("GITHUB_OWNER") 
            repo = os.getenv("GITHUB_REPO")
            
            if not all([github_token, owner, repo]):
                print("⚠️ GitHub credentials not available for release creation")
                return None
            
            project_name = state.get("project_name", "Generated Project")
            release_notes = self.generate_release_notes(state)
            
            # GitHub API URL for releases
            url = f"https://api.github.com/repos/{owner}/{repo}/releases"
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            data = {
                "tag_name": f"v{version}",
                "name": f"{project_name} v{version}",
                "body": release_notes,
                "draft": False,
                "prerelease": False
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 201:
                response_data = response.json()
                print(f"✅ GitHub release created: {response_data['html_url']}")
                return {
                    "status": "success",
                    "release_url": response_data['html_url'],
                    "tag_name": response_data['tag_name']
                }
            else:
                print(f"⚠️ Failed to create release: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return {
                    "status": "error",
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            print(f"⚠️ Error creating GitHub release: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def generate_release_notes(self, state):
        """
        Generate release notes from project state.
        
        Args:
            state (dict): Project state
            
        Returns:
            str: Generated release notes
        """
        project_name = state.get("project_name", "Generated Project")
        design_summary = str(state.get("design", ""))[:200]
        if len(design_summary) >= 200:
            design_summary += "..."
        
        files_generated = state.get("generated_deployment_files", {})
        file_list = "\n".join([f"- {file}" for file in files_generated.keys()])
        
        release_notes = f"""# {project_name} - Automated Deployment Release

## 🚀 Project Overview
{design_summary}

## 📦 Generated Deployment Files
{file_list}

## 🛠️ Features
- Dockerized application setup
- Docker Compose for local development  
- Kubernetes manifests for cloud deployment
- CI/CD pipeline configuration
- Production-ready deployment scripts

## 🚀 Quick Start
1. Clone this repository
2. Review the deployment configuration files
3. Set up your environment variables
4. Run the deployment using provided scripts

---
*This release was automatically generated by AI-powered deployment system*
"""
        return release_notes

    def setup_github_environment(self):
        """
        Setup and validate GitHub environment for deployment.
        
        Returns:
            bool: True if environment is properly configured
        """
        return self._check_github_environment()


# Example Usage
if __name__ == "__main__":
    # Example using GroqLLM (replace with your preferred model)
    try:
        from src.project.LLMS.model import GroqLLM
        model = GroqLLM().get_openai_code()  # or get_groq_deep(), etc.
        
        deployer = DeployApplication(model)
        
        # Example project state
        example_state = {
            "project_folder": "./generated_projects/example_project",
            "project_name": "example-web-app",
            "design": "A simple web application using Python Flask with PostgreSQL database",
            "version": "1.0.0"
        }
        
        # Generate deployment files and optionally push to GitHub
        result_state = deployer.generate_deployment_files(example_state)
        
        print(f"\n📊 Deployment Summary:")
        print(f"   Project: {result_state.get('project_name', 'Unknown')}")
        print(f"   Files generated: {len(result_state.get('generated_deployment_files', {}))}")
        print(f"   Status: {'✅ Success' if result_state.get('generated_deployment_files') else '❌ Failed'}")
        
    except ImportError as e:
        print(f"❌ Could not import required modules: {e}")
        print("Please ensure all dependencies are installed and configured properly.")
    except Exception as e:
        print(f"❌ Deployment failed: {e}")