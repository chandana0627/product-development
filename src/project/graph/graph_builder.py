import os
from typing import TypedDict, List
from langgraph.graph import StateGraph, END, START
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from src.project.nodes.stories import Story
from src.project.state.state import State
from src.project.nodes.product_review import ProductReview
from src.project.nodes.design import Design
from src.project.LLMS.model import GroqLLM
from langgraph.checkpoint.memory import MemorySaver
from src.project.nodes.design_review import DesignReview
from src.project.nodes.generate_code import GenerateCode
from src.project.nodes.design_review import DesignReview
from src.project.nodes.code_review import CodeReview
from src.project.nodes.code_after_review import CodeAfterReview
from src.project.nodes.security_review import SecurityReview
from src.project.nodes.code_after_security import CodeAfterSecurity
from src.project.nodes.write_test_cases import WriteTestCases
from src.project.nodes.test_cases_review import TestCasesReview
from src.project.nodes.qa_testing import QATesting
from src.project.nodes.code_after_qa import CodeAfterQA
from src.project.nodes.deployment import DeployApplication




class GraphBuilder:

    def __init__(self):
        self.graph_builder=StateGraph(State)        
        self.load_llm = GroqLLM()
        self.memory = MemorySaver()
        
    def softwarelifecycle(self):
        """
        Builds a software life cycle graph using LangGraph.
        """
        self.story_node=Story(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Story",self.story_node.generate_story)
        self.graph_builder.add_node("human_feedback", ProductReview.human_feedback)
        self.design_node=Design(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Design",self.design_node.build_design)
        self.design_review_node = DesignReview(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Design_Review", self.design_review_node.review_design)
        self.generate_code_node = GenerateCode(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Generate_Code", self.generate_code_node.generate_code)
        self.code_review_node = CodeReview(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Code_Review", self.code_review_node.review_code)
        self.code_after_review_node = CodeAfterReview(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Code_After_Review", self.code_after_review_node.regenerate_code)
        self.security_review_node = SecurityReview(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Security_Review", self.security_review_node.security_review)
        self.code_after_security_node = CodeAfterSecurity(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Code_After_Security", self.code_after_security_node.regenerate_secure_code)
        self.write_test_cases_node = WriteTestCases(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Write_Test_Cases", self.write_test_cases_node.test_cases)
        self.test_cases_review_node = TestCasesReview(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("Test_Cases_Review", self.test_cases_review_node.review_test_cases)
        self.qa_testing_node = QATesting(self.load_llm.get_openai_reason())
        self.graph_builder.add_node("QA_Testing", self.qa_testing_node.review_test_cases)
        self.code_after_qa_node = CodeAfterQA(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Code_After_QA", self.code_after_qa_node.regenerate_test_cases)
        self.deploy_application_node = DeployApplication(self.load_llm.get_openai_code())
        self.graph_builder.add_node("Deployment", self.deploy_application_node.generate_deployment_files)
        self.graph_builder.add_edge(START,"Story")
        self.graph_builder.add_edge("Story", "human_feedback")
        self.graph_builder.add_conditional_edges("human_feedback", ProductReview.should_continue, ["Story", "Design"])
        self.graph_builder.add_edge("Design", "Design_Review")
        self.graph_builder.add_conditional_edges("Design_Review", DesignReview.should_continue, ["Design", "Generate_Code"])
        self.graph_builder.add_edge("Generate_Code", "Code_Review")
        self.graph_builder.add_conditional_edges("Code_Review", CodeReview.should_continue, ["Code_After_Review", "Security_Review"])
        self.graph_builder.add_edge("Code_After_Review", "Code_Review")
        self.graph_builder.add_conditional_edges("Security_Review", SecurityReview.should_continue, ["Code_After_Security", "Write_Test_Cases"])
        self.graph_builder.add_edge("Code_After_Security", "Code_Review")
        self.graph_builder.add_edge("Write_Test_Cases", "Test_Cases_Review")
        self.graph_builder.add_conditional_edges("Test_Cases_Review", TestCasesReview.should_continue, ["Write_Test_Cases", "QA_Testing"])
        self.graph_builder.add_conditional_edges("QA_Testing", QATesting.should_continue, ["Code_After_QA", "Deployment"])
        self.graph_builder.add_edge("Code_After_QA", "Code_Review")
        self.graph_builder.add_edge("Deployment", "Generate_Code")
        
        
        
        return self.graph_builder.compile(
            interrupt_after=["Story"], # Removed interrupt_after to allow continuous execution
            checkpointer=self.memory
        )
