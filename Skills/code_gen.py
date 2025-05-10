from Core.skill import Skill
import openai
import os
from typing import Dict, Any


class CodeGenSkill(Skill):
    """Skill for generating Python code based on user descriptions."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is not set. Please configure the 'OPENAI_API_KEY' environment variable.")
        openai.api_key = self.api_key

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "code_gen",
            "trigger": ["generate code", "write code", "code"],
            "description": "Generates Python code based on user descriptions."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generates Python code based on a user description."""
        if not user_input.strip():
            return "Please provide a description of the code you want to generate."

        try:
            prompt = f"Generate Python code for the following request:\n{user_input}"
            response = openai.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful and knowledgeable AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"An error occurred while generating code: {e}"
