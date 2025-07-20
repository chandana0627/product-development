from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    """
    Represents the structure of the state used in the graph.
    """
    requirements: str # User's requirements
    messages: List[HumanMessage]  # Track AI-generated messages
    story: Optional[str]  # Store the generated user story
    story_feedback: Optional[str]  # User's feedback for improvements
    design: str
    design_feedback: Optional[str]
    project_folder: Optional[str]
    generated_code: Optional[Dict[str, str]]
    code_feedback: Optional[str]
    code_after_review: Optional[Dict[str, str]]
    security_feedback: Optional[str]
    code_after_security: Optional[Dict[str, str]]
    test_cases: Optional[Dict[str, Any]]
    test_cases_feedback: Optional[str]
    qa_test_feedback: Optional[str]
    generated_deployment_files: Optional[Dict[str, str]]
    current_node: Optional[str]
    number_of_rejections_for_design: int
    number_of_rejections_for_code: int
    number_of_rejections_for_security: int
    number_of_rejections_for_test_cases: int
    number_of_rejections_for_qa: int
