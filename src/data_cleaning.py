import os
import cv2
import pandas as pd
from PIL import Image, UnidentifiedImageError
import imagehash
from tqdm import tqdm
import numpy as np
from collections import defaultdict

# Parameters
species_dirs = ["/Users/mdshayan/Desktop/invasive-species-classifier/data/raw/Rhinella_marina", "/Users/mdshayan/Desktop/invasive-species-classifier/data/raw/Vulpes_vulpes"] 
metadata_dir = "/Users/mdshayan/Desktop/invasive-species-classifier/data/metadata"
min_resolution = (224, 224)
valid_ext = ".jpg"
hashes = set()
hash_to_file = defaultdict(list)

def clean_images_for_species(species_name):
    print(f"\nCleaning images for species: {species_name}")
    image_dir = f"data/raw/{species_name}"
    metadata_path = f"{metadata_dir}/{species_name}/metadata.csv"
    
    # Load metadata
    df = pd.read_csv(metadata_path)
    valid_entries = []
    
    for _, row in tqdm(df.iterrows(), total=len(df), desc=f"Processing {species_name}"):
        file_path = os.path.join(image_dir, row["imageFile"])
        
        # Skip if file missing
        if not os.path.exists(file_path):
            continue
        
        try:
            # Open image with Pillow
            with Image.open(file_path) as img:
                # Check resolution
                if img.width < min_resolution[0] or img.height < min_resolution[1]:
                    os.remove(file_path)
                    continue
                
                # Convert to consistent format (.jpg)
                new_path = os.path.splitext(file_path)[0] + valid_ext
                if img.format != 'JPEG':
                    img = img.convert("RGB")
                    img.save(new_path, "JPEG")
                    if new_path != file_path:
                        os.remove(file_path)
                        file_path = new_path
                
                # Detect duplicates using perceptual hash
                img_hash = imagehash.phash(img)
                if img_hash in hashes:
                    os.remove(file_path)
                    continue
                hashes.add(img_hash)
                hash_to_file[img_hash].append(file_path)
                
                # Valid row to keep
                row["imageFile"] = os.path.basename(file_path)
                valid_entries.append(row)
                
        except (UnidentifiedImageError, OSError, cv2.error):
            if os.path.exists(file_path):
                os.remove(file_path)
    
    # Save cleaned metadata
    cleaned_df = pd.DataFrame(valid_entries)
    cleaned_df.to_csv(metadata_path, index=False)
    print(f"Cleaned {species_name}: {len(cleaned_df)} valid entries retained")

# Run cleaning on all species folders
for path in species_dirs:
    species = os.path.basename(path)
    clean_images_for_species(species)
