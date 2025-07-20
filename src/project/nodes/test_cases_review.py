from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output

class TestCasesReview:
    """
    AI-powered Test Case Reviewer that verifies the completeness and correctness of test cases.
    Iterates until the test cases meet quality standards.
    """

    def __init__(self, model):
        """
        Initializes the TestCaseReview class with an AI model.
        """
        self.llm = model

    def review_test_cases(self, state):
        """
        Reviews AI-generated test cases and provides feedback for improvements.

        Args:
            state (dict): Contains design, generated code, and test cases.

        Returns:
            dict: Decision to approve or provide feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Test_Cases_Review")
        design_text = state["design"]
        generated_code = state["generated_code"]
        test_cases = state["test_cases"]

        # AI Prompt for Test Case Review
        prompt = f"""
        You are a QA engineer reviewing automated test cases.
        Focus on essential test coverage while maintaining practical quality standards.

        ## 📋 Review Context

        ### Design Document:
        {design_text}

        ### Implementation:
        {generated_code}

        ### Test Cases:
        {test_cases}

        ---
        ## 🔍 Review Guidelines

        ### 1. Core Testing (Essential)
        - Basic functionality
        - Critical user flows
        - Common error cases
        - Data validation

        ### 2. Test Structure
        - Clear test names
        - Setup/teardown
        - Proper assertions
        - Error handling

        ### 3. Testing Practices
        - Unit test isolation
        - Integration points
        - Mock usage
        - Database handling

        ### 4. Quality Factors
        Consider based on requirements:
        - Performance checks
        - Security validation
        - Edge cases
        - Error scenarios

        Note: Focus on tests that:
        - Validate core features
        - Catch common issues
        - Enable automation
        - Support maintenance

        ---
        ## 🚦 Response Format

        For complete test coverage:
        ```plaintext
        APPROVED
        ```

        For incomplete coverage:
        ```plaintext
        REJECTED
        1. Issue 1: <Clear description>
        2. Issue 2: <Clear description>
        ```

        Note: Only reject for issues that:
        - Miss critical functionality
        - Have incorrect assertions
        - Lack proper isolation
        - Create maintenance problems
        ⚠ **DO NOT add explanations or extra text. Only use the specified response format.**
        """
        state["number_of_rejections_for_test_cases"] = state.get("number_of_rejections_for_test_cases", 0) + 1

        ai_test_response = self.llm.invoke([HumanMessage(content=prompt)]).content
        ai_test_response = clean_deepseek_output(ai_test_response)

        state["test_cases_feedback"] = ai_test_response
        return state

    @staticmethod
    def should_continue(state):
        """
        Determines if test cases should proceed or be revised.

        Args:
            state (dict): The current state dictionary.

        Returns:
            str: Next node to execute ("Test_Case_Fix" or "Run_Tests").
        """
        feedback = state.get("test_cases_feedback")
        if state["number_of_rejections_for_test_cases"] >= 2:
            state["number_of_rejections_for_test_cases"] = 0  # Reset counter
            return "QA_Testing"
        elif "REJECTED" in feedback:
            return "Write_Test_Cases"
        else:
            return "QA_Testing"
