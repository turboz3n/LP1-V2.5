from Core.skill import Skill
import os
from typing import Dict, Any
from openai import OpenAI  # Import the OpenAI class


class CodeSummarizerSkill(Skill):
    """Skill for summarizing Python code files."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "code_summarizer",
            "trigger": ["summarize code", "code summary", "summarize"],
            "description": "Summarizes Python code files by providing a concise explanation of their functionality."
        }

    def summarize_file(self, file_path: str) -> str:
        """Summarizes the content of a Python file."""
        if not os.path.exists(file_path):
            return f"[Summarizer] File not found: {file_path}"

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            prompt = (
                "You are a professional software engineer. Summarize the following Python code:"
                f"\n\n{source_code}\n\nReply with a short explanation of what it does."
            )

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a code summarization expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Summarizer Error] {e}"

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handles user requests to summarize code."""
        file_path = context.get("file_path")
        if file_path:
            return self.summarize_file(file_path)
        return "No file path provided for summarization."
