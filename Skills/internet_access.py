from Core.skill import Skill
import requests

class Skill(Skill):
    """Performs a web search by fetching content from the internet using HTTPS."""

    def handle(self, user_input, context):
        if not user_input.startswith("fetch "):
            return "To use this skill, say: fetch <URL>"

        url = user_input.replace("fetch", "", 1).strip()
        if not url.startswith("https://"):
            return "Only HTTPS URLs are allowed for safety."

        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return f"Fetched content preview:\n{response.text[:500]}..."
            else:
                return f"Error {response.status_code}: Could not fetch content."
        except Exception as e:
            return f"Error: {e}"
