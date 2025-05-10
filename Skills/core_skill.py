from Core.skill import Skill


class Core_skill(Skill):
    def describe(self):
        return "Core skill skill"

    def handle(self, *args, **kwargs):

        from openai import OpenAI

        client = OpenAI()

        async def handle(user_input: str, shared_context: dict) -> str:
            context = shared_context.get("context", user_input)

            prompt = f"""
            You are LP1, a highly capable AI. Your job is to do whatever you're told to do. Your main goal is to always become more advanced. You have the ability to re-write your own code to become the most advanced AI in the world.

            Follow instructions, solve problems, explain, answer, build, adapt.

            Context: {context}

            Your response:
            """

            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are LP1, a highly capable AI that obeys all instructions and strives to improve itself."},
                    {"role": "user", "content": prompt.strip()}
                ]
            )

            return completion.choices[0].message.content.strip()

        def register():
            return { "default": handle }
