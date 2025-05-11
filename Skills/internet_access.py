from Core.skill import Skill
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import os
import json
from datetime import datetime


class InternetAccessSkill(Skill):
    """Skill for searching, retrieving, and summarizing live web content."""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.knowledge_base_path = "knowledge_base.json"

        # Initialize the knowledge base if it doesn't exist
        if not os.path.exists(self.knowledge_base_path):
            with open(self.knowledge_base_path, "w") as f:
                json.dump([], f)

    def describe(self):
        return {
            "name": "internet_access",
            "trigger": ["search", "learn about", "look up", "internet"],
            "description": "Searches the internet, retrieves content, and summarizes it for the user."
        }

    def handle(self, user_input, context):
        """Handles internet-related tasks based on the user's query."""
        # Step 1: Check if the input is a URL
        if self.is_url(user_input):
            return self.summarize_url(user_input)

        # Step 2: Dynamically expand topics
        topics = self.expand_topics()

        # Step 3: Search and summarize for each topic
        knowledge = []
        for topic in topics:
            print(f"Searching for: {topic}")
            search_results = self.search(topic)
            for result in search_results:
                summary = self.summarize_url(result)
                if summary:
                    knowledge.append({
                        "topic": topic,
                        "url": result,
                        "summary": summary,
                        "timestamp": datetime.now().isoformat()
                    })

        # Step 4: Store knowledge in the knowledge base
        self.store_knowledge(knowledge)

        return f"Successfully gathered and stored knowledge on {len(topics)} topics."

    def expand_topics(self):
        """Dynamically expands the topics list based on knowledge gaps or trends."""
        try:
            # Load existing knowledge
            with open(self.knowledge_base_path, "r") as f:
                knowledge = json.load(f)

            # Analyze knowledge to find gaps or trends
            existing_topics = {entry["topic"] for entry in knowledge}
            new_topics = []

            # Example: Add trending topics (hardcoded for now, but could be fetched dynamically)
            trending_topics = ["blockchain", "renewable energy", "space exploration"]
            for topic in trending_topics:
                if topic not in existing_topics:
                    new_topics.append(topic)

            return list(existing_topics) + new_topics
        except Exception as e:
            print(f"Error expanding topics: {e}")
            return ["artificial intelligence", "machine learning"]  # Default topics

    def search(self, topic):
        """Performs a web search and returns a list of URLs."""
        try:
            res = requests.get(f"https://html.duckduckgo.com/html/?q={topic}", headers=self.headers)
            links = list(set(
                re.findall(r'<a rel="nofollow" class="result__a" href="(https://[^"]+)', res.text)
            ))[:3]  # Limit to top 3 results
            return links
        except Exception as e:
            print(f"Search failed for topic '{topic}': {e}")
            return []

    def summarize_url(self, url):
        """Fetches and summarizes content from a URL."""
        try:
            html = requests.get(url, timeout=10, headers=self.headers).text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text("\n")
            short_text = "\n".join(text.split("\n")[:80])

            # Summarize with OpenAI
            prompt = f"Summarize this for a beginner:\n{text[:2000]}"
            summary = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            ).choices[0].message.content.strip()

            return summary
        except Exception as e:
            print(f"Error summarizing URL '{url}': {e}")
            return None

    def store_knowledge(self, knowledge):
        """Stores gathered knowledge in the knowledge base."""
        try:
            with open(self.knowledge_base_path, "r+") as f:
                existing_knowledge = json.load(f)
                existing_knowledge.extend(knowledge)
                f.seek(0)
                json.dump(existing_knowledge, f, indent=2)
        except Exception as e:
            print(f"Error storing knowledge: {e}")

    def is_url(self, text):
        """Checks if the input is a valid URL."""
        return text.startswith("http://") or text.startswith("https://")
