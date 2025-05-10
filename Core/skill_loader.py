import importlib
import os
import sys

def load_skills():
    skills = {}
    skill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Skills"))
    sys.path.append(skill_dir)

    print("[LP1] Scanning Skills folder...")
    for filename in os.listdir(skill_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            skill_name = filename[:-3]  # remove .py
            try:
                if module_name in sys.modules:
                    del sys.modules[module_name]
                module = importlib.import_module(skill_name)
                if hasattr(module, "Skill"):
                    instance = module.Skill()
                    skills[skill_name.lower()] = instance
                    print(f"[LP1] Loaded: {skill_name}")
                else:
                    print(f"[LP1] Skipped (no Skill class): {filename}")
            except Exception as e:
                print(f"[LP1] Failed to load {filename}: {e}")

    return skills
