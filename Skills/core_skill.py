from Core.skill import Skill
from typing import Dict, Any
import openai
import os


class CoreSkill(Skill):
    """Core skill for handling general reasoning and fallback responses."""

    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "core_skill",
            "trigger": ["default", "fallback", "reasoning"],
            "description": "Handles core reasoning tasks or fallback responses when no other skill matches."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Provides core reasoning or fallback responses."""
        try:
            context_text = context.get("context", user_input)

            prompt = f"""
            You are LP1, a highly capable AI. Your job is to follow instructions, solve problems, explain, answer, build, and adapt. 
            Your main goal is to always become more advanced and helpful.

            Context: {context_text}

            Your response:
            """

            response = openai.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are LP1, a highly capable AI that obeys all instructions and strives to improve itself."},
                    {"role": "user", "content": prompt.strip()}
                ]
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error in core reasoning: {e}"
