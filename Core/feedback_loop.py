from tinydb import TinyDB
from typing import Optional
import os

FEEDBACK_PATH = "lp1/data/feedback.json"

# Ensure the feedback directory exists
os.makedirs(os.path.dirname(FEEDBACK_PATH), exist_ok=True)

# Initialize the TinyDB database
db = TinyDB(FEEDBACK_PATH)

def record_feedback(input_text: str, response: str, skill_name: str, rating: int, note: Optional[str] = None):
    """
    Records user feedback for a specific skill interaction.

    Args:
        input_text (str): The user's input.
        response (str): The system's response.
        skill_name (str): The name of the skill used.
        rating (int): The user's rating of the response (e.g., 1-5).
        note (Optional[str]): Additional feedback or comments from the user.
    """
    db.insert({
        "input": input_text,
        "response": response,
        "skill": skill_name,
        "rating": rating,
        "note": note
    })

def average_rating(skill_name: str) -> float:
    """
    Calculates the average rating for a specific skill.

    Args:
        skill_name (str): The name of the skill.

    Returns:
        float: The average rating for the skill, or 0.0 if no ratings exist.
    """
    records = [r for r in db.all() if r["skill"] == skill_name]
    if not records:
        return 0.0
    return sum(r["rating"] for r in records) / len(records)
