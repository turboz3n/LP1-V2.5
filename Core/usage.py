from typing import Dict
from tinydb import TinyDB, Query
import os

USAGE_PATH = "lp1/data/usage.json"

# Ensure the directory for the usage database exists
os.makedirs(os.path.dirname(USAGE_PATH), exist_ok=True)

# Initialize the TinyDB database
db = TinyDB(USAGE_PATH)

def log_skill_use(skill_name: str):
    """
    Logs the usage of a skill by incrementing its usage count.

    Args:
        skill_name (str): The name of the skill being used.
    """
    Skill = Query()
    found = db.search(Skill.name == skill_name)
    if found:
        count = found[0]["count"] + 1
        db.update({"count": count}, Skill.name == skill_name)
    else:
        db.insert({"name": skill_name, "count": 1})

def get_skill_usage() -> Dict[str, int]:
    """
    Retrieves the usage statistics for all skills.

    Returns:
        Dict[str, int]: A dictionary where keys are skill names and values are usage counts.
    """
    return {entry["name"]: entry["count"] for entry in db.all()}
