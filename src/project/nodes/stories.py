from src.project.state.state import State
from langchain_core.messages import HumanMessage
from src.project.utils.deep_clean import clean_deepseek_output


class Story:
    """
    Generates user stories based on input requirements and refines them based on user feedback.
    """

    def __init__(self, model):
        """
        Initializes the Story class with the given AI model.
        """
        self.llm = model

    def generate_story(self, state: State):
        """
        Generates or refines a user story based on the requirements or user feedback.

        Args:
            state (State): The current state containing user requirements and feedback.

        Returns:
            dict: Updated state with AI-generated user stories.
        """
        from src.project.ui.streamlitui import StreamlitUI
        StreamlitUI.track_workflow("Story")
        base_format = """
        ## 📝 User Story Format

        As a <type of user>
        I want <some goal>
        So that <some reason/benefit>

        Acceptance Criteria:
        1. Given <context>
        When <action>
        Then <expected result>

        Priority: (High/Medium/Low)
        Effort: (S/M/L)
        """
        # If there's feedback, modify the story accordingly
        if state.get("story_feedback"):
            prompt = f"""
            You are an Agile analyst refining user stories based on feedback.
            Focus on clarity, completeness, and actionable criteria.

            ## 📋 Context

            ### Current Story:
            {state.get('story')}

            ### Feedback:
            {state['story_feedback']}

            ---
            ## 🔍 Refinement Guidelines

            1. Address Feedback
            - Clarify ambiguous points
            - Add missing details
            - Improve acceptance criteria

            2. Story Structure
            {base_format}

            Note: Provide only refined user stories, no explanations.
            """
        else:
            # First-time story generation
            prompt = f"""
            You are an Agile analyst creating user stories from requirements.
            Focus on user value and clear acceptance criteria.

            ## 📋 Context

            ### Requirements:
            {state['requirements']}

            ---
            ## 🔍 Story Guidelines

            1. Essential Elements
            - User role
            - Clear goal
            - Business value
            - Testable criteria

            2. Story Structure
            {base_format}

            Note: Provide only user stories, no explanations.
            """

        # Invoke AI model to generate/refine the story
        ai_response = self.llm.invoke([HumanMessage(content=prompt)]).content
        ai_response = clean_deepseek_output(ai_response)
        print("Generated Story/n", ai_response)

        return {
            "story": ai_response,  # Store the generated/refined story
            "story_feedback": None  # Reset feedback
        }
