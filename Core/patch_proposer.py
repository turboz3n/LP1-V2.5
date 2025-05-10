import difflib
import os
import openai

def propose_patch(original_path: str, prompt: str) -> str:
    """
    Proposes a patch for a given file based on user instructions.

    Args:
        original_path (str): Path to the original file.
        prompt (str): User instructions for modifying the file.

    Returns:
        str: A message indicating the status of the patch proposal.
    """
    if not os.path.exists(original_path):
        return "File not found."

    # Read the original file content
    with open(original_path, "r") as f:
        original_code = f.read()

    try:
        # Generate the new code using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You're an expert Python developer. Rewrite code based on user feedback."},
                {"role": "user", "content": f"Here is the file content:\n\n{original_code}\n\nNow, based on this instruction, rewrite it:\n{prompt}"}
            ]
        )

        new_code = response.choices[0].message["content"].strip()

        # Generate a unified diff patch
        patch = difflib.unified_diff(
            original_code.splitlines(),
            new_code.splitlines(),
            fromfile=original_path,
            tofile=original_path,
            lineterm=""
        )

        patch_text = "\n".join(patch)

        # Save the patch to a file
        patch_path = "lp1/data/patch.diff"
        os.makedirs(os.path.dirname(patch_path), exist_ok=True)
        with open(patch_path, "w") as f:
            f.write(patch_text)

        return f"Patch proposed and saved to {patch_path}. Awaiting approval."
    except Exception as e:
        return f"Error generating patch: {e}"
