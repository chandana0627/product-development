import streamlit as st
from src.project.utils.file_manager import create_project_folder
from src.project.graph.graph_builder import GraphBuilder
from src.project.state.state import State
import shutil



@st.cache_resource
def get_graph():
    builder = GraphBuilder()
    return builder.softwarelifecycle()
    
class StreamlitUI:
    def __init__(self):
        self.state = State()
        self.thread = {"configurable": {"thread_id": "my_project_session", "recursion_limit": 50}}
        self.graph = get_graph()  # correctly assigned here

    



    def initialize_session_state(self):
        if "project_name" not in st.session_state:
            st.session_state.project_name = ""
        if "project_folder" not in st.session_state:
            st.session_state.project_folder = None
        if "requirements" not in st.session_state:
            st.session_state.requirements = ""
        if "workflow_phase" not in st.session_state:
            st.session_state.workflow_phase = "initialization"
        if "story" not in st.session_state:
            st.session_state.story = None
        if "story_result" not in st.session_state:
            st.session_state.story_result = None
        if "feedback" not in st.session_state:
            st.session_state.feedback = ""
        if "feedback_submitted" not in st.session_state:
            st.session_state.feedback_submitted = False
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "story_feedback" not in st.session_state:
            st.session_state.story_feedback = None
        if "design" not in st.session_state:
            st.session_state.design = ""
        if "design_feedback" not in st.session_state:
            st.session_state.design_feedback = None
            
        # Code related states
        if "generated_code" not in st.session_state:
            st.session_state.generated_code = None
        if "code_feedback" not in st.session_state:
            st.session_state.code_feedback = None
        if "code_after_review" not in st.session_state:
            st.session_state.code_after_review = None
            
        # Security states
        if "security_feedback" not in st.session_state:
            st.session_state.security_feedback = None
        if "code_after_security" not in st.session_state:
            st.session_state.code_after_security = None
            
        # Testing states
        if "test_cases" not in st.session_state:
            st.session_state.test_cases = None
        if "test_cases_feedback" not in st.session_state:
            st.session_state.test_cases_feedback = None
        if "qa_test_feedback" not in st.session_state:
            st.session_state.qa_test_feedback = None
            
        # Deployment states
        if "generated_deployment_files" not in st.session_state:
            st.session_state.generated_deployment_files = None
            
        # Workflow tracking
        if "current_node" not in st.session_state:
            st.session_state.current_node = None
            
        # Rejection counters
        if "number_of_rejections_for_design" not in st.session_state:
            st.session_state.number_of_rejections_for_design = 0
        if "number_of_rejections_for_code" not in st.session_state:
            st.session_state.number_of_rejections_for_code = 0
        if "number_of_rejections_for_security" not in st.session_state:
            st.session_state.number_of_rejections_for_security = 0
        if "number_of_rejections_for_test_cases" not in st.session_state:
            st.session_state.number_of_rejections_for_test_cases = 0
        if "number_of_rejections_for_qa" not in st.session_state:
            st.session_state.number_of_rejections_for_qa = 0
        
        # Feedback handling states
        if "show_feedback_input" not in st.session_state:
            st.session_state.show_feedback_input = False
        if "awaiting_feedback_decision" not in st.session_state:
            st.session_state.awaiting_feedback_decision = False
        if "update_attempted" not in st.session_state:
            st.session_state.update_attempted = False

    st.title("Software Development Lifecycle")
    

    def display_ui(self):
        self.initialize_session_state()

        project_name = st.text_input("Enter Project Name:", value=st.session_state.project_name)
        requirements = st.text_area(
            "Enter Project Requirements:",
            value=st.session_state.requirements,
            height=150,
            help="Describe the requirements for your project in detail."
        )

        if st.button("Initialize Project", use_container_width=True):
            if not project_name:
                st.error("Please enter a project name.")
                return
            if not requirements:
                st.error("Please enter project requirements.")
                return
            try:
                project_folder = create_project_folder(project_name)
                st.session_state.project_name = project_name
                st.session_state.project_folder = project_folder
                st.session_state.requirements = requirements
                st.session_state.workflow_phase = "story_generation"
                st.rerun()

            except Exception as e:
                st.error(f"Error initializing project: {str(e)}")

    def handle_story_generation(self):
        with st.spinner("Generating user story..."):
            try:
                result = self.graph.invoke(
                    {
                        "requirements": st.session_state.get("requirements"),
                        "project_folder": st.session_state.get("project_folder")
                    },
                    config=self.thread
                )

                if "story" in result:
                    st.session_state.story = result["story"]
                    st.session_state.story_result = result
                    st.session_state.workflow_phase = "story_review"
                    st.subheader("Generated User Story:")
                    st.write(result["story"])
                    st.rerun()
                else:
                    st.error("Failed to generate story.")

            except Exception as e:
                st.error(f"Error generating story: {e}")

    def handle_story_review(self):
        if st.session_state.story:
            st.subheader("📜 Generated Story")
            st.write(st.session_state.story)

            if st.session_state.feedback_submitted:
                st.subheader("📝 Submitted Feedback")
                st.write(st.session_state.feedback)

            if st.session_state.awaiting_feedback_decision:
                col1, col2 = st.columns(2, gap="small")
                with col1:
                    if st.button("✅ Accept Story", use_container_width=True):
                        with st.spinner("🔄 Accepting Story..."):
                            try:
                                current_state = {
                                    "story": st.session_state.story,
                                    "story_feedback": "",
                                    "requirements": st.session_state.requirements,
                                    "project_folder": st.session_state.project_folder,
                                    "current_node": "human_feedback",
                                    "number_of_rejections_for_design": st.session_state.number_of_rejections_for_design,
                                    "number_of_rejections_for_code": st.session_state.number_of_rejections_for_code,
                                    "number_of_rejections_for_security": st.session_state.number_of_rejections_for_security,
                                    "number_of_rejections_for_test_cases": st.session_state.number_of_rejections_for_test_cases,
                                    "number_of_rejections_for_qa": st.session_state.number_of_rejections_for_qa
                                }
                                self.graph.update_state(values=current_state, config=self.thread)
                                result = self.graph.invoke(None, config=self.thread)
                                
                                # Synchronize Streamlit session state with graph state
                                self._sync_session_state_with_graph(result)
                                
                                st.session_state.feedback_submitted = False
                                st.session_state.show_feedback_input = False
                                st.session_state.awaiting_feedback_decision = False
                                st.session_state.workflow_phase = "design_review"
                                st.session_state.update_attempted = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error accepting story: {e}")
                with col2:
                    if st.button("❌ Reject & Provide Feedback", use_container_width=True):
                        st.session_state.show_feedback_input = True
                        st.session_state.awaiting_feedback_decision = False
                        st.session_state.update_attempted = False
                        # No rerun here to allow feedback input

            elif not st.session_state.show_feedback_input:
                col1, col2 = st.columns(2, gap="small")
                with col1:
                    if st.button("✅ Accept Story", use_container_width=True):
                        with st.spinner("🔄 Accepting Story..."):
                            try:
                                current_state = {
                                    "story": st.session_state.story,
                                    "story_feedback": "",
                                    "requirements": st.session_state.requirements,
                                    "project_folder": st.session_state.project_folder,
                                    "current_node": "human_feedback",
                                    "number_of_rejections_for_design": st.session_state.number_of_rejections_for_design,
                                    "number_of_rejections_for_code": st.session_state.number_of_rejections_for_code,
                                    "number_of_rejections_for_security": st.session_state.number_of_rejections_for_security,
                                    "number_of_rejections_for_test_cases": st.session_state.number_of_rejections_for_test_cases,
                                    "number_of_rejections_for_qa": st.session_state.number_of_rejections_for_qa
                                }
                                self.graph.update_state(values=current_state, config=self.thread)
                                result = self.graph.invoke(None, config=self.thread)
                                
                                # Synchronize Streamlit session state with graph state
                                self._sync_session_state_with_graph(result)
                                
                                st.session_state.feedback_submitted = False
                                st.session_state.show_feedback_input = False
                                st.session_state.awaiting_feedback_decision = False
                                st.session_state.workflow_phase = "design_review"
                                st.session_state.update_attempted = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error accepting story: {e}")
                with col2:
                    if st.button("❌ Reject & Provide Feedback", use_container_width=True):
                        st.session_state.show_feedback_input = True
                        st.session_state.awaiting_feedback_decision = False
                        st.session_state.update_attempted = False
                        # No rerun here to allow feedback input

            if st.button("⏭️ Skip Feedback & Continue", use_container_width=True):
                with st.spinner("🔄 Skipping Feedback..."):
                    try:
                        current_state = {
                            "story": st.session_state.story,
                            "story_feedback": "",
                            "requirements": st.session_state.requirements,
                            "project_folder": st.session_state.project_folder,
                            "current_node": "human_feedback",
                            "number_of_rejections_for_design": st.session_state.number_of_rejections_for_design,
                            "number_of_rejections_for_code": st.session_state.number_of_rejections_for_code,
                            "number_of_rejections_for_security": st.session_state.number_of_rejections_for_security,
                            "number_of_rejections_for_test_cases": st.session_state.number_of_rejections_for_test_cases,
                            "number_of_rejections_for_qa": st.session_state.number_of_rejections_for_qa
                        }
                        self.graph.update_state(values=current_state, config=self.thread)
                        result = self.graph.invoke(None, config=self.thread)
                        
                        # Synchronize Streamlit session state with graph state
                        self._sync_session_state_with_graph(result)
                        
                        st.session_state.feedback_submitted = False
                        st.session_state.show_feedback_input = False
                        st.session_state.awaiting_feedback_decision = False
                        st.session_state.workflow_phase = "design_review"
                        st.session_state.update_attempted = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error during feedback skip transition: {e}")

        # 3. Collect Feedback
        if st.session_state.show_feedback_input:
            feedback = st.text_area("✍️ Enter your feedback:", height=100, key="story_feedback_input")
            if st.button("Submit Feedback"):
                if feedback.strip():
                    with st.spinner("🔁 Processing Human Feedback..."):
                        try:
                            current_state = {
                                "story": st.session_state.get("story"),
                                "story_feedback": feedback,
                                "requirements": st.session_state.get("requirements"),
                                "project_folder": st.session_state.get("project_folder"),
                                "current_node": "human_feedback"
                            }
                            self.graph.update_state(values=current_state, config=self.thread)
                            result = self.graph.invoke(None, config = self.thread)
                            
                            # Synchronize Streamlit session state with graph state
                            self._sync_session_state_with_graph(result)

                            st.session_state.story = result.get("story", st.session_state.story)
                            st.session_state.feedback = feedback
                            st.session_state.feedback_submitted = True
                            st.session_state.show_feedback_input = False
                            st.session_state.awaiting_feedback_decision = True
                            st.success("📜 Story updated. Would you like to give more feedback?")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ Error processing feedback: {e}")
                else:
                    st.warning("⚠️ Please enter feedback before submitting.")

    def _sync_session_state_with_graph(self, graph_state):
        """
        Synchronize Streamlit session state with the graph state to ensure consistency.
        """
        st.session_state.story = graph_state.get("story", st.session_state.get("story"))
        st.session_state.requirements = graph_state.get("requirements", st.session_state.get("requirements"))
        st.session_state.project_folder = graph_state.get("project_folder", st.session_state.get("project_folder"))
        st.session_state.current_node = graph_state.get("current_node", st.session_state.get("current_node"))
        st.session_state.design = graph_state.get("design", st.session_state.get("design", ""))
        st.session_state.design_feedback = graph_state.get("design_feedback", st.session_state.get("design_feedback"))
        st.session_state.generated_code = graph_state.get("generated_code", st.session_state.get("generated_code"))
        st.session_state.code_feedback = graph_state.get("code_feedback", st.session_state.get("code_feedback"))
        st.session_state.code_after_review = graph_state.get("code_after_review", st.session_state.get("code_after_review"))
        st.session_state.security_feedback = graph_state.get("security_feedback", st.session_state.get("security_feedback"))
        st.session_state.code_after_security = graph_state.get("code_after_security", st.session_state.get("code_after_security"))
        st.session_state.test_cases = graph_state.get("test_cases", st.session_state.get("test_cases"))
        st.session_state.test_cases_feedback = graph_state.get("test_cases_feedback", st.session_state.get("test_cases_feedback"))
        st.session_state.qa_test_feedback = graph_state.get("qa_test_feedback", st.session_state.get("qa_test_feedback"))
        st.session_state.generated_deployment_files = graph_state.get("generated_deployment_files", st.session_state.get("generated_deployment_files"))
        
        # Synchronize rejection counters
        st.session_state.number_of_rejections_for_design = graph_state.get("number_of_rejections_for_design", st.session_state.get("number_of_rejections_for_design", 0))
        st.session_state.number_of_rejections_for_code = graph_state.get("number_of_rejections_for_code", st.session_state.get("number_of_rejections_for_code", 0))
        st.session_state.number_of_rejections_for_security = graph_state.get("number_of_rejections_for_security", st.session_state.get("number_of_rejections_for_security", 0))
        st.session_state.number_of_rejections_for_test_cases = graph_state.get("number_of_rejections_for_test_cases", st.session_state.get("number_of_rejections_for_test_cases", 0))
        st.session_state.number_of_rejections_for_qa = graph_state.get("number_of_rejections_for_qa", st.session_state.get("number_of_rejections_for_qa", 0))

    @staticmethod
    def track_workflow(node_name):
        nodes = [
            "Requirements", "Story", "human_feedback", "Design", "Design_Review",
            "Generate_Code", "Code_Review", "Code_After_Review", "Security_Review",
            "Code_After_Security", "Write_Test_Cases", "Test_Cases_Review",
            "QA_Testing", "Code_After_QA", "Deployment"
        ]
        st.sidebar.subheader("🔄 Workflow Progress")
        for node in nodes:
            if node == node_name:
                st.sidebar.markdown(f"<span style='color: #00ff00; font-weight: bold;'>▶️ {node}</span>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f"<span style='color: #808080;'>⭕ {node}</span>", unsafe_allow_html=True)
        