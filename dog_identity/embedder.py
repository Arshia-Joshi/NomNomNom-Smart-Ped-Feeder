import os
import cv2
import numpy as np
import torch
from torchvision import models, transforms

# ---------------------------
# Load MobileNetV2
# ---------------------------
model = models.mobilenet_v2(pretrained=True)
model.classifier = torch.nn.Identity()   # remove classification head
model.eval()

# ---------------------------
# Image preprocessing
# ---------------------------
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

# ---------------------------
# Get embedding from image
# ---------------------------
def get_embedding(img):
    img = transform(img).unsqueeze(0)
    with torch.no_grad():
        embedding = model(img)
    return embedding.numpy().flatten()

# ---------------------------
# Build embeddings for each dog
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
EMB_DIR = os.path.join(BASE_DIR, "embeddings")

os.makedirs(EMB_DIR, exist_ok=True)

for dog_name in os.listdir(DATA_DIR):
    dog_path = os.path.join(DATA_DIR, dog_name)
    if not os.path.isdir(dog_path):
        continue

    embeddings = []

    print(f"[INFO] Processing {dog_name}...")

    for img_name in os.listdir(dog_path):
        img_path = os.path.join(dog_path, img_name)
        img = cv2.imread(img_path)

        if img is None:
            continue

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        emb = get_embedding(img)
        embeddings.append(emb)

    embeddings = np.array(embeddings)
    np.save(os.path.join(EMB_DIR, f"{dog_name}.npy"), embeddings)

    print(f"[DONE] Saved embeddings for {dog_name}")

print("✅ All embeddings created successfully")
