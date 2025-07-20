from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output
import streamlit as st

class CodeReview:
    """
    AI-powered Code Reviewer that checks if the code is complete and meets quality standards.
    Loops until the code is satisfactory.
    """

    def __init__(self, model):
        """
        Initializes the CodeReview class with an AI model.
        """
        self.llm = model

    def review_code(self, state):
        """
        Reviews the AI-generated code and provides feedback until it meets the requirements.

        Args:
            state (dict): Contains requirements, user story, and generated code.

        Returns:
            dict: Decision to approve or send feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Code_Review")
        st.session_state.current_node = "Code_Review"
        requirements = state["requirements"]
        user_story = state["story"]
        design_text = state["design"]
        generated_code = state.get("code_after_review") or state["generated_code"]
        prompt = f"""
        You are a senior software engineer conducting a practical code review.
        Focus on ensuring the code meets core requirements while maintaining good engineering practices.
        ## 📋 Review Context
        ### Design Document:
        {design_text}
        ### Generated Code:
        ```python
        {generated_code}
        ```
        ### Requirements:
        {requirements}
        ---
        ## 🔍 Review Guidelines
        ### 1. Core Functionality (Essential)
        - Does the code implement the main requirements?
        - Does it follow the approved design architecture?
        - Are all critical features implemented?
        ### 2. Code Structure
        - Is the code logically organized into modules?
        - Are dependencies clearly defined?
        - Is the code maintainable and readable?
        ### 3. Code Quality
        - Does it follow basic coding standards?
        - Are there any obvious bugs or errors?
        - Is error handling implemented where needed?
        ### 4. Project Files
        - Are all necessary files present?
        - Source code files
        - Configuration files
        - Basic documentation (README)
        - Requirements/dependencies list
        ### 5. Implementation Details
        - Are the chosen implementations practical?
        - Is the code efficient for common operations?
        - Are there any clear performance issues?
        Note: Security review and testing will be handled in separate phases.
        ---
        ## 🚦 Response Format
        For code that meets core requirements:
        ```plaintext
        APPROVED
        ```
        For code with significant issues:
        ```plaintext
        REJECTED
        1. Issue 1: <Clear description>
        2. Issue 2: <Clear description>
        ...
        ```
        Focus on issues that:
        - Prevent core functionality
        - Create maintenance problems
        - Cause obvious performance issues
        - Break basic coding standards
        """
        if 'number_of_rejections_for_code' not in state:
            state['number_of_rejections_for_code'] = 0
     
        state["number_of_rejections_for_code"] = state.get("number_of_rejections_for_code", 0) +1
        st.session_state.number_of_rejections_for_code = state["number_of_rejections_for_code"]
        ai_code_feedback = self.llm.invoke([HumanMessage(content=prompt)]).content
        ai_code_feedback = clean_deepseek_output(ai_code_feedback)
        print(f"AI Code Review Feedback: {ai_code_feedback}")
        return {"code_feedback": ai_code_feedback, "current_node" : "Code_Review"}
    
  
    @staticmethod
    def should_continue(state):
        """
        Determines if the code review should continue based on feedback.
        """
        feedback = state.get("code_feedback", "")
        if state["number_of_rejections_for_code"] >= 2:
            print("Approved forcefully to Security Review")
            state["number_of_rejections_for_code"] = 0
            st.session_state.number_of_rejections_for_code = 0
            return "Security_Review"

        elif "APPROVED" in feedback:
            print("✅ Code Approved! Moving to Security Review...")
            return "Security_Review"
        else:
            print("\n🔄 Code Rejected! Regenerating...")
            return "Code_After_Review"
