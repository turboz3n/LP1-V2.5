from Core.skill import Skill
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re
import os
import json
from datetime import datetime
import random
import string
import nltk
from nltk.corpus import words
nltk.download('words')


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
            print(f"Detected URL: {user_input}")  # Debug statement
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
        """Generates meaningful random topics for autonomous browsing using nltk."""
        try:
            # Load existing knowledge
            with open(self.knowledge_base_path, "r") as f:
                knowledge = json.load(f)

            # Extract existing topics from the knowledge base
            existing_topics = {entry["topic"] for entry in knowledge}

            # Use the NLTK words corpus to generate random topics
            word_list = words.words()

            # Generate random topics by combining real words
            def generate_random_topic():
                word_count = random.randint(1, 3)  # Randomly choose 1 to 3 words
                return " ".join(random.choices(word_list, k=word_count))

            # Generate a list of random topics
            random_topics = [generate_random_topic() for _ in range(10)]

            # Filter out topics already in the knowledge base
            new_topics = [topic for topic in random_topics if topic not in existing_topics]

            # Limit the number of new topics to avoid overloading
            return new_topics[:5]  # Fetch up to 5 new topics
        except Exception as e:
            print(f"Error expanding topics: {e}")
            return [f"random_topic_{random.randint(1, 1000)}"]  # Default fallback topic

    def search(self, topic):
        """Performs a web search and returns a list of URLs."""
        try:
            print(f"Performing search for topic: {topic}")  # Debug statement
            res = requests.get(f"https://html.duckduckgo.com/html/?q={topic}", headers=self.headers, timeout=10)
            links = list(set(
                re.findall(r'<a rel="nofollow" class="result__a" href="(https://[^"]+)', res.text)
            ))[:3]  # Limit to top 3 results

            if not links:
                print(f"No search results found for topic: {topic}")  # Debug statement

            return links
        except requests.exceptions.Timeout:
            print(f"Search timed out for topic: {topic}")
            return []
        except Exception as e:
            print(f"Search failed for topic '{topic}': {e}")
            return []

    def summarize_url(self, url):
        """Fetches and summarizes content from a URL."""
        try:
            print(f"Fetching content from URL: {url}")  # Debug statement
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, timeout=10, headers=headers)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            html = response.text

            # Parse the HTML content
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text("\n")
            short_text = "\n".join(text.split("\n")[:80])  # Limit to the first 80 lines

            # Summarize with OpenAI
            prompt = f"Summarize this for a beginner:\n{text[:2000]}"  # Limit input to 2000 characters
            summary = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ]
            ).choices[0].message.content.strip()

            return summary
        except requests.exceptions.Timeout:
            print(f"Fetching URL timed out: {url}")
            return f"Sorry, I couldn't fetch the content from the URL due to a timeout."
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL '{url}': {e}")
            return f"Sorry, I couldn't fetch the content from the URL: {e}"
        except Exception as e:
            print(f"Error summarizing URL '{url}': {e}")
            return f"Sorry, I couldn't summarize the URL due to an error: {e}"

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
        url_pattern = re.compile(
            r'^(https?://)?'  # http:// or https:// (optional)
            r'([a-zA-Z0-9.-]+)'  # Domain name
            r'(\.[a-zA-Z]{2,})'  # Top-level domain
            r'(/[a-zA-Z0-9._~:/?#@!$&\'()*+,;=%-]*)?$'  # Path (optional)
        )
        return bool(url_pattern.match(text))
