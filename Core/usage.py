from typing import Dict
from tinydb import TinyDB, Query
import os

USAGE_PATH = "lp1/data/usage.json"
os.makedirs(os.path.dirname(USAGE_PATH), exist_ok=True)
db = TinyDB(USAGE_PATH)

def log_skill_use(skill_name: str):
    Skill = Query()
    found = db.search(Skill.name == skill_name)
    if found:
        count = found[0]["count"] + 1
        db.update({"count": count}, Skill.name == skill_name)
    else:
        db.insert({"name": skill_name, "count": 1})

def get_skill_usage() -> Dict[str, int]:
    return {entry["name"]: entry["count"] for entry in db.all()}
