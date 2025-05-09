import os
import torch
from Core.skill_loader import load_skills
from Core.brain import Brain

if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    os.environ["LP1_DEVICE"] = device

    print("[LP1] Initialization complete")
    load_skills()

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
            brain = Brain()
response = brain.handle_input(user_input)
            print(f"LP1: {response}")
        except KeyboardInterrupt:
            print("\nSession interrupted by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
