from Core.skill import Skill
from typing import Dict, Any
from transformers import pipeline

class AdvancedLearningSkill(Skill):
    def __init__(self):
        self.qa_pipeline = None  # Lazy initialization

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "advanced_learning",
            "trigger": ["how", "why", "what is", "explain"],
            "description": "Handles advanced learning queries using a question-answering pipeline."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handles advanced learning queries using a QA pipeline."""
        if self.qa_pipeline is None:
            self.qa_pipeline = pipeline("question-answering")

        context_text = context.get("context", "")
        if not context_text:
            return "Please provide context to answer from."

        try:
            result = self.qa_pipeline({"question": user_input, "context": context_text})
            return f"Answer: {result['answer']} (score: {result['score']:.2f})"
        except Exception as e:
            return "An error occurred while processing your query. Please try again later."
