#/Skills/knowledge_ingestor.py

import requests
import re
import os
import json
from sentence_transformers import SentenceTransformer
import numpy as np

WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
STORE_PATH = "LP1-V2.5/memory/knowledge_store.json"
EMBEDDINGS_PATH = "LP1-V2.5/memory/knowledge_vectors.npy"

def fetch_wikipedia_summary(topic: str) -> str:
    response = requests.get(WIKI_API + topic.replace(" ", "_"))
    if response.status_code == 200:
        return response.json().get("extract", "")
    return ""

def clean_text(text: str) -> list:
    sentences = re.split(r'[.!?]\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 10]

def save_knowledge(topic: str, sentences: list, vectors: np.ndarray):
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

def learn_topic(topic: str) -> str:
    summary = fetch_wikipedia_summary(topic)
    if not summary:
        return f"No reliable information found on '{topic}'."

    sentences = clean_text(summary)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(sentences)

    save_knowledge(topic, sentences, vectors)
    return f"Learned about {topic}: {len(sentences)} knowledge units stored."

# Optional standalone test
if __name__ == "__main__":
    topic = input("Topic to learn: ")
    print(learn_topic(topic))

