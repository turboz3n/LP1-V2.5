# Core/brain.py
from dotenv import load_dotenv
load_dotenv()
from Core.memory import Memory
import re
from Skills import knowledge_ingestor
import json
import os

from Core.skill_loader import load_skills
from Core.ethics_enforcer import safe_completion

class Brain:
    def __init__(self):
        self.skills = load_skills()
        self.context = []
        self.session_context = []
        self.memory = Memory()
        self.goal_store = "goals.json"
        if not os.path.exists(self.goal_store):
            with open(self.goal_store, "w") as f:
                json.dump([], f)

    def classify_input(self, user_input):
        user_input = user_input.strip().lower()
        if user_input.endswith('?') or user_input.startswith(('what', 'who', 'how', 'when', 'why')):
            return 'question'
        if user_input.startswith(('i want', 'please', 'can you', 'i need', 'make', 'do', 'create')):
            return 'command'
        if user_input.startswith(('suggest', 'maybe', 'could you')):
            return 'suggestion'
        return 'unknown'

    def classify_directive(self, text: str) -> dict:
        lowered = text.lower()

        if any(phrase in lowered for phrase in ["i want you to", "you should", "your job is to"]):
            return {"intent": "goal", "priority": "high", "action": "record_and_plan"}

        if any(phrase in lowered for phrase in ["never say", "don't ever", "stop doing"]):
            return {"intent": "rule", "priority": "high", "action": "record_and_enforce"}

        if re.match(r"^(please )?(make|build|write|create|generate) ", lowered):
            return {"intent": "command", "priority": "medium", "action": "trigger_skill"}

        return {"intent": "chat", "priority": "low", "action": "respond"}

    def store_goal(self, goal: str):
        with open(self.goal_store, "r+") as f:
            goals = json.load(f)
            goals.append(goal)
            f.seek(0)
            json.dump(goals, f, indent=2)

    def handle_input(self, user_input):
        self.memory.log("user", user_input)
        self.session_context.append({"user": user_input})

        if any(kw in user_input.lower() for kw in ["learn ", "study ", "become more knowledgeable"]):
            topic = user_input.lower().split("about")[-1].strip() if "about" in user_input.lower() else user_input.split(" ", 1)[-1]
            result = knowledge_ingestor.learn_topic(topic)
            self.memory.log("lp1", result)
            self.store_goal(f"learn {topic}")
            self.session_context.append({"lp1": result})
            return result

        elif re.search(r'(what|give me a).*?(summary|recap|learned).*?(about|on) (.+)', user_input.lower()):
            match = re.search(r'(about|on) (.+)', user_input.lower())
            if match:
                topic = match.group(2).strip()
                summary = self.memory.query(topic)
                response = summary if summary else f"I haven't learned anything specific about {topic} yet."
            else:
                response = "Could not identify the topic to summarize."

        else:
            directive = self.classify_directive(user_input)

            if directive["action"] == "record_and_plan":
                self.memory.log("goal", user_input)
                self.store_goal(user_input)
                response = f"Got it. Queued your goal: '{user_input}'. I’ll plan how to achieve it."

            elif directive["action"] == "record_and_enforce":
                self.memory.log("rule", user_input)
                response = f"Understood. I will enforce: '{user_input}'"

            elif directive["action"] == "trigger_skill":
                response = f"I recognized that as a command. Routing to skillset to execute: '{user_input}'"

            else:
                intent_type = self.classify_input(user_input)
                if intent_type == 'question':
                    response = self.respond_to_question(user_input)
                elif intent_type == 'command':
                    response = self.execute_command(user_input)
                elif intent_type == 'suggestion':
                    response = self.plan_new_capability(user_input)
                else:
                    response = "I'm not sure how to respond. Could you clarify what you'd like me to do?"

        self.memory.log("lp1", response)
        self.session_context.append({"lp1": response})
        return response

    def respond_to_question(self, user_input):
        recent = self.memory.recall()
        memory_context = "\n".join(f"{m['role']}: {m['content']}" for m in recent)
        response = safe_completion(
            f"Context:\n{memory_context}\n\n{user_input}"
        )
        return response.choices[0].message.content

    def execute_command(self, user_input):
        if 'improve' in user_input or 'become smarter' in user_input:
            topic = user_input.split("improve", 1)[-1].strip() or "general intelligence"
            self.memory.log("goal", f"Self-improvement: {topic}")
            self.store_goal(f"Self-improvement: {topic}")
            result = knowledge_ingestor.learn_topic(topic)
            self.memory.log("lp1", result)
            return result
        return "Command acknowledged, but I need more detail on the requested action."

    def plan_new_capability(self, user_input):
        return "Planning module stub: This will eventually propose new modules when capabilities are lacking."

brain = Brain()
