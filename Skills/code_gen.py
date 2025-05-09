import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def run(user_input: str, context: str = None):
    if not context:
        context = user_input

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful and knowledgeable AI assistant."},
                {"role": "user", "content": context}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating response: {e}"

if __name__ == "__main__":
    import sys
    user_input = " ".join(sys.argv[1:])
    print(run(user_input))

