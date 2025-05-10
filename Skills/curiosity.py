from Core.skill import Skill
from typing import Dict, Any
import openai
import os


class CuriositySkill(Skill):
    """Skill for exploring ideas and generating thought-provoking questions."""

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "curiosity",
            "trigger": ["explore", "unknown", "ask a question", "learn", "curious"],
            "description": "Explores ideas and generates thought-provoking follow-up questions."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Generates thought-provoking follow-up questions based on the conversation."""
        try:
            prompt = f"""
            You are an AI explorer. Help the user understand or expand ideas by asking thought-provoking questions.
            User input: {user_input}
            """

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You're an AI explorer. Help the user understand or expand ideas."},
                    {"role": "user", "content": prompt.strip()}
                ]
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error in curiosity skill: {e}"
