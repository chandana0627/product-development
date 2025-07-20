import os
from langchain_core.messages import HumanMessage
from src.project.utils.file_manager import save_generated_code
import re
import streamlit as st

class GenerateCode:
    """
    AI-powered code generation based on the approved design document.
    """

    def __init__(self, model):
        """
        Initializes the GenerateCode node with an AI model.
        """
        self.llm = model

    def generate_code(self, state):
        """
        Generates code based on the approved design document.
        Saves it in the user-defined project folder.

        Args:
            state (dict): Contains user story, design document, feedback, and project folder.

        Returns:
            dict: Dictionary containing generated code files.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Generate_Code")
        st.session_state.current_node = "Generate_Code"
        requirements = state["requirements"]
        user_story = state["story"]
        design_text = state["design"]

        # Ensure project folder exists
        project_root = state.get("project_folder")
        if not project_root:
            raise ValueError("❌ Error: Project folder not found in state")
        os.makedirs(project_root, exist_ok=True)

        # AI Prompt
        prompt = f"""
        You are an expert software engineer responsible for generating **clean, modular, and scalable code** based on the approved software design.
        The generated project **must be structured correctly into separate folders** for maintainability.
        ---  
        ### **📌 User Requirements:**  
        {requirements}
        ### **📌 User Story:**  
        {user_story}
        ### **📌 Approved Design Document:**  
        {design_text}
        ---  
        ## **🔹 Task:**  
        - Generate **fully functional, well-structured** code **following the given design, user story, and requirements**.  
        - Follow **best practices**: Clean Code, DRY, Reusability, and PEP8 (for Python).  
        - Ensure that **files are organized into the correct folders** for maintainability.  
        - **DO NOT create all files in one place**—**use a structured folder hierarchy**.
        ---  
        ## **✅ Project Structure & Expected Output Format**  
        Your output **must** follow this **modular structure**:  
        ```plaintext
        📂 project_root/
        ├── 📂 src/                  # Main Source Code
        │   ├── 📂 api/              # API-related files
        │   │   ├── routes.py
        │   │   ├── __init__.py
        │   │
        │   ├── 📂 models/           # Database models
        │   │   ├── user.py
        │   │   ├── __init__.py
        │   │
        │   ├── 📂 services/         # Business logic
        │   │   ├── chatbot.py
        │   │   ├── __init__.py
        │   │
        │   ├── 📂 database/         # Database-related operations
        │   │   ├── connection.py
        │   │   ├── __init__.py
        │   │
        │   ├── config.py           # Configuration settings
        │   ├── app.py              # Main entry point for the application
        │
        ├── 📂 tests/                # Unit & integration tests
        │   ├── test_models.py
        │
        ├── requirements.txt         # Dependencies
        ├── README.md                # Project documentation
        ├── .gitignore               # Git ignore file
        ```   
        ---  
        ## **🔹 Additional Instructions**  
        - **DO NOT** add explanations or unnecessary text.  
        - **DO NOT** include `<think>` or reasoning steps—only structured code.  
        - **Ensure each file is saved in the correct folder** as per the structure.  
        - If dependencies are needed, generate a `requirements.txt` file.  
        - If configuration is required, generate a `config.py` file.  
        - **All database-related files must be in the `database/` folder.**  
        - **API routes and logic must be inside the `api/` folder.**  
        ---  
        ## **🛠 Example Output Format**  
        Your response **must strictly follow this format**:  
        ```plaintext
        ```src/api/routes.py
        <code for routes.py>        
        ```
        ```src/models/user.py
        <code for user.py>
        ```
        ```src/database/connection.py
        <code for database connection>
        ```
        ```requirements.txt
        <dependencies list>
        ```
        ```
        the above provided example is to understand the format of the response that is expected please don't follow as it is according to the use case you have to generate it accordingly.
        ⚠️ For the README file:
        - Provide the entire content inside a single code block like this:
        ```README.md
        # Project Title
        ## Introduction
        <project description>
        ## API Endpoints
        <list endpoints here>
        ## Installation
        <steps>
        ## Contributing
        <guidelines>
        ⚠️ For the README:
        - Wrap the entire content inside a single code block:
        ```README.md
        <full markdown content here>
        This is just a formate you can add anything or remove anything as per your use case.
        """

        print("\n🚀 Generating code files...")

        # Invoke AI model to generate code
        ai_response_code = self.llm.invoke([HumanMessage(content=prompt)]).content

        # ✅ Parse AI response into structured files
        generated_code_dict = self.parse_code_response(ai_response_code)

        # ✅ Save the generated code in the user-specified project folder
        if generated_code_dict:
            print("\n💾 Saving generated code files...")
            save_generated_code(generated_code_dict, project_root)
            print("\n✅ Code generation complete!")
        else:
            print("\n⚠️ No code files were generated from the AI response")

        return {"generated_code": generated_code_dict, "project_folder": project_root, "current_node" : "Generate_Code"}

    def parse_code_response(self, response):
        """
        Parses the AI-generated code response into a dict {file_path: content}, cleaning invalid filenames.
        """
        code_blocks = response.split("```")
        file_mapping = {}
        readme_buffer = []

        # Allow only valid filenames with extensions like .py, .md, .txt etc.
        valid_file_pattern = re.compile(r'^[\w\-./\\]+(\.\w+)$')

        for block in code_blocks:
            lines = block.strip().split("\n")
            if len(lines) < 2:
                continue

            file_name = lines[0].strip()
            file_content = "\n".join(lines[1:])

            # Ignore folder names like 'project_root/' or reserved names
            if file_name.lower().startswith("project_root") or file_name.lower().endswith("/"):
                print(f"Skipping invalid folder reference: {file_name}")
                continue

            # Merge README content into one file
            if "readme" in file_name.lower() or file_name.lower().endswith(".md"):
                readme_buffer.append(file_content)
                continue

            # Ignore non-code section labels (markdown, shell, etc.)
            if not valid_file_pattern.match(file_name):
                print(f"⚠️ Ignoring invalid filename: {file_name}")
                continue

            file_mapping[file_name] = file_content

        # Combine README content safely
        if readme_buffer:
            file_mapping["README.md"] = "\n\n".join(readme_buffer)

        return file_mapping
