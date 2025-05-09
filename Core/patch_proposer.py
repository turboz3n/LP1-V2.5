import difflib
import os
from openai import OpenAI

client = OpenAI()

def propose_patch(original_path: str, prompt: str) -> str:
    if not os.path.exists(original_path):
        return "File not found."

    with open(original_path, "r") as f:
        original_code = f.read()

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You're an expert Python developer. Rewrite code based on user feedback."},
            {"role": "user", "content": f"Here is the file content:\n\n{original_code}\n\nNow, based on this instruction, rewrite it:\n{prompt}"}
        ]
    )

    new_code = response.choices[0].message.content.strip()
    patch = difflib.unified_diff(
        original_code.splitlines(),
        new_code.splitlines(),
        fromfile=original_path,
        tofile=original_path,
        lineterm=""
    )

    patch_text = "\n".join(patch)
    patch_path = "lp1/data/patch.diff"
    os.makedirs(os.path.dirname(patch_path), exist_ok=True)
    with open(patch_path, "w") as f:
        f.write(patch_text)

    return f"Patch proposed and saved to {patch_path}. Awaiting approval."
