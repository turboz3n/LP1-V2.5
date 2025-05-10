import importlib
import os
import sys

def load_skills():
    skills = {}
    skill_dir = os.path.join(os.path.dirname(__file__), "../Skills")
    skill_dir = os.path.abspath(skill_dir)
    sys.path.append(skill_dir)

    print("[LP1] Scanning Skills folder...")
    for filename in os.listdir(skill_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "Skill"):
                    skill_instance = module.Skill()
                    skills[module_name.lower()] = skill_instance
                    print(f"[LP1] Loaded: {filename}")
                else:
                    print(f"[LP1] Skipped (no Skill class): {filename}")
            except Exception as e:
                print(f"[LP1] Failed to load {filename}: {e}")

    return skills
