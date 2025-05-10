from dotenv import load_dotenv
load_dotenv()
from Core.memory import Memory
import re
import json
import os
from Core.skill_loader import load_skills
from Core.ethics_enforcer import safe_completion
import openai
from Skills import knowledge_ingestor

class Brain:
    def __init__(self):
        self.skills = load_skills()
        self.context = []
        self.session_context = []
        self.memory = Memory()
        self.client = openai  # Use the updated OpenAI library
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
        You are a directive classifier for an AI assistant.
        Given this user input, classify it as one of the following:
        - goal → user wants to set a long-term objective (e.g., "Learn about neural networks").
        - rule → user is defining behavioral boundaries (e.g., "Never share personal data").
        - trigger_skill → user is asking for an action or task to be performed (e.g., "Improve your knowledge on neural networks").
        - chat → general conversation (e.g., "How are you?").

        Respond ONLY with a JSON object with these fields: intent, priority, action.
        - intent: One of "goal", "rule", "trigger_skill", or "chat".
        - priority: One of "low", "medium", or "high".
        - action: A concise description of the action (e.g., "learn_topic", "update_knowledgebase", "respond").

        Input: {text}
        """
        try:
            response = self.client.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You classify user directives."},
                    {"role": "user", "content": prompt}
                ]
            )

            print("[Classifier raw output]", response.choices[0].message["content"])
            classification = json.loads(response.choices[0].message["content"])
            return classification
        except Exception as e:
            print(f"[Directive Classifier Error] {e}")
            return {"intent": "chat", "priority": "low", "action": "respond"}

    def create_new_skill(self, action_name):
        """Dynamically create a new skill file for the given action."""
        skill_name = action_name.lower().replace(" ", "_")
        skill_file_path = f"Skills/{skill_name}.py"

        if os.path.exists(skill_file_path):
            return f"The skill '{action_name}' already exists."

        # Generate a basic skill template
        skill_template = f"""
from Core.skill import Skill
from typing import Dict, Any

class {skill_name.capitalize()}Skill(Skill):
    \"\"\"Dynamically created skill for '{action_name}'.\"\"\"

    def describe(self) -> Dict[str, Any]:
        return {{
            "name": "{skill_name}",
            "trigger": ["{action_name}"],
            "description": "This is a dynamically created skill for '{action_name}'."
        }}

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        return "This is a placeholder response for the '{action_name}' skill."
"""

        # Write the skill file
        os.makedirs("Skills", exist_ok=True)
        with open(skill_file_path, "w") as f:
            f.write(skill_template.strip())

        # Reload skills
        self.skills = load_skills()
        self.skill_aliases = self.generate_alias_mapping()

        return f"The skill '{action_name}' has been created and loaded."

    def get_chat_context(self):
        """Retrieve recent chat context for natural conversation."""
        recent = self.memory.recall(limit=5)
        return "\n".join(f"{m['role']}: {m['content']}" for m in recent if m['role'] in ["user", "lp1"])

    def handle_input(self, user_input):
        self.memory.log("user", user_input)
        self.session_context.append({"user": user_input})

        # Handle pending skill creation
        if self.pending_skill_creation:
            if "yes" in user_input.lower():
                response = self.create_new_skill(self.pending_skill_creation)
                self.pending_skill_creation = None  # Reset pending state
                self.chat_mode = False  # Exit chat mode
            else:
                response = "Skill creation canceled."
                self.pending_skill_creation = None  # Reset pending state
                self.chat_mode = False  # Exit chat mode
            self.memory.log("lp1", response)
            self.session_context.append({"lp1": response})
            return response

        # Classify the directive
        directive = self.classify_directive(user_input)

        if directive["intent"] == "goal":
            self.chat_mode = False  # Exit chat mode
            self.memory.log("goal", user_input)
            self.store_goal(user_input)

            # Process the goal immediately
            matched_skill = self.match_skill_to_goal(user_input)
            if matched_skill:
                try:
                    response = matched_skill.handle(user_input, {"memory": self.memory})
                except Exception as e:
                    response = f"Error executing skill for goal '{user_input}': {e}"
            else:
                response = f"Queued your goal: '{user_input}'. I’ll plan how to achieve it."

        elif directive["intent"] == "rule":
            self.chat_mode = False  # Exit chat mode
            self.memory.log("rule", user_input)
            response = f"Understood. I will enforce: '{user_input}'"

        elif directive["intent"] == "trigger_skill":
            self.chat_mode = False  # Exit chat mode
            action = directive["action"]
            if action in self.skills:
                try:
                    response = self.skills[action].handle(user_input, {"memory": self.memory})
                except Exception as e:
                    response = f"Error executing skill '{action}': {e}"
            else:
                response = f"I don't have a skill for the action '{action}'. Would you like me to create one?"
                self.pending_skill_creation = action  # Set pending skill creation

        elif directive["intent"] == "chat":
            if not self.chat_mode:
                # First time entering chat mode
                response = "Let's chat! How can I assist you further?"
                self.chat_mode = True
            else:
                # Continue the conversation naturally
                response = self.client.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input}
                    ]
                ).choices[0].message["content"].strip()

        else:
            self.chat_mode = False  # Exit chat mode
            response = "I'm not sure how to respond. Could you clarify what you'd like me to do?"

        self.memory.log("lp1", response)
        self.session_context.append({"lp1": response})
        return response

    def store_goal(self, goal: str):
        with open(self.goal_store, "r+") as f:
            goals = json.load(f)
            goals.append(goal)
            f.seek(0)
            json.dump(goals, f, indent=2)
