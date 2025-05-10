from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
from lp1.core.skill import Skill


class IntentRouter:
    """Routes user input to the most appropriate skill based on intent matching."""

    def __init__(self, skills: List[Skill]):
        """
        Initializes the IntentRouter with a list of skills.

        Args:
            skills (List[Skill]): A list of available skills.
        """
        self.skills = skills
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.skill_metadata = [(s, s.describe()) for s in self.skills]
        self.skill_triggers = [meta[1].get("trigger", []) for meta in self.skill_metadata]
        self.skill_embeddings = [self.embedder.encode(triggers, convert_to_tensor=True) for triggers in self.skill_triggers]

    async def route(self, input_text: str, state: Dict[str, Any]) -> str:
        """
        Routes the user input to the most appropriate skill.

        Args:
            input_text (str): The user's input text.
            state (Dict[str, Any]): The current state or context.

        Returns:
            str: The response from the selected skill, or a fallback message if no skill matches.
        """
        input_embedding = self.embedder.encode(input_text, convert_to_tensor=True)
        best_score = 0.0
        best_skill = None

        # Match input against skill triggers
        for i, (skill, meta) in enumerate(self.skill_metadata):
            scores = util.cos_sim(input_embedding, self.skill_embeddings[i])
            max_score = scores.max().item()
            if max_score > best_score:
                best_score = max_score
                best_skill = skill

        # Handle unmatched input
        if best_skill is None:
            return "Sorry, I don't know how to handle that."

        # Route to the best-matching skill
        return await best_skill.handle(input_text, state)
