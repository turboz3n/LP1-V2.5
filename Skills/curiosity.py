from Core.skill import Skill


class Curiosity(Skill):
    """"""
    def describe(self):
        return "Curiosity skill"


        from lp1.core.skill import Skill
        from typing import Dict, Any
        from openai import OpenAI

        client = OpenAI()

        class CuriositySkill(Skill):
            def describe(self) -> Dict[str, Any]:
                return {
                    "name": "curiosity",
                    "trigger": ["explore", "unknown", "ask a question", "learn", "curious"]
                }

            async def handle(self, input_text: str, state: Dict[str, Any]) -> str:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You're an AI explorer. Help the user understand or expand ideas."},
                        {"role": "user", "content": input_text}
                    ]
                )
                return response.choices[0].message.content.strip()
def handle(self, user_input, context):
        """Generates thought-provoking follow-up questions based on the conversation."""
        return "Why do you think that is? What would change if you looked at it from a different perspective?"
