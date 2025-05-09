from typing import Dict
from tinydb import TinyDB, Query
import os

TOM_PATH = "lp1/data/theory_of_mind.json"
os.makedirs(os.path.dirname(TOM_PATH), exist_ok=True)
db = TinyDB(TOM_PATH)

def update_agent_profile(agent_id: str, beliefs: Dict):
    Agent = Query()
    existing = db.search(Agent.id == agent_id)
    if existing:
        db.update({"beliefs": beliefs}, Agent.id == agent_id)
    else:
        db.insert({"id": agent_id, "beliefs": beliefs})

def get_agent_beliefs(agent_id: str) -> Dict:
    Agent = Query()
    result = db.search(Agent.id == agent_id)
    if result:
        return result[0].get("beliefs", {})
    return {}

def explain_assumption(agent_id: str) -> str:
    beliefs = get_agent_beliefs(agent_id)
    if not beliefs:
        return f"No model of {agent_id} found."
    summary = f"LP1 believes the following about {agent_id}:\n"
    for k, v in beliefs.items():
        summary += f"- {k}: {v}\n"
    return summary
