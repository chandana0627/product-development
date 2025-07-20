import streamlit as st
from src.project.ui.streamlitui import StreamlitUI


def main():
    """Main function to run the Streamlit UI and workflow"""
    # Initialize the UI
    ui = StreamlitUI()
    ui.initialize_session_state()
 

    current_node = st.session_state.get("workflow_phase", "initialization")

    if current_node == "initialization":
        user_input = ui.display_ui()
        ui.track_workflow("Requirements")
        if user_input:
            # set a flag for next rerun
            st.session_state.initialized = True
            st.rerun()  # Force rerun after setting session state

    elif current_node == "story_generation":
        ui.handle_story_generation()
        if st.session_state.get("story"):
            st.session_state.workflow_phase = "story_review"
            st.rerun()

    elif current_node == "story_review":
        ui.handle_story_review()
        ui.track_workflow("human_feedback")
        
        
    
        
        
    # elif current_node == "Deployment":
    #     ui.download_project()
        

    
if __name__ == "__main__":
    main()
