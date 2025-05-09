from tinydb import TinyDB
from typing import Optional
import os

FEEDBACK_PATH = "lp1/data/feedback.json"
os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)
db = TinyDB(FEEDBACK_PATH)

def record_feedback(input_text: str, response: str, skill_name: str, rating: int, note: Optional[str] = None):
    db.insert({
        "input": input_text,
        "response": response,
        "skill": skill_name,
        "rating": rating,
        "note": note
    })

def average_rating(skill_name: str) -> float:
    records = [r for r in db.all() if r["skill"] == skill_name]
    if not records:
        return 0.0
    return sum(r["rating"] for r in records) / len(records)
