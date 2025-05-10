from Core.skill import Skill
from Core.memory import recall_recent
from typing import Dict, Any
from openai import OpenAI  # Import the OpenAI class
import os


class MetaReasonerSkill(Skill):
    """Skill for introspection and analyzing LP1's past interactions to identify improvements."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "meta_reasoner",
            "trigger": ["why did you fail", "analyze", "what went wrong", "reflect"],
            "description": "Analyzes past interactions to identify errors, missed opportunities, or improvement ideas."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Reflects on past interactions and provides diagnostics and suggestions."""
        try:
            # Retrieve recent interaction history
            history = recall_recent(5)
            if not history:
                return "No recent interactions to analyze."

            # Build the prompt for introspection
            prompt = "Reflect on these past LP1 interactions. Identify errors, missed opportunities, or improvement ideas:\n\n"
            for h in history:
                prompt += f"User: {h['input']}\nLP1: {h['response']} (via {h['skill']})\n\n"
            prompt += "\nProvide diagnostics and suggestions for improvement."

            # Use OpenAI to generate the analysis
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an introspective AI agent that audits your own performance."},
                    {"role": "user", "content": prompt.strip()}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error in meta-reasoner skill: {e}"
