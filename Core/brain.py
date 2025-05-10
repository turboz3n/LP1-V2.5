from dotenv import load_dotenv
load_dotenv()
from Core.memory import Memory
import re
import json
import os
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
        You are a directive classifier for an AI assistant.
        Given this user input, classify it as one of the following:
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

    def handle_input(self, user_input):
        self.memory.log("user", user_input)
        self.session_context.append({"user": user_input})

        # Classify the directive
        directive = self.classify_directive(user_input)
        print("[Directive]", directive)  # Debug log

        # Handle the directive based on its intent
        if directive["intent"] == "chat":
            if not self.chat_mode:
                # First time entering chat mode
                response = "Let's chat! How can I assist you further?"
                self.chat_mode = True
            else:
                # Continue the conversation naturally
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input}
                    ]
                ).choices[0].message.content.strip()

        elif directive["intent"] == "goal":
            # Handle goal intent
            if directive["source"] == "user":
                # Execute user-directed tasks immediately
                response = self.dynamic_fallback(directive["action"], user_input)
            else:
                # Queue self-directed tasks
                self.queue_goal(directive["action"])
                response = f"Got it! I'll queue the goal: {directive['action']}"

        elif directive["intent"] == "rule":
            # Handle rule intent
            response = f"Understood. I'll enforce the rule: {directive['action']}"

        elif directive["intent"] == "trigger_skill":
            # Handle trigger_skill intent
            skill_name = directive["action"]
            if skill_name in self.skills:
                # Execute the skill if it exists
                response = self.skills[skill_name].handle(user_input, self.context)
            else:
                # Fallback: Use OpenAI to handle the action
                response = self.dynamic_fallback(skill_name, user_input)

        else:
            # Fallback for unknown intents
            response = "I'm not sure how to respond. Could you clarify what you'd like me to do?"

        self.memory.log("lp1", response)
        self.session_context.append({"lp1": response})
        return response

    def dynamic_fallback(self, action, user_input):
        """
        Handles generic or undefined actions dynamically using the OpenAI LLM.

        Args:
            action (str): The action to perform.
            user_input (str): The original user input.

        Returns:
            str: The response generated by the OpenAI LLM.
        """
        try:
            # Use OpenAI to interpret and execute the action
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a highly capable assistant that can perform tasks dynamically based on user instructions."},
                    {"role": "user", "content": f"Perform the following action: {action}. Context: {user_input}"}
                ]
            ).choices[0].message.content.strip()
            return response
        except Exception as e:
            print(f"[Dynamic Fallback Error] {e}")
            return f"Sorry, I couldn't perform the action '{action}' due to an error."

    def queue_goal(self, goal):
        """
        Adds a self-directed goal to the goals list.

        Args:
            goal (str): The goal to queue.
        """
        try:
            with open(self.goal_store, "r") as f:
                goals = json.load(f)
        except FileNotFoundError:
            goals = []

        goals.append(goal)

        with open(self.goal_store, "w") as f:
            json.dump(goals, f)

        print(f"[Goal Queued] {goal}")
