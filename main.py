import os
import torch
from Core.ethics_policy import ethics_statement
from Core.brain import Brain

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.environ["LP1_DEVICE"] = device

    print("[LP1] Initialization complete")
    print("[LP1] Ethics Policy:")
    print(ethics_statement())

    brain = Brain()

    print("[LP1] Skills loaded:")
    for skill in brain.skills:
        print(f" - {skill.__class__.__name__}")

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
        except Exception as e:
            print(f"Error: {e}")
