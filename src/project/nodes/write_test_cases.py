from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output
import os
from src.project.utils.file_manager import save_generated_code


class WriteTestCases:
    """
    AI-powered security review for validating the security compliance of the generated code.
    """

    def __init__(self, model):
        """
        Initializes the SecurityReview node with an AI model.
        """
        self.llm = model

    def test_cases(self, state):
        """
        Conducts a security audit on the generated code.

        Args:
            state (dict): Contains user story, design document, generated code, and project folder.

        Returns:
            dict: Security review feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Write_Test_Cases")
        project_root = state.get("project_folder")
        if not project_root:
            raise ValueError("❌ Error: Project folder not found in state")
        os.makedirs(project_root, exist_ok=True)

        generated_code = state["generated_code"]
        
            
        if state.get("test_cases_feedback"):
            prompt = f"""
        You are a test engineer improving existing test cases based on feedback.
        Focus on addressing critical issues while preserving working tests.

        ## 📋 Context
        ### Feedback:
        {state['test_cases_feedback']}

        ### Current Tests:
        ```python
        {state['test_cases']}
        ```

        ### Design Document:
        {state['design']}

        ---
        ## 🔍 Improvement Guidelines

        ### 1. Address Feedback
        - Fix identified issues
        - Keep working tests unchanged
        - Maintain test clarity
        - Ensure proper coverage

        ### 2. Quality Standards
        - Clear test organization
        - Proper assertions
        - Good error messages
        - Efficient setup/teardown

        ### 3. Framework Usage
        - Follow pytest best practices
        - Proper fixture usage
        - Clean test isolation
        - Effective mocking

        ---
        ## 📝 Output Format
        Provide updated test files:
        ```plaintext
        ```tests/test_core.py
        <updated test code>

        ```tests/test_api.py
        <updated test code>

        ```tests/conftest.py
        <updated fixtures>
        ```
        ---
         **DO NOT** include explanations, reasoning, or placeholders.  
        """
        else:
            prompt = f"""
        You are a software test engineer creating test cases for the given code.
        Focus on essential functionality while maintaining good testing practices.

        ## 📋 Context
        ### Design Document:
        {state['design']}

        ### Code to Test:
        ```python
        {generated_code}
        ```

        ---
        ## 🔍 Testing Guidelines

        ### 1. Essential Test Coverage
        - Unit tests for core functionality
        - Basic integration tests
        - Critical edge cases
        - Error handling scenarios

        ### 2. Test Structure
        - Organize tests by feature/module
        - Clear test names and descriptions
        - Setup and teardown handling
        - Mock external dependencies

        ### 3. Testing Framework
        - Use pytest for Python tests
        - Include necessary fixtures
        - Group related tests
        - Basic parameterization

        ### 4. Quality Checks
        - Input validation
        - Basic security checks
        - Error scenarios
        - Performance considerations

        ---
        ## 📝 Output Format
        Generate test files in this structure:
        ```plaintext
        tests/
        test_core.py     # Core functionality tests
        test_api.py      # API endpoint tests
        conftest.py      # Shared fixtures
        requirements.txt  # Test dependencies
        ```

        Example response format:
        ```plaintext
        ```tests/test_core.py
        <test code>

        ```tests/test_api.py
        <test code>

        ```tests/conftest.py
        <fixtures>

        ```tests/requirements.txt
        <dependencies>
        ```
        ---
         **DO NOT** include explanations, reasoning, or placeholders.  
        """

        print("\n🚀 Generating test cases for the code...")

        # **4️⃣ Invoke AI model to generate test cases**
        ai_response_test_cases = self.llm.invoke([HumanMessage(content=prompt)]).content

        print("\n🔍 AI Test Case Response:", ai_response_test_cases)

        # **5️⃣ Parse AI response safely**
        generated_test_dict = self.parse_code_response(ai_response_test_cases)

        # ✅ Save the generated test cases in the user-specified project folder
        if generated_test_dict:
            print("\n💾 Saving generated test case files...")
            save_generated_code(generated_test_dict, project_root)
            print("\n✅ Test case generation complete!")
        else:
            print("\n⚠️ No test files were generated from the AI response")

        print("\n✅ Test case generation complete! Ready for execution...")

        # **7️⃣ Return updated state with new test cases**
        return {**state, "test_cases": generated_test_dict}

    def parse_code_response(self, response):
        """
        Parses the AI-generated response into a dictionary mapping file paths to code.
        """
        code_blocks = response.split("```")  # AI formats code blocks using ```
        file_mapping = {}

        for block in code_blocks:
            lines = block.strip().split("\n")
            if len(lines) > 1:
                file_name = lines[0].strip()  # First line should be the file name
                file_mapping[file_name] = "\n".join(lines[1:])  # Rest is code

        return file_mapping