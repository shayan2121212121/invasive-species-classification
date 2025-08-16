import os
import pandas as pd

# Define species and assign integer labels
species_list = ["rhinella_marina", "vulpes_vulpes", "anas_platyrhynchos"]  # Add more as needed
label_mapping = {name: idx for idx, name in enumerate(sorted(species_list))}

# Directory paths
preprocessed_dir = "/Users/mdshayan/Desktop/invasive-species-classifier/data/preprocessed"
label_output_dir = "/Users/mdshayan/Desktop/invasive-species-classifier/data/metadata_labels"
os.makedirs(label_output_dir, exist_ok=True)

# Combine all species data
all_data = []

for species in species_list:
    species_id = label_mapping[species]
    species_dir = os.path.join(preprocessed_dir, species)
    image_files = [f for f in os.listdir(species_dir) if f.lower().endswith(".jpg")]
    
    for file in image_files:
        all_data.append({
            "imageFile": file,
            "species": species,
            "species_id": species_id
        })

# Create DataFrame and save
df_labels = pd.DataFrame(all_data)
df_labels.to_csv(os.path.join(label_output_dir, "image_labels.csv"), index=False)

# Optional: print mapping
print("Species Label Mapping:")
for name, idx in label_mapping.items():
    print(f"{name} → {idx}")
