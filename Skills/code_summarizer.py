from Core.skill import Skill


class Code_summarizer(Skill):
    """"""
    def describe(self):
        return "Code summarizer skill"


        import os
        from openai import OpenAI

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        async def summarize_file(file_path: str) -> str:
            if not os.path.exists(file_path):
                return f"[Summarizer] File not found: {file_path}"

            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            prompt = (
                "You are a professional software engineer. Summarize the following Python code:"
                f"\n\n{source_code}\n\nReply with a short explanation of what it does."
            )

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a code summarization expert."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content.strip()

        def register():
            return { "summarize": summarize_file }
def handle(self, user_input, context):
        """Summarizes uploaded code or text files available to LP1."""
        if "context" in context and "file" in context["context"]:
            code = context["context"]["file"]
            return f"Summary of file:\n(Stub) This appears to be {len(code.splitlines())} lines of code."
        return "No code provided to summarize."