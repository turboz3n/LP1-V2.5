from PIL import Image
import requests
from transformers import CLIPProcessor, CLIPModel
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def analyze_image(image_path: str) -> str:
    image = Image.open(image_path)
    texts = ["screenshot of code", "diagram", "text document", "graph", "form", "web UI"]

    inputs = processor(text=texts, images=image, return_tensors="pt", padding=True)
    outputs = model(**inputs)

    logits_per_image = outputs.logits_per_image
    probs = logits_per_image.softmax(dim=1)

    best_match = texts[torch.argmax(probs)].strip()
    confidence = torch.max(probs).item()

    return f"Image appears to be: '{best_match}' (confidence: {confidence:.2f})"
