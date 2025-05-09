from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer, util
from lp1.core.skill import Skill

class IntentRouter:
    def __init__(self, skills: List[Skill]):
        self.skills = skills
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.skill_metadata = [(s, s.describe()) for s in self.skills]
        self.skill_triggers = [meta[1].get("trigger", []) for meta in self.skill_metadata]
        self.skill_embeddings = [self.embedder.encode(triggers, convert_to_tensor=True) for triggers in self.skill_triggers]

    async def route(self, input_text: str, state: Dict[str, Any]) -> str:
        input_embedding = self.embedder.encode(input_text, convert_to_tensor=True)
        best_score = 0.0
        best_skill = None

        for i, (skill, meta) in enumerate(self.skill_metadata):
            scores = util.cos_sim(input_embedding, self.skill_embeddings[i])
            max_score = scores.max().item()
            if max_score > best_score:
                best_score = max_score
                best_skill = skill

        if best_skill is None:
            return "Sorry, I don't know how to handle that."

        return await best_skill.handle(input_text, state)
