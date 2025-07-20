from src.project.state.state import State
from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output

class QATesting:
    """
    AI-powered QA Tester that reviews test cases to ensure they meet functional and quality requirements.
    Loops until all test cases are satisfactory.
    """

    def __init__(self, model):
        """
        Initializes the QATesting class with an AI model.
        """
        self.llm = model

    def review_test_cases(self, state):
        """
        Reviews the AI-generated test cases and provides feedback until they meet the requirements.

        Args:
            state (dict): Contains requirements, test cases, and design details.

        Returns:
            dict: Decision to approve or send feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("QA_Testing")
        requirements = state["requirements"]
        design_text = state["design"]
        test_cases = state["test_cases"]

        # AI Prompt for Test Case Review
        prompt = f"""
        You are a QA engineer reviewing test cases for completeness and quality.
        Focus on practical test coverage while maintaining testing standards.
        ## 📋 Review Context
        ### Requirements:
        {requirements}
        ### Design Document:
        {design_text}
        ### Test Cases:
        {test_cases}
        ---
        ## 🔍 Review Guidelines
        ### 1. Core Test Coverage
        - User requirements validation
        - Critical path testing
        - Error scenarios
        - Data validation
        ### 2. Test Quality
        - Clear test structure
        - Proper assertions
        - Well-documented steps
        - Expected outcomes
        ### 3. Test Types (If Applicable)
        - Unit tests
        - Integration tests
        - Performance tests
        - Security tests
        ### 4. Test Implementation
        - Automatable format
        - Test isolation
        - Proper setup/teardown
        - Maintainable code
        Note: Evaluate tests based on:
        - Core functionality coverage
        - Critical user flows
        - Essential error handling
        - Basic security needs
       ---
        ## 🚦 Response Format
        For complete test coverage:
        ```plaintext
        APPROVED
        ```
        For inadequate coverage:
        ```plaintext
        REJECTED
        1. Issue 1: <Clear description>
        2. Issue 2: <Clear description>
        ```
        Note: Focus on issues that:
        - Impact core functionality
        - Miss critical scenarios
        - Create maintenance problems
        - Prevent automation
        ⚠ **DO NOT add explanations or extra text. Only use the specified response format.**
        """
        print("\n🔍 Performing QA Test Review...")
        state["number_of_rejections_for_qa"] = state.get("number_of_rejections_for_qa", 0) + 1

        ai_test_review_response = self.llm.invoke([HumanMessage(content=prompt)]).content
        ai_test_review_response = clean_deepseek_output(ai_test_review_response)

        state["qa_test_feedback"] = ai_test_review_response
        return state

    @staticmethod
    def should_continue(state):
        """
        Determines if test cases should proceed to execution or be revised.

        Args:
            state (dict): The current state dictionary.

        Returns:
            str: Next node to execute ("Test_Execution" or "Test_Case_Review").
        """
        feedback = state.get("qa_test_feedback", "")
        if state["number_of_rejections_for_qa"] >= 2:
            print("Approved forcefully to Deployment")
            state["number_of_rejections_for_qa"] = 0
            return "Deployment"
        elif "REJECTED" in feedback:
            return "Code_After_QA"
        else:
            return "Deployment"
