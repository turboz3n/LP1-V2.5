from typing import Dict
from tinydb import TinyDB, Query
import os

TOM_PATH = "lp1/data/theory_of_mind.json"

# Ensure the directory for the Theory of Mind database exists
os.makedirs(os.path.dirname(TOM_PATH), exist_ok=True)

# Initialize the TinyDB database
db = TinyDB(TOM_PATH)

def update_agent_profile(agent_id: str, beliefs: Dict):
    """
    Updates or creates a profile for an agent with the given beliefs.

    Args:
        agent_id (str): The unique identifier for the agent.
        beliefs (Dict): A dictionary of beliefs about the agent.
    """
    Agent = Query()
    existing = db.search(Agent.id == agent_id)
    if existing:
        db.update({"beliefs": beliefs}, Agent.id == agent_id)
    else:
        db.insert({"id": agent_id, "beliefs": beliefs})

def get_agent_beliefs(agent_id: str) -> Dict:
    """
    Retrieves the beliefs about a specific agent.

    Args:
        agent_id (str): The unique identifier for the agent.

    Returns:
        Dict: A dictionary of beliefs about the agent, or an empty dictionary if no profile exists.
    """
    Agent = Query()
    result = db.search(Agent.id == agent_id)
    if result:
        return result[0].get("beliefs", {})
    return {}

def explain_assumption(agent_id: str) -> str:
    """
    Provides a summary of LP1's beliefs about a specific agent.

    Args:
        agent_id (str): The unique identifier for the agent.

    Returns:
        str: A summary of LP1's beliefs about the agent.
    """
    beliefs = get_agent_beliefs(agent_id)
    if not beliefs:
        return f"No model of {agent_id} found."
    summary = f"LP1 believes the following about {agent_id}:\n"
    for k, v in beliefs.items():
        summary += f"- {k}: {v}\n"
    return summary
