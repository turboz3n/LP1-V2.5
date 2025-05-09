from lp1.core.skill import Skill
from typing import Dict, Any
import subprocess, os

class SelfRewriteSkill(Skill):
    def describe(self) -> Dict[str, Any]:
        return {
            "name": "self_rewrite",
            "trigger": ["refactor", "improve yourself", "rewrite code", "patch"]
        }

    async def handle(self, input_text: str, state: Dict[str, Any]) -> str:
        if "git" not in input_text:
            return "To apply changes, please reference a Git diff or patch."

        patch_path = "lp1/data/patch.diff"
        if not os.path.exists(patch_path):
            return "No patch file found at lp1/data/patch.diff."

        try:
            subprocess.run(["git", "apply", patch_path], check=True)
            return "Patch successfully applied to codebase."
        except subprocess.CalledProcessError as e:
            return f"Failed to apply patch: {e}"
