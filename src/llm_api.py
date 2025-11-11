import openai
from openai import OpenAI
import requests
from typing import List

class LLMClient:
    def __init__(self,**kwargs):
        rag_used=kwargs["rag_used"]
        rag_is_available=None
        pass
    def _build_prompt(self,question:str,documents:List[str])->str:
        # 结合RAG构建提示词
        pass
    def generate_answer(self,question:str) -> str:
        # 调用API回答问题
        pass
    
if __name__=="__main__":
    llm=LLMClient()