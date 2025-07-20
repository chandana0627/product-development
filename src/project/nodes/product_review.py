from src.project.state.state import State

class ProductReview:
    """
    Handles user feedback and determines the flow of the graph based on feedback.
    """

    @staticmethod
    def human_feedback(state: State):
        """
        Process user feedback for the story.

        Args:
            state (State): Current state containing the story and feedback.

        Returns:
            dict: Updated state with feedback.
        """
        return {
            "story": state["story"],
            "story_feedback": state.get("story_feedback")
        }

    @staticmethod
    def should_continue(state: State) -> str:
        """
        Determines whether to continue to design or go back for story refinement.

        Args:
            state (State): Current state containing the story and feedback.

        Returns:
            str: Next node to execute ('Story' for refinement or 'Design' to proceed).
        """
        # If there's feedback, go back to story generation
        if not state.get("story_feedback"):
            return "Design"

        # If there is feedback, go back to Story node
        return "Story"