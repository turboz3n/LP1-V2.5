import os
from dotenv import load_dotenv
import torch
from Core.ethics_policy import ethics_statement
from Core.brain import Brain

# Load environment variables from the .env file
load_dotenv()

# Access the API key
api_key = os.getenv("OPENAI_API_KEY")

def main():
    """
    Entry point for LP1. Initializes the system and handles user interactions.
    """
    # Set the device for computation
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.environ["LP1_DEVICE"] = device

    print("[LP1] Initialization complete")
    print("[LP1] Ethics Policy:")
    print(ethics_statement())

    # Initialize the Brain
    brain = Brain()

    # Main interaction loop
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            response = brain.handle_input(user_input)
            print(f"LP1: {response}")
        except KeyboardInterrupt:
            print("\nSession interrupted by user.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
