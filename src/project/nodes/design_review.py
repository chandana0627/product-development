from src.project.state.state import State
from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output

class DesignReview:
    """
    AI-powered Design Reviewer that checks if the design is complete and meets quality standards.
    Loops until the design is satisfactory.
    """

    def __init__(self, model):
        """
        Initializes the DesignReview class with an AI model.
        """
        self.llm = model

    def review_design(self, state):
        """
        Reviews the AI-generated design and provides feedback until it meets the requirements.

        Args:
            state (dict): Contains requirements, user story, and generated design.

        Returns:
            dict: Decision to approve or send feedback.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Design_Review")
        requirements = state["requirements"]
        user_story = state["story"]
        design_text = state["design"]

        # AI Prompt for Design Review
        prompt = f"""
        You are an experienced software architect performing a practical design review.
        Your goal is to ensure the design satisfies core requirements while maintaining flexibility for future enhancements.
        ## 📋 Project Context
        ### Requirements:
        {requirements}
        ### User Story:
        {user_story}
        ### Design Document:
        {design_text}
        ---
        ## 🔍 Review Guidelines
        ### 1. Essential Requirements (Must Have)
        - Does the design address all core user requirements?
        - Is the basic system architecture defined?
        - Are critical components and their interactions specified?
        ### 2. Technical Architecture (As Needed)
        Based on project requirements, evaluate:
        - Frontend: Technology stack and key components should be present
        - Backend: API design and service architecture
        - Database: Data model and relationships
        - Integration: External system interfaces
        ### 3. Non-Functional Requirements (If Applicable)
        Consider only if specifically required:
        - Security: Authentication, authorization, data protection
        - Performance: Response times, resource usage
        - Scalability: Growth handling, load management
        - Maintenance: Logging, monitoring, deployment
        ### 4. Project Constraints
        - Are the chosen technologies appropriate?
        - Does the design fit project timeline and resources?
        - Are there any technical limitations addressed?
        ---
        ## ⚖️ Evaluation Approach
        - Focus on requirements-driven decisions
        - Accept pragmatic solutions over perfect architecture
        - Consider project scope and constraints
        - Allow for iterative improvements
        ---
        ## 🚦 Response Format
        For a satisfactory design that meets core requirements:
        ```plaintext
        APPROVED
        ```
        For designs with critical issues:
        ```plaintext
        REJECTED
        1. Issue 1: <Clear description of critical problem>
        2. Issue 2: <Clear description of critical problem>
        ...
        ```
        Note: Only reject for issues that:
        - Prevent core functionality delivery
        - Risk project success
        - Violate essential requirements
        - Create significant technical debt

        Focus on critical feedback that drives immediate improvements.
        """
       
        state["number_of_rejections_for_design"] = state.get("number_of_rejections_for_design", 0) + 1

        ai_design_response = self.llm.invoke([HumanMessage(content=prompt)]).content
        ai_design_response = clean_deepseek_output(ai_design_response)

        
        state["design_feedback"] = ai_design_response
        print("\n🔍 Design Review Feedback:", ai_design_response)
        return state

        # Parse AI response
        


    @staticmethod
    def should_continue(state):
        """
        Determines if the design should proceed or be revised.

        Args:
            state (dict): The current state dictionary.

        Returns:
            str: Next node to execute ("Design" or "Generate_Code").
        """
        feedback = state.get("design_feedback")
        if state["number_of_rejections_for_design"] >= 2:
            print("Approved forcefully to generate code")
            return "Generate_Code"
        elif "APPROVED" in feedback:
            return "Generate_Code"
        else:
            return "Design"
      





