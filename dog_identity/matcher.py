import os
import numpy as np
import cv2
from sklearn.metrics.pairwise import cosine_similarity
from .embedder import get_embedding

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMB_DIR = os.path.join(BASE_DIR, "embeddings")

# ---------------------------
# Load stored embeddings
# ---------------------------
known_embeddings = {}

for file in os.listdir(EMB_DIR):
    if file.endswith(".npy"):
        name = file.replace(".npy", "")
        known_embeddings[name] = np.load(os.path.join(EMB_DIR, file))

print("[INFO] Loaded dog identities:", list(known_embeddings.keys()))

# ---------------------------
# Identify dog
# ---------------------------
def identify_dog(face_img, threshold=0.80):
    """
    face_img: cropped RGB image of dog face
    returns: dog name or 'unknown'
    """
    test_emb = get_embedding(face_img).reshape(1, -1)

    best_match = "unknown"
    best_score = 0

    for name, emb_list in known_embeddings.items():
        score = cosine_similarity(test_emb, emb_list).max()
        if score > best_score:
            best_score = score
            best_match = name

    if best_score >= threshold:
        return best_match
    else:
        return "unknown"
