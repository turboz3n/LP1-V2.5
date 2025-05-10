from Core.skill import Skill 
from duckduckgo_search import DDGS

class Skill(Skill): """Searches the internet for information using natural language queries."""
    def handle(self, user_input, context):
    # Extract topic from user input
    topic = user_input.lower().replace("search", "").replace("look up", "").replace("find", "").strip()

    if not topic:
        return "What would you like me to search for?"

    # Perform the search
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(topic, max_results=3):
                results.append(f"{r['title']}\n{r['href']}\n")

        return "\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Search failed: {e}"

