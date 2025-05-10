from Core.skill import Skill
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import re

class Skill(Skill):
    """Learns from the internet by searching, retrieving, and summarizing live web content."""

    def handle(self, user_input, context):
        client = OpenAI()

        # Step 1: Extract query topic
        topic = user_input.lower().replace("search", "").replace("learn about", "").replace("look up", "").strip()
        if not topic:
            return "What topic should I research?"

        # Step 2: Search via DuckDuckGo HTML
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            res = requests.get(f"https://html.duckduckgo.com/html/?q={topic}", headers=headers)
            links = list(set(
                re.findall(r'<a rel="nofollow" class="result__a" href="(https://[^"]+)', res.text)
            ))[:3]  # top 3
        except Exception as e:
            return f"Search failed: {e}"

        # Step 3: Fetch and clean each page
        summaries = []
        for url in links:
            try:
                html = requests.get(url, timeout=6, headers=headers).text
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text("\n")
                short_text = "\n".join(text.split("\n")[:80])

                # Step 4: Summarize with OpenAI
                prompt = f"Summarize this for a beginner:\n{text[:2000]}"
                summary = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ]
                ).choices[0].message.content

                summaries.append(f"**{url}**\n{summary.strip()}\n")
            except Exception as e:
                summaries.append(f"**{url}**\nError fetching/summarizing: {e}\n")

        return "\n\n".join(summaries) if summaries else "No usable content found."

module_name = __name__
