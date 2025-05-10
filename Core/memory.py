# Core/memory.py

import os
import json
from datetime import datetime

MEMORY_FILE = "lp1_memory.json"

class Memory:
    """Manages LP1's memory, including logging, recalling, and clearing interactions."""

    def __init__(self, memory_file: str = MEMORY_FILE):
        """
        Initializes the Memory class and ensures the memory file exists.

        Args:
            memory_file (str): Path to the memory file.
        """
        self.memory_file = memory_file
        self._ensure_file()

    def _ensure_file(self):
        """Ensures the memory file exists."""
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)

    def log(self, role: str, content: str):
        """
        Logs a new interaction to memory.

        Args:
            role (str): The role of the interaction (e.g., 'user', 'system').
            content (str): The content of the interaction.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "content": content
        }
        memory = self._load_memory()
        memory.append(entry)
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)

    def recall(self, limit: int = 10):
        """
        Recalls the most recent interactions from memory.

        Args:
            limit (int): The number of interactions to recall.

        Returns:
            list: A list of the most recent interactions.
        """
        memory = self._load_memory()
        return memory[-limit:]

    def clear(self):
        """Clears all interactions from memory."""
        with open(self.memory_file, 'w') as f:
            json.dump([], f)

    def _load_memory(self):
        """
        Loads the memory from the memory file.

        Returns:
            list: A list of all logged interactions.
        """
        with open(self.memory_file, 'r') as f:
            return json.load(f)
