import os
import ast  # ✅ Safe parsing instead of eval()
from langchain_core.messages import HumanMessage
from src.project.utils.file_manager import save_generated_code, clear_project_folder

class CodeAfterSecurity:
    """
    Handles regenerating code after review and saving it in the project folder.
    """

    def __init__(self, model):
        """
        Initializes the class with an AI model.
        """
        self.llm = model

    def regenerate_secure_code(self, state):
        """
        If the Code is insecure,It will regenerates and saves updated code.

        Args:
            state (dict): Contains requirements, user story, project folder path, and review feedback.

        Returns:
            dict: Updated state with regenerated code.
        """  
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Code_After_Security")
        project_root = state.get("project_folder")
        if not project_root:
            raise ValueError("❌ Error: Project folder not found in state")
        os.makedirs(project_root, exist_ok=True)

        generated_code = state["generated_code"]
    
        # **3️⃣ AI Prompt to Regenerate Code**
        regenerate_prompt = f"""
        You are a **highly skilled senior software security engineer** responsible for **modifying code after a security review**.  
        Your task is to **fix all identified security vulnerabilities** while keeping all previously correct parts intact.
        ---  
        ## **🔹 Security Issues Identified (Fix These)**
        The previous code was **rejected** due to the following security vulnerabilities:  
        {state['security_feedback']}
        **Carefully analyze each issue and ensure all security flaws are fixed.**  
        Use the following to guide your updates:  
        The following is the previously generated code.  
        ✅ **Keep all correct parts unchanged** and **apply fixes only where necessary**.
        ```python
        {generated_code}
        ```
        ---  
        ## **🔹 Code Modification Guidelines**
        - **Fix only the security vulnerabilities** while preserving correct functionality.  
        - Ensure the code follows **secure coding practices (OWASP, ISO 27001, NIST, etc.).**  
        - Implement **proper authentication, encryption, and input validation** where necessary.  
        - Ensure **secure database queries** (use parameterized queries, avoid SQL injections).  
        - **Sanitize user inputs** to prevent XSS, CSRF, and injection attacks.  
        - **DO NOT introduce unnecessary placeholder code.**  
        - **DO NOT** rewrite the entire code unless absolutely necessary.
        ---  
        ## **🛠 Example Output Format**  
        Your response **must strictly follow this format**:  
        ```plaintext
        ```src/api/routes.py
        <code for routes.py with security fixes>
        ```
        ```src/models/user.py
        <code for user.py with security improvements>
        ```
        ```src/database/connection.py
        <code for secure database connection>
        ```
        ```requirements.txt
        <dependencies list, if modified>
        ```
        The above format is provided to understand the response structure.  
        Generate the output **as per the security fixes required**.
        ---  
        **⚠️ STRICT INSTRUCTIONS:**  
        - **DO NOT** rewrite the entire code unless absolutely necessary.  
        - **DO NOT** include explanations, reasoning, or placeholders.  
        - Ensure **ALL** identified security vulnerabilities are fixed before submitting.  
        """

        print("\n🚀 Generating updated code based on feedback...")

        # **4️⃣ Invoke AI model to regenerate the code**
        ai_response_secure_code = self.llm.invoke([HumanMessage(content=regenerate_prompt)]).content
        
        print("\n🔍 AI Secure Code Response:", ai_response_secure_code)

        # **5️⃣ Parse AI response safely**
        generated_code_dict = self.parse_code_response(ai_response_secure_code)

        # ✅ Save the generated code in the user-specified project folder
        if generated_code_dict:
            print("\n💾 Saving generated code files...")
            save_generated_code(generated_code_dict, project_root)
            print("\n✅ Code generation complete!")
        else:
            print("\n⚠️ No code files were generated from the AI response")

        print("\n✅ Code regeneration complete! Sending for review...")

        # **7️⃣ Return updated state with new code**
        return {**state, "generated_code": generated_code_dict}

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

    
