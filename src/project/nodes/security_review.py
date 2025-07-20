from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output


class SecurityReview:
    """
    AI-powered security review for validating the security compliance of the generated code.
    """

    def __init__(self, model):
        """
        Initializes the SecurityReview node with an AI model.
        """
        self.llm = model

    def security_review(self, state):
        """
        Conducts a security audit on the generated code.

        Args:
            state (dict): Contains user story, design document, generated code, and project folder.

        Returns:
            dict: Security review feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Security_Review")

        # Ensure the generated code is available for review
        if "generated_code" not in state or not state["generated_code"]:
            return {**state, "security_feedback": "❌ Error: No generated code available for security review."}

        # AI Security Review Prompt
        security_review_prompt = f"""
        You are a security engineer conducting a focused security assessment of the code.
        Your goal is to identify critical security issues while maintaining practicality.

        ## 📋 Context
        ### Requirements:
        {state["requirements"]}

        ### Design Document:
        {state["design"]}

        ### Code for Review:
        ```python
        {state["generated_code"]}
        ```

        ---
        ## 🔍 Security Review Guidelines

        ### 1. Essential Security (Must Check)
        - Authentication implementation (if user auth is required)
        - Password handling and storage
        - Basic input validation
        - Protection of sensitive data
        - API endpoint security

        ### 2. Data Protection
        - Data encryption (where necessary)
        - Secure storage of credentials
        - Safe handling of user data
        - Database security

        ### 3. Application Security
        - Input sanitization
        - Error handling
        - Session management
        - Access control

        ### 4. Infrastructure & Deployment
        - Environment configuration
        - Dependency management
        - Basic logging setup
        - Deployment security

        Note: Focus on security measures that are:
        - Critical for the specific use case
        - Proportional to the application's risk level
        - Required by the project requirements

        ---
        ## 🚦 Response Format

        For code that meets essential security requirements:
        ```plaintext
        APPROVED
        ```

        For code with security issues:
        ```plaintext
        REJECTED
        1. Issue 1: <Clear security vulnerability description>
        2. Issue 2: <Clear security vulnerability description>
        ...
        ```

        Only reject for:
        - Critical security flaws
        - Missing essential security features
        - Clear vulnerabilities
        - Non-compliance with basic security practices

        Note: Focus on practical security measures rather than theoretical perfection.
        """  
        state["number_of_rejections_for_security"] = state.get("number_of_rejections_for_security" , 0) + 1
        print("\n🔍 Performing Security Review...")

        # Invoke AI model for security review
        ai_security_response = self.llm.invoke([HumanMessage(content=security_review_prompt)]).content
        ai_security_response = clean_deepseek_output(ai_security_response)

        print("\n🔍 Security Review Feedback:", ai_security_response)

        # Return security feedback
        return {**state, "security_feedback": ai_security_response}


    @staticmethod
    def should_continue(state):
        """
        Determines if the code review should continue based on feedback.
        """
        feedback = state.get("security_feedback", "")

        if state["number_of_rejections_for_security"] >= 2:
            print("Approved forcefully to Write_Test_Cases")
            state["number_of_rejections_for_security"] = 0
            return "Write_Test_Cases"
        elif "REJECTED" in feedback:
            print("\n🔄 InSecure Code Rejected! Regenerating Secure Code...")
            return "Code_After_Security"
        else:
            print("✅ Code Approved! Moving to Write Test Cases...")
            return "Write_Test_Cases"
