# Core/memory.py

import os
import json
from datetime import datetime

MEMORY_FILE = "lp1_memory.json"

class Memory:
    def __init__(self, memory_file: str = MEMORY_FILE):
        self.memory_file = memory_file
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w') as f:
                json.dump([], f)

    def log(self, role: str, content: str):
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
        memory = self._load_memory()
        return memory[-limit:]

    def clear(self):
        with open(self.memory_file, 'w') as f:
            json.dump([], f)

    def _load_memory(self):
        with open(self.memory_file, 'r') as f:
            return json.load(f)
