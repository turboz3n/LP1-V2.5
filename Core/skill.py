#Core/skill.py

from abc import ABC, abstractmethod

class Skill(ABC): """Base class for all skills. Each skill must describe itself and define how it handles input."""

@abstractmethod
def describe(self) -> str:
    """Returns a brief description of the skill."""
    pass

@abstractmethod
def handle(self, *args, **kwargs):
    """Handles the input logic for this skill."""
    pass

