import os
import openai

def generate_tests(skill_path: str) -> str:
    """
    Generates pytest-compatible unit tests for a given skill.

    Args:
        skill_path (str): The file path of the skill module.

    Returns:
        str: A message indicating the status of the test generation.
    """
    if not os.path.exists(skill_path):
        return "Skill not found."

    # Read the source code of the skill
    with open(skill_path, "r") as f:
        source = f.read()

    try:
        # Generate unit tests using OpenAI
        messages = [
            {"role": "system", "content": "You're an AI that writes unit tests for Python modules."},
            {"role": "user", "content": f"Generate pytest-compatible unit tests for this skill:\n{source}"}
        ]

        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        test_code = response.choices[0].message["content"].strip()

        # Determine the test file path
        test_path = skill_path.replace("Skills/", "Tests/test_").replace(".py", "_test.py")
        os.makedirs(os.path.dirname(test_path), exist_ok=True)

        # Write the generated tests to the test file
        with open(test_path, "w") as f:
            f.write(test_code)

        return f"Unit tests written to: {test_path}"
    except Exception as e:
        return f"Error generating unit tests: {e}"
