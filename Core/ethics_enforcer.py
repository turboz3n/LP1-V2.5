from lp1.core.ethics_policy import enforce_ethics_context
from openai import OpenAI  # Import the OpenAI class
import os

def safe_completion(prompt: str, role: str = "user", system_override: str = None):
    """
    Ensures that the prompt adheres to ethical guidelines before sending it to the OpenAI API.

    Args:
        prompt (str): The user input or query to process.
        role (str): The role of the message sender (default is "user").
        system_override (str): Optional override for the system message.

    Returns:
        dict: The response from the OpenAI API.
    """
    # Apply ethical enforcement to the prompt
    enforced_prompt = enforce_ethics_context(prompt)

    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Send the prompt to the OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_override or "You are a kind, helpful, and safe AI assistant."},
                {"role": role, "content": enforced_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return {"error": f"Failed to complete the request: {e}"}
