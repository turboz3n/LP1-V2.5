from lp1.core.skill import Skill
from lp1.core.memory import recall_recent
from typing import Dict, Any
from openai import OpenAI

client = OpenAI()

class MetaReasonerSkill(Skill):
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "meta_reasoner",
            "trigger": ["why did you fail", "analyze", "what went wrong", "reflect"]
        }

    async def handle(self, input_text: str, state: Dict[str, Any]) -> str:
        history = recall_recent(5)
        prompt = "Reflect on these past LP1 interactions. Identify errors, missed opportunities, or improvement ideas:\n\n"
        for h in history:
            prompt += f"User: {h['input']}\nLP1: {h['response']} (via {h['skill']})\n\n"
        prompt += "\nGive diagnostics and suggestions."

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're an introspective AI agent that audits your own performance."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content.strip()
