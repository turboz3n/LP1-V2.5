import importlib 
import os 
import sys 
import traceback

def load_skills():
    skills = {}
    skills_dir = os.path.join(os.path.dirname(__file__), '../skills')
    sys.path.insert(0, os.path.abspath(skills_dir))

    for filename in os.listdir(skills_dir):
        if filename.endswith('.py') and not filename.startswith('__'):
            modulename = filename[:-3]
            try:
                module = importlib.import_module(modulename)
                skills[modulename] = module
            except Exception as e:
                print(f"Failed to load skill {modulename}: {e}")

    return skills
