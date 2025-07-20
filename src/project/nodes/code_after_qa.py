import os
from langchain_core.messages import HumanMessage
from src.project.utils.file_manager import save_generated_code, clear_project_folder
import streamlit as st

class CodeAfterQA:
    """
    Handles regenerating test cases after QA review and saving them in the project folder.
    """

    def __init__(self, model):
        """
        Initializes the class with an AI model.
        """
        self.llm = model

    def regenerate_test_cases(self, state):
        """
        If the test cases are rejected, regenerates and saves updated test cases.

        Args:
            state (dict): Contains project folder path, test case feedback, and previously generated test cases.

        Returns:
            dict: Updated state with regenerated test cases.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Code_After_QA")
        project_folder = state.get("project_folder")
        st.session_state.current_node = "Code_After_QA"
        if not project_folder:
            return {**state, "test_case_feedback": "❌ Error: Project folder path is missing."}

        
        os.makedirs(project_folder, exist_ok=True)
        
        regenerate_prompt = f"""
        You are a **highly skilled senior software engineer** responsible for **fixing QA testing issues**.  
        Your task is to **resolve all identified failures** while keeping correct parts unchanged.
        ---  
        ## **🔹 QA Test Failures**
        The code failed due to the following reasons:  
        {state['qa_test_feedback']}
        ### **📌 Approved Design Document**  
        {state['design']}
        The previously generated code is provided below.  
        ✅ **Keep all correct parts unchanged** and **fix only the problematic sections**.
        ```python
        {state['generated_code']}
        ```
        ---  
        ## **🔹 Code Fixing Guidelines**
        - **Fix only the failing sections** while keeping correct functionality.
        - Ensure the code passes **all test cases** before responding.
        - Improve security, error handling, and scalability.
        - **DO NOT rewrite the entire code unless necessary.**
        - **DO NOT** include explanations or placeholders.
        ---  
        ## **🛠 Example Output Format**  
        Your response **must strictly follow this format**:  
        ```plaintext
        ```src/api/routes.py
        <updated code for routes.py>
        ```
        ```src/models/user.py
        <updated code for user.py>
        ```
        ```requirements.txt
        <updated dependencies if needed>
        ```
        ---
        **⚠️ STRICT INSTRUCTIONS:**  
        - **DO NOT** include explanations or reasoning.
        - Ensure **ALL** QA testing failures are fixed before responding.
        """

        print("\n🚀 Regenerating updated code based on QA feedback...")

        # **4️⃣ Invoke AI model to regenerate the code**
        ai_response_code = self.llm.invoke([HumanMessage(content=regenerate_prompt)]).content

        print("\n🔍 AI Response:", ai_response_code)

        # **5️⃣ Parse AI response safely**
        generated_code_dict = self.parse_code_response(ai_response_code)

        # ✅ Save the generated code in the user-specified project folder
        if generated_code_dict:
            print("\n💾 Saving updated code files...")
            save_generated_code(generated_code_dict, project_folder)
            print("\n✅ Code modification complete! Ready for re-testing.")
        else:
            print("\n⚠️ No valid code files were generated from the AI response")

        return {**state, "generated_code": generated_code_dict, "current_node": "Code_After_QA"}

    def parse_code_response(self, response):
        """
        Parses the AI-generated response into a dictionary mapping file paths to code.

        Args:
            response (str): AI-generated response.

        Returns:
            dict: Dictionary with file paths as keys and code as values.
        """
        code_blocks = response.split("```")  
        file_mapping = {}

        for block in code_blocks:
            lines = block.strip().split("\n")
            if len(lines) > 1:
                file_name = lines[0].strip()  
                file_mapping[file_name] = "\n".join(lines[1:])  

        return file_mapping