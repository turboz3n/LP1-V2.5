from Core.skill import Skill
import requests
import re
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import Dict, Any

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
STORE_PATH = "LP1-V2.5/memory/knowledge_store.json"
EMBEDDINGS_PATH = "LP1-V2.5/memory/knowledge_vectors.npy"


class KnowledgeIngestorSkill(Skill):
    """Skill for ingesting structured knowledge or domain content for internal reference."""

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "knowledge_ingestor",
            "trigger": ["learn", "ingest knowledge", "study topic", "knowledge"],
            "description": "Ingests structured knowledge or domain content for internal reference."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Ingests structured knowledge or domain content for internal reference."""
        topic = user_input.lower().replace("learn about", "").strip()
        if not topic:
            return "Please specify a topic to learn about."

        return self.learn_topic(topic)

    def fetch_wikipedia_summary(self, topic: str) -> str:
        """Fetches a summary of a topic from Wikipedia."""
        response = requests.get(WIKI_API + topic.replace(" ", "_"))
        if response.status_code == 200:
            return response.json().get("extract", "")
        return ""

    def clean_text(self, text: str) -> list:
        """Cleans and splits text into sentences."""
        sentences = re.split(r'[.!?]\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def save_knowledge(self, topic: str, sentences: list, vectors: np.ndarray):
        """Saves knowledge and embeddings to disk."""
        os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
        if os.path.exists(STORE_PATH):
            with open(STORE_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}
        data[topic] = sentences
        with open(STORE_PATH, "w") as f:
            json.dump(data, f, indent=2)
        np.save(EMBEDDINGS_PATH, vectors)

    def learn_topic(self, topic: str) -> str:
        """Learns about a topic by fetching and processing its summary."""
        summary = self.fetch_wikipedia_summary(topic)
        if not summary:
            return f"No reliable information found on '{topic}'."

        sentences = self.clean_text(summary)
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vectors = model.encode(sentences)

        self.save_knowledge(topic, sentences, vectors)
        return f"Learned about {topic}: {len(sentences)} knowledge units stored."
