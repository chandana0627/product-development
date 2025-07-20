from src.project.state.state import State
from langchain_core.messages import HumanMessage

class Design:
    """
    Generates system design based on approved user stories.
    """

    def __init__(self, model):
        """
        Initializes the Design class with the given AI model.
        """
        self.llm = model

    def build_design(self, state: State):
        """
        Generates a system design based on the approved user story.

        Args:
            state (State): The current state containing the approved user story.

        Returns:
            dict: Updated state with the system design.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Design")
        base_sections = """
        ## 📋 Design Document
        ### 1. System Overview
        - Purpose and Scope
        - Key Features
        - User Roles
        ### 2. Architecture
        - System Structure
        - frontend and backend separation
        - Database Design
        - External Integrations
        - Deployment Architecture
        - Data Storage
        - Security Architecture
        - Key Components
        - Data Flow
        ### 3. Technical Stack
        - Core Technologies
        - Key Libraries
        - Infrastructure
        ### 4. Implementation Details
        - Critical Features
        - Data Models
        - API Design
        ### 5. Non-Functional Requirements
        - Security Measures
        - Performance Goals
        - Scalability Plans
        ### Do not generate any code and <think> </think>.
        """
        
        if state.get("design_feedback"):  # If feedback exists, refine the design
            prompt = f"""
            You are a software architect refining a design based on feedback.
            Focus on addressing review comments while maintaining design stability.
            ## 📋 Context
            ### User Story:
            {state['story']}
            ### Current Design:
            {state['design']}
            ### Feedback:
            {state['design_feedback']}
            ---
            ## 🔍 Refinement Guidelines
            1. Address Feedback
            - Fix identified issues
            - Keep working elements
            - Maintain consistency
            - Improve clarity
            - Do not generate new design document for the same thing please modify the existing design document. 
            2. Design Structure
            {base_sections}
            Note:
            - Focus on feedback points
            - Keep successful parts
            - Improve weak areas
            - Maintain practicality
            - Don't Generate any code in this phase
            """
        else:
            prompt = f"""
            You are a software architect creating a practical design document.
            Focus on essential features while maintaining good architecture practices.
            ## 📋 Context
            ### User Story:
            {state['story']}
            ---
            ## 🔍 Design Guidelines
            {base_sections}
            Note: 
            - Include only relevant sections
            - Focus on critical features
            - Keep design practical
            - Use ASCII diagrams for clarity
            - Don't Generate any code in this phase
            """

        # Generate the design using the AI model
        ai_response = self.llm.invoke([HumanMessage(content=prompt)])
        print("\n🎨 Generating System Design Document...")
        print(ai_response.content)
        return {
            "design": ai_response.content,  # Store the generated design
            "story": state["story"]  # Preserve the story
        }