from Core.skill import Skill
from typing import Dict, Any
import subprocess
import os


class SelfRewriteSkill(Skill):
    """Skill for modifying LP1's own logic or code based on reflective instructions."""

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "self_rewrite",
            "trigger": ["refactor", "improve yourself", "rewrite code", "patch"],
            "description": "Modifies LP1's own logic or code based on reflective instructions."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Handles self-modification requests."""
        if "git" not in user_input:
            return "To apply changes, please reference a Git diff or patch."

        patch_path = "lp1/data/patch.diff"
        if not os.path.exists(patch_path):
            return "No patch file found at lp1/data/patch.diff."

        try:
            subprocess.run(["git", "apply", patch_path], check=True)
            return "Patch successfully applied to the codebase."
        except subprocess.CalledProcessError as e:
            return f"Failed to apply patch: {e}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
