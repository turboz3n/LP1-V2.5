from Core.skill import Skill
import os
import difflib
import importlib
from typing import List, Dict, Any


class PatchProposal:
    def __init__(self, file_path: str, new_code: str):
        self.file_path = file_path
        self.new_code = new_code

    def diff(self) -> str:
        if not os.path.exists(self.file_path):
            return f"[New file] {self.file_path}\n" + self.new_code
        with open(self.file_path, 'r') as f:
            original = f.readlines()
        updated = self.new_code.splitlines(keepends=True)
        return ''.join(difflib.unified_diff(original, updated, fromfile=self.file_path, tofile=self.file_path))

    def summary(self) -> str:
        try:
            summarizer = importlib.import_module("lp1.skills.code_summarizer")
            if hasattr(summarizer, "summarize_file"):
                return summarizer.summarize_file(self.file_path)
        except Exception as e:
            return f"[Summary Error] {e}"
        return "[Summary] Not available."

    def apply(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w') as f:
            f.write(self.new_code)


class AutoPatcher:
    def __init__(self):
        self.pending_patches: List[PatchProposal] = []

    def propose_patch(self, file_path: str, new_code: str):
        patch = PatchProposal(file_path, new_code)
        self.pending_patches.append(patch)
        return patch.diff()

    def list_diffs(self) -> str:
        output = []
        for p in self.pending_patches:
            output.append(f"File: {p.file_path}")
            output.append("\n--- Summary ---")
            output.append(p.summary())
            output.append("\n--- Diff ---")
            output.append(p.diff())
            output.append("\n")
        return "\n".join(output)

    def apply_all(self):
        for patch in self.pending_patches:
            patch.apply()
        self.pending_patches.clear()

    def clear(self):
        self.pending_patches.clear()


class Autopatcher(Skill):
    """Skill for proposing and applying patches to LP1's codebase."""

    def __init__(self):
        self.autopatcher = AutoPatcher()

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "autopatcher",
            "trigger": ["fix", "bug", "patch", "update"],
            "description": "Proposes and applies patches to the system's codebase."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Attempts to modify LP1's code or skills based on detected issues or requests."""
        if "list patches" in user_input:
            return self.autopatcher.list_diffs()
        elif "apply patches" in user_input:
            self.autopatcher.apply_all()
            return "All patches have been applied."
        elif "clear patches" in user_input:
            self.autopatcher.clear()
            return "All pending patches have been cleared."
        elif "propose patch" in user_input:
            file_path = context.get("file_path")
            new_code = context.get("new_code")
            if not file_path or not new_code:
                return "Please provide both 'file_path' and 'new_code' in the context."
            diff = self.autopatcher.propose_patch(file_path, new_code)
            return f"Patch proposed:\n{diff}"
        else:
            return "Invalid command. Use 'list patches', 'apply patches', 'clear patches', or 'propose patch'."
