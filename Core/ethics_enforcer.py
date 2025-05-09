from lp1.core.ethics_policy import enforce_ethics_context
from openai import OpenAI

client = OpenAI()

def safe_completion(prompt: str, role: str = "user", system_override: str = None):
    enforced_prompt = enforce_ethics_context(prompt)
    return client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_override or "You are a kind, helpful, and safe AI assistant."},
            {"role": role, "content": enforced_prompt}
        ]
    )
