from lp1.core.skill import Skill
from typing import Dict, Any
import requests

class InternetAccessSkill(Skill):
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "internet_access",
            "trigger": ["fetch", "http", "get", "download", "scrape"]
        }

    async def handle(self, input_text: str, state: Dict[str, Any]) -> str:
        if not input_text.startswith("fetch "):
            return "To use this skill, say: fetch <URL>"

        url = input_text.replace("fetch", "", 1).strip()
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
