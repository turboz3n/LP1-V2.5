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
            module_name = filename[:-3]
            try:
                if module_name in sys.modules:
                    del sys.modules[module_name]

                module = importlib.import_module(module_name)
                if hasattr(module, "Skill"):
                    instance = module.Skill()
                    # Validate that the Skill class has a 'handle' method
                    if hasattr(instance, "handle") and callable(instance.handle):
                        normalized_name = module_name.lower().replace(" ", "_").replace("-", "_")
                        skills[normalized_name] = instance
                        print(f"[LP1] Loaded: {module_name} as {normalized_name}")
                    else:
                        print(f"[LP1] Skipped (Skill class missing 'handle' method): {filename}")
                else:
                    print(f"[LP1] Skipped (no Skill class): {filename}")
            except Exception as e:
                print(f"[LP1] Failed to load {filename}: {e}")

    return skills
