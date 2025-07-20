import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEndpoint
from langchain_community.llms import HuggingFaceHub
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
load_dotenv()

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

class GroqLLM:
    def get_groq_deep(self):
        try:
            llm = ChatGroq(model='gemma2-9b-it')
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
    
    def get_groq_quen(self):
        try:
            llm = ChatGroq(model='qwen-qwq-32b')
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
    
    def get_hf_codellam(self):
        try:
            # Use the InferenceClient with the appropriate task method
            llm = HuggingFaceHub(
            repo_id="mistralai/Mistral-7B-Instruct",
            model_kwargs={"temperature": 0.2, "max_length": 500}
        )
            return llm
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        
        
    def get_groq_quenc(self):
        try:
            llm = ChatGroq(model='meta-llama/llama-4-maverick-17b-128e-instruct')
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
        
        
    def get_openai_reason(self):
        try:
            llm = ChatOpenAI(model="o3-mini-2025-01-31")
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
    
    
    def get_openai_code(self):
        try:
            llm = ChatOpenAI(model="chatgpt-4o-latest", temperature=0.2)
        except Exception as e:
            raise ValueError(f"Error Occurred with Exception : {e}")
        return llm
