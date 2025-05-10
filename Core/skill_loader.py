import importlib
import os
import sys
from Core.skill import Skill  # Ensure the correct Skill base class is imported

def load_skills():
    skills = {}
    skill_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../Skills"))
    sys.path.append(skill_dir)

    print("[LP1] Scanning Skills folder...")
    for filename in os.listdir(skill_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            try:
                # Dynamically import the module
                module = importlib.import_module(module_name)

                # Iterate through all attributes in the module
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    # Check if the attribute is a class and a subclass of Skill
                    if isinstance(attr, type) and issubclass(attr, Skill) and attr is not Skill:
                        instance = attr()  # Instantiate the skill
                        normalized_name = module_name.lower().replace(" ", "_").replace("-", "_")
                        skills[normalized_name] = instance
                        print(f"[LP1] Loaded: {module_name} as {normalized_name}")
                        break  # Stop after finding the first valid Skill subclass
            except Exception as e:
                print(f"[LP1] Failed to load {filename}: {e}")

    return skills
