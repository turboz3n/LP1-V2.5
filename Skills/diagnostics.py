from Core.skill import Skill
import platform
import psutil
from typing import Dict, Any


class DiagnosticsSkill(Skill):
    """Skill for providing system diagnostics and health checks."""

    def describe(self) -> Dict[str, Any]:
        return {
            "name": "diagnostics",
            "trigger": ["system status", "health check", "diagnostics", "resources"],
            "description": "Provides system diagnostics, including CPU and memory usage."
        }

    def handle(self, user_input: str, context: Dict[str, Any]) -> str:
        """Returns system health and resource usage information."""
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            return (
                f"System Diagnostics:\n"
                f"Platform: {platform.system()} {platform.release()}\n"
                f"CPU Usage: {cpu}%\n"
                f"Memory: {mem.percent}% used "
                f"({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)"
            )
        except Exception as e:
            return f"Error in diagnostics skill: {e}"
