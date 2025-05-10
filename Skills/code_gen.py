from Core.skill import Skill
import openai
import os
from typing import Dict, Any


class CodeGenSkill(Skill):
    """Skill for generating Python code based on user descriptions."""

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "code_gen",
            "trigger": ["generate code", "write code", "code"],
            "description": "Generates Python code based on user descriptions."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generates Python code based on a user description."""
        try:
            prompt = f"Generate Python code for the following request:\n{user_input}"
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful and knowledgeable AI assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating code: {e}"
