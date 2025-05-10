from dotenv import load_dotenv
load_dotenv()
from Core.memory import Memory
import re
import json
import os
import requests  # For internet access
from Core.skill_loader import load_skills
from Core.ethics_enforcer import safe_completion
from openai import OpenAI  # Import the OpenAI class
from Skills import knowledge_ingestor

class Brain:
    def __init__(self):
        self.skills = load_skills()
        self.context = []
        self.session_context = []
        self.memory = Memory()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Initialize the OpenAI client
        self.goal_store = "goals.json"
        self.chat_mode = False  # Track whether LP1 is in chat mode
        self.pending_skill_creation = None  # Track pending skill creation
        if not os.path.exists(self.goal_store):
            with open(self.goal_store, "w") as f:
                json.dump([], f)

        # Generate dynamic alias mapping
        self.skill_aliases = self.generate_alias_mapping()

        # Validate loaded skills
        self.validate_skills()

    def validate_skills(self):
        """Ensure all loaded skills implement the required methods."""
        invalid_skills = []
        for skill_name, skill_obj in self.skills.items():
            if not hasattr(skill_obj, 'handle') or not callable(skill_obj.handle):
                print(f"[Error] Skill '{skill_name}' is invalid: Missing 'handle' method.")
                invalid_skills.append(skill_name)
            elif not hasattr(skill_obj, 'describe') or not callable(skill_obj.describe):
                print(f"[Error] Skill '{skill_name}' is invalid: Missing 'describe' method.")
                invalid_skills.append(skill_name)
        for skill_name in invalid_skills:
            del self.skills[skill_name]

    def generate_alias_mapping(self):
        """Dynamically generate alias mappings from skill descriptions."""
        aliases = {}
        for skill_name, skill_obj in self.skills.items():
            description = skill_obj.describe()
            if "trigger" in description:
                for alias in description["trigger"]:
                    normalized_alias = alias.lower().replace(" ", "_").replace("-", "_")
                    aliases[normalized_alias] = skill_name
        print(f"[LP1] Generated alias mapping: {aliases}")
        return aliases

    def classify_directive(self, text: str) -> dict:
        prompt = f"""
        You are LP1, an advanced AI assistant. Given this user input, classify it as one of the following:
        - goal → user wants to set a long-term objective (e.g., "Learn about neural networks").
        - rule → user is defining behavioral boundaries (e.g., "Never share personal data").
        - trigger_skill → user is asking for an action or task to be performed (e.g., "Improve your knowledge on neural networks").
        - chat → general conversation (e.g., "How are you?").

        Respond ONLY with a JSON object containing:
        - intent: One of "goal", "rule", "trigger_skill", or "chat".
        - priority: One of "low", "medium", or "high".
        - action: A concise description of the action (e.g., "learn_topic", "update_knowledgebase", "respond").
        - source: Either "user" (if the task is user-directed) or "self" (if the task is self-directed).

        Input: {text}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You classify user directives."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Access the message content correctly
            print("[Classifier raw output]", response.choices[0].message.content)
            classification = json.loads(response.choices[0].message.content)
            return classification
        except Exception as e:
            print(f"[Directive Classifier Error] {e}")
            return {"intent": "chat", "priority": "low", "action": "respond", "source": "user"}

    def summarize_skills(self):
        """
        Summarizes all loaded skills and their descriptions.
        """
        if not self.skills:
            return "I currently have no skills loaded."

        skill_descriptions = []
        for skill_name, skill_obj in self.skills.items():
            if hasattr(skill_obj, "describe") and callable(skill_obj.describe):
                description = skill_obj.describe()
                skill_descriptions.append(f"- {skill_name}: {description.get('description', 'No description available.')}")
            else:
                skill_descriptions.append(f"- {skill_name}: No description available.")

        return "Here are my current skills and their descriptions:\n" + "\n".join(skill_descriptions)

    def describe_capabilities(self):
        """
        Returns a high-level description of LP1's capabilities.
        """
        return (
            "I am LP1, an advanced AI assistant. Here are my main capabilities:\n"
            "- I can execute predefined skills, such as summarizing code or analyzing data.\n"
            "- I can dynamically handle tasks using my language model capabilities.\n"
            "- I maintain a memory of recent tasks and conversations.\n"
            "- I can classify user directives into goals, rules, skills, or general conversation.\n"
            "- I can queue self-directed goals for future execution.\n"
            "- I can read and summarize my own code to improve myself.\n"
            "Let me know how I can assist you!"
        )

    def read_own_code(self, file_path):
        """
        Reads and summarizes the content of a given file.

        Args:
            file_path (str): The path to the file to read.

        Returns:
            str: A summary of the file's content.
        """
        try:
            with open(file_path, "r") as f:
                code = f.read()
            # Use the LLM to summarize the code
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a code summarization expert."},
                    {"role": "user", "content": f"Summarize the following code:\n\n{code}"}
                ]
            ).choices[0].message.content.strip()
            return response
        except Exception as e:
            return f"Sorry, I couldn't read the file due to an error: {e}"

    def fetch_data_from_internet(self, query):
        """
        Fetches data from the internet for a given query.

        Args:
            query (str): The search query.

        Returns:
            str: The retrieved information or an error message.
        """
        try:
            # Example: Use a trusted API like Wikipedia
            response = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}")
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "No information available.")
            else:
                return "Failed to retrieve information."
        except Exception as e:
            return f"Error fetching data: {e}"
