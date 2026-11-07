from typing import Dict, List, Optional
from ai_team.llm import LLMClient

class BaseAgent:
    def __init__(self, name: str, role: str, system_prompt: str, model: Optional[str] = None):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.client = LLMClient(model=model)

    def think_and_act(self, prompt: str, context: Optional[str] = None) -> str:
        messages = []
        if context:
            messages.append({"role": "user", "content": f"Bối cảnh & Dữ liệu đầu vào:\n{context}"})
        messages.append({"role": "user", "content": prompt})
        
        return self.client.generate(messages, system_prompt=self.system_prompt)
