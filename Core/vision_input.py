from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel

# Load the CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def analyze_image(image_path: str) -> str:
    """
    Analyzes an image and identifies its content based on predefined categories.

    Args:
        image_path (str): The file path to the image.

    Returns:
        str: A description of the image content with confidence score.
    """
    try:
        # Load the image
        image = Image.open(image_path)
        texts = ["screenshot of code", "diagram", "text document", "graph", "form", "web UI"]

        # Process the image and text inputs
        inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
        outputs = model(**inputs)

        # Compute probabilities
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)

        # Determine the best match
        best_match = texts[torch.argmax(probs)].strip()
        confidence = torch.max(probs).item()

        return f"Image appears to be: '{best_match}' (confidence: {confidence:.2f})"
    except Exception as e:
        return f"Error analyzing image: {e}"
