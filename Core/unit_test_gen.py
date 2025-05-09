import os
from openai import OpenAI

client = OpenAI()

def generate_tests(skill_path: str) -> str:
    if not os.path.exists(skill_path):
        return "Skill not found."

    with open(skill_path, "r") as f:
        source = f.read()

    messages = [
        {"role": "system", "content": "You're an AI that writes unit tests for Python modules."},
        {"role": "user", "content": f"Generate pytest-compatible unit tests for this skill:\n{source}"}
    ]

    response = client.chat.completions.create(model="gpt-4", messages=messages)
    test_code = response.choices[0].message.content.strip()

    test_path = skill_path.replace("skills/", "tests/test_")
    with open(test_path, "w") as f:
        f.write(test_code)

    return f"Unit tests written to: {test_path}"
