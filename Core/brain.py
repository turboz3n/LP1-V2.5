from dotenv import load_dotenv
load_dotenv()
from Core.memory import Memory
import re
import json
import os
import requests
from Core.skill_loader import load_skills
from Core.ethics_enforcer import safe_completion
from openai import OpenAI
from Skills import knowledge_ingestor

class Memory:
    def __init__(self):
        self.logs = []  # Stores conversation logs
        self.task_history = []  # Stores completed tasks

    def log(self, role, message):
        self.logs.append({"role": role, "message": message})

    def add_task(self, task):
        self.task_history.append(task)

    def get_recent_tasks(self, count=5):
        return self.task_history[-count:]

class Brain:
    def __init__(self):
        self.skills = load_skills()
        self.context = []
        self.session_context = []
        self.memory = Memory()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.goal_store = "goals.json"
        self.chat_mode = False
        self.pending_skill_creation = None
        if not os.path.exists(self.goal_store):
            with open(self.goal_store, "w") as f:
                json.dump([], f)

        self.skill_aliases = self.generate_alias_mapping()
        self.validate_skills()

    def validate_skills(self):
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
        recent_context = "\n".join([f"{entry['role']}: {entry['message']}" for entry in self.session_context[-5:]])
        prompt = f"""
        You are LP1, an advanced AI assistant. Given this user input and recent context, classify it as one of the following:
        - goal → user wants to set a long-term objective (e.g., "Learn about neural networks").
        - rule → user is defining behavioral boundaries (e.g., "Never share personal data").
        - trigger_skill → user is asking for an action or task to be performed (e.g., "Improve your knowledge on neural networks").
        - chat → general conversation (e.g., "How are you?").

        Respond ONLY with a JSON object containing:
        - intent: One of "goal", "rule", "trigger_skill", or "chat".
        - priority: One of "low", "medium", or "high".
        - action: A concise description of the action (e.g., "learn_topic", "update_knowledgebase", "respond").
        - source: Either "user" (if the task is user-directed) or "self" (if the task is self-directed).

        Recent Context:
        {recent_context}

        Input: {text}
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You classify user directives with context-awareness."},
                    {"role": "user", "content": prompt}
                ]
            )
            print("[Classifier raw output]", response.choices[0].message.content)
            classification = json.loads(response.choices[0].message.content)
            return classification
        except Exception as e:
            print(f"[Directive Classifier Error] {e}")
            return {"intent": "chat", "priority": "low", "action": "respond", "source": "user"}

    def dynamic_fallback(self, action, user_input):
        try:
            recent_tasks = "\n".join(self.memory.get_recent_tasks())
            recent_goals = json.dumps(json.load(open(self.goal_store, "r")), indent=2)

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are LP1, a highly capable assistant that can perform tasks dynamically based on user instructions."},
                    {"role": "user", "content": f"""
                    Perform the following action: {action}.
                    Context:
                    - User Input: {user_input}
                    - Recent Tasks: {recent_tasks}
                    - Current Goals: {recent_goals}
                    """}
                ]
            ).choices[0].message.content.strip()

            self.memory.add_task(f"Completed action: {action} - {response}")
            return response
        except Exception as e:
            print(f"[Dynamic Fallback Error] {e}")
            return f"Sorry, I couldn't perform the action '{action}' due to an error."

    def handle_input(self, user_input):
        self.memory.log("user", user_input)
        self.session_context.append({"user": user_input})

        directive = self.classify_directive(user_input)
        print("[Directive]", directive)

        if directive["intent"] == "chat":
            if "who are you" in user_input.lower() or "what can you do" in user_input.lower():
                response = self.describe_capabilities()
            elif "what skills do you have" in user_input.lower() or "list your skills" in user_input.lower():
                response = self.summarize_skills()
            elif "what did you learn" in user_input.lower():
                recent_tasks = self.memory.get_recent_tasks()
                if recent_tasks:
                    response = "Here's what I've done recently:\n" + "\n".join(recent_tasks)
                else:
                    response = "I haven't done much yet. Let me know how I can assist you!"
            else:
                recent_context = "\n".join([f"{entry['role']}: {entry['message']}" for entry in self.session_context[-5:]])
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are LP1, a friendly and conversational assistant with advanced capabilities."},
                        {"role": "user", "content": f"{user_input}\n\nRecent Context:\n{recent_context}"}
                    ]
                ).choices[0].message.content.strip()

        elif directive["intent"] == "goal":
            if directive["source"] == "user":
                response = self.dynamic_fallback(directive["action"], user_input)
                self.memory.add_task(f"Completed goal: {directive['action']}")
            else:
                self.queue_goal(directive["action"])
                response = f"Got it! I'll queue the goal: {directive['action']}"

        elif directive["intent"] == "rule":
            response = f"Understood. I'll enforce the rule: {directive['action']}"

        elif directive["intent"] == "trigger_skill":
            skill_name = directive["action"]
            if skill_name in self.skills:
                response = self.skills[skill_name].handle(user_input, self.context)
                self.memory.add_task(f"Executed skill: {skill_name}")
            else:
                response = self.dynamic_fallback(skill_name, user_input)
                self.memory.add_task(f"Fallback executed for action: {skill_name}")

        else:
            response = "I'm not sure how to respond. Could you clarify what you'd like me to do?"

        self.memory.log("lp1", response)
        self.session_context.append({"lp1": response})
        return response
