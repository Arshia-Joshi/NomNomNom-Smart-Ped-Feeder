import cv2
import os
from dog_identity.matcher import identify_dog

folder = "dog_identity/data/karu"

# Pick first image automatically (e.g., k1.jpg)
img_name = os.listdir(folder)[0]
img_path = os.path.join(folder, img_name)

img = cv2.imread(img_path)

if img is None:
    raise ValueError(f"Could not read image: {img_path}")

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

print("Testing with image:", img_name)
print("Identified as:", identify_dog(img))
