import os
from PIL import Image, ImageOps
from tqdm import tqdm
import random

# Configuration
source_base = "/Users/mdshayan/Desktop/invasive-species-classifier/data/raw"
target_base = "/Users/mdshayan/Desktop/invasive-species-classifier/data/preprocessed"
species_list = ["rhinella_marina", "vulpes_vulpes"]  # Add more as needed
target_size = (224, 224)
augment_count = 2  # Number of augmentations per image

def resize_and_augment_save(species_name):
    src_dir = os.path.join(source_base, species_name)
    tgt_dir = os.path.join(target_base, species_name)
    os.makedirs(tgt_dir, exist_ok=True)

    image_files = [f for f in os.listdir(src_dir) if f.lower().endswith(".jpg")]

    for file in tqdm(image_files, desc=f"Processing {species_name}"):
        src_path = os.path.join(src_dir, file)
        try:
            img = Image.open(src_path).convert("RGB")
            img = ImageOps.exif_transpose(img)

            # Resize original
            resized = img.resize(target_size)
            tgt_path = os.path.join(tgt_dir, file)
            resized.save(tgt_path, format="JPEG")

            # Augment and save N variations
            for i in range(augment_count):
                aug = resized.copy()

                if random.random() > 0.5:
                    aug = ImageOps.mirror(aug)
                if random.random() > 0.5:
                    aug = ImageOps.flip(aug)
                if random.random() > 0.5:
                    angle = random.choice([15, -15, 30, -30])
                    aug = aug.rotate(angle)

                aug_file = os.path.splitext(file)[0] + f"_aug{i}.jpg"
                aug.save(os.path.join(tgt_dir, aug_file), format="JPEG")

        except Exception as e:
            print(f"Error processing {file}: {e}")

# Run preprocessing for all species
for species in species_list:
    resize_and_augment_save(species)
